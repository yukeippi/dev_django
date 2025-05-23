from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from .models import DiaryEntry, DiaryComment

class DateRangeFilter(admin.SimpleListFilter):
    title = _('作成日')
    parameter_name = 'created_range'

    def lookups(self, request, model_admin):
        return (
            ('today', _('今日')),
            ('yesterday', _('昨日')),
            ('this_week', _('今週')),
            ('last_week', _('先週')),
            ('this_month', _('今月')),
            ('last_month', _('先月')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        elif self.value() == 'yesterday':
            yesterday = now - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday.date())
        elif self.value() == 'this_week':
            start_of_week = now - timedelta(days=now.weekday())
            return queryset.filter(created_at__date__gte=start_of_week.date())
        elif self.value() == 'last_week':
            start_of_last_week = now - timedelta(days=now.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(created_at__date__gte=start_of_last_week.date(), created_at__date__lte=end_of_last_week.date())
        elif self.value() == 'this_month':
            return queryset.filter(created_at__year=now.year, created_at__month=now.month)
        elif self.value() == 'last_month':
            if now.month == 1:
                last_month = 12
                last_month_year = now.year - 1
            else:
                last_month = now.month - 1
                last_month_year = now.year
            return queryset.filter(created_at__year=last_month_year, created_at__month=last_month)

def make_published(modeladmin, request, queryset):
    queryset.update(updated_at=timezone.now())
make_published.short_description = "選択した日記を更新済みとしてマーク"

class AssignToUserAction:
    def __init__(self, user):
        self.user = user
        self.name = f'assign_to_{user.username}'
        self.short_description = f'選択した日記を {user.username} に割り当て'
        
    def __call__(self, modeladmin, request, queryset):
        queryset.update(author=self.user)

class DiaryCommentInline(admin.TabularInline):
    model = DiaryComment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author' and not request.user.is_superuser:
            kwargs['initial'] = request.user
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DiaryEntryAdmin(admin.ModelAdmin):
    actions = [make_published]
    inlines = [DiaryCommentInline]
    list_display = ('title', 'short_content', 'author', 'created_at', 'updated_at', 'days_since_creation')
    list_filter = (DateRangeFilter, 'author', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'author')
        }),
        ('内容', {
            'fields': ('content',)
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '内容（抜粋）'
    
    def days_since_creation(self, obj):
        delta = timezone.now().date() - obj.created_at.date()
        return f'{delta.days}日'
    days_since_creation.short_description = '作成からの日数'
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # スーパーユーザーのみが利用可能な機能
        if request.user.is_superuser:
            # システム内の全ユーザーを取得（最大5人まで）
            users = User.objects.all()[:5]
            
            # ユーザーごとにアクションを作成
            for user in users:
                action = AssignToUserAction(user)
                actions[action.name] = (action, action.name, action.short_description)
                
        return actions

class DiaryCommentAdmin(admin.ModelAdmin):
    list_display = ('diary', 'author', 'short_content', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('content',)
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '内容（抜粋）'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(DiaryEntry, DiaryEntryAdmin)
admin.site.register(DiaryComment, DiaryCommentAdmin)

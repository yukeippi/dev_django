from django.core.validators import BaseValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MinLengthExclusiveValidator(BaseValidator):
    """指定した文字数より多いことを検証するバリデーター（指定値は含まない）"""
    message = '%(limit_value)d文字以上で入力してください。'
    code = 'min_length_exclusive'

    def compare(self, a, b):
        return a <= b

    def clean(self, x):
        return len(x) if x else 0


@deconstructible
class MaxLengthExclusiveValidator(BaseValidator):
    """指定した文字数未満であることを検証するバリデーター（指定値は含まない）"""
    message = '%(limit_value)d文字未満で入力してください。'
    code = 'max_length_exclusive'

    def compare(self, a, b):
        return a >= b

    def clean(self, x):
        return len(x) if x else 0


@deconstructible
class LengthRangeValidator:
    """文字数の範囲を検証するバリデーター"""
    def __init__(self, min_length=None, max_length=None, min_message=None, max_message=None):
        self.min_length = min_length
        self.max_length = max_length
        self.min_message = min_message or f'{min_length}文字以上で入力してください。'
        self.max_message = max_message or f'{max_length}文字以下で入力してください。'

    def __call__(self, value):
        if not value:
            return
        
        length = len(value)
        
        if self.min_length is not None and length < self.min_length:
            raise ValidationError(self.min_message, code='min_length')
        
        if self.max_length is not None and length > self.max_length:
            raise ValidationError(self.max_message, code='max_length')

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.min_length == other.min_length and
            self.max_length == other.max_length and
            self.min_message == other.min_message and
            self.max_message == other.max_message
        )

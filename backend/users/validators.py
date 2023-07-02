import re

from django.core.exceptions import ValidationError


def validate_user_name(value):
    value = value.lower()
    reg = re.compile(r'^[\w.@+-]+\Z')
    if not reg.match(value):
        raise ValidationError(
            u'%s Не заполнено обязательное поле или оно заполнено некорректно!'
        )
    if value == 'me':
        raise ValidationError(
            'Нельзя использовать это имя, выберите другое'
        )
    return value

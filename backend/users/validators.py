import re

from django.core.exceptions import ValidationError


def validate_user_name(value):
    reg = re.compile(r'^[\w.@+-]+\Z')
    if not reg.match(value):
        raise ValidationError(
            u'%s Не заполнено обязательное поле или оно заполнено некорректно'
        )
    if value.lower() == 'me':
        raise ValidationError(
            'Нельзя использовать это имя, выберите другое'
        )

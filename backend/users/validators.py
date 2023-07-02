import re

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


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
    if User.objects.filter(username=value).exists():
        raise ValidationError("Такое имя уже зарегистрировано")
    return value

import re
from rest_framework.serializers import ValidationError


def validate_youtube_link(value):
    """
    Валидатор, проверяющий, что ссылка ведет на youtube.com или youtu.be.
    """
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    )

    # Проверяем, соответствует ли значение регулярному выражению
    if not re.match(youtube_regex, value):
        raise ValidationError('Ссылка должна вести на youtube.com или youtu.be')

    return value
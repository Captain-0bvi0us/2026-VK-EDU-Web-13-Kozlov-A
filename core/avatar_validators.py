from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# Требования ДЗ5: ограничение расширений и размера (ошибки на бэкенде)
AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_EXTENSIONS = ("jpg", "jpeg", "png")

avatar_extension_validator = FileExtensionValidator(
    allowed_extensions=list(AVATAR_EXTENSIONS),
    message=(
        "Разрешены только файлы JPEG и PNG "
        "(расширения: %(allowed_extensions)s)."
    ),
)


def validate_avatar_max_size(uploaded_file):
    if uploaded_file.size > AVATAR_MAX_BYTES:
        mb = AVATAR_MAX_BYTES // (1024 * 1024)
        raise ValidationError(
            f"Размер файла не должен превышать {mb} МБ.",
        )


def validate_avatar_upload(uploaded_file):
    avatar_extension_validator(uploaded_file)
    validate_avatar_max_size(uploaded_file)

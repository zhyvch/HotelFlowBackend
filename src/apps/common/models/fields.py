from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from src.apps.common import validators

from django.conf import settings

class PhoneNumberField(CharField):
    default_validators = [validators.validate_phone_number]

    @property
    def description(self):
        return _('Phone number (E.164 format)') if settings.USE_E164 else _('Phone number')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 15)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

from django.conf import settings

import phonenumbers


@deconstructible
class PhoneNumberValidator:
    message = _('Enter a valid phone number.')
    code = 'invalid'
    country_codes_pattern = '|'.join(map(str, phonenumbers.COUNTRY_CODE_TO_REGION_CODE.keys()))
    E164_format_regex = _lazy_re_compile(
        rf'^\+({country_codes_pattern})\d{{4,14}}$'
    )
    basic_format_regex = _lazy_re_compile(
        r'^\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
    )
    allowlist_regex = _lazy_re_compile(
        '|'.join(settings.PHONE_NUMBER_ACCESS_CONTROL.get('allowlist'))
    )
    denylist_regex = _lazy_re_compile(
        '|'.join(settings.PHONE_NUMBER_ACCESS_CONTROL.get('denylist'))
    )

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        error = ValidationError(self.message, code=self.code, params={'value': value})

        if settings.USE_E164:
            if not value or value[0] != '+' or len(value) > 15:
                raise error

            if not self.E164_format_regex.match(value):
                raise error

            if not self.validate_access_control(value):
                raise error

            try:
                number_obj: phonenumbers.PhoneNumber = phonenumbers.parse(value, keep_raw_input=True)
            except phonenumbers.NumberParseException:
                raise error

            if settings.TRUNCATE_TOO_LONG_PHONE_NUMBERS:
                phonenumbers.truncate_too_long_number(number_obj)

            if not phonenumbers.is_valid_number(number_obj):
                raise error
        else:
            if not value or len(value) > 100:
                raise error

            if not self.basic_format_regex.match(value):
                raise error

            if not self.validate_access_control(value):
                raise error

    def validate_access_control(self, value):
        return self.allowlist_regex.match(value) and not self.denylist_regex.match(value)



    def __eq__(self, other):
        return (
            isinstance(other, PhoneNumberValidator)
            and (self.message == other.message)
            and (self.code == other.code)
        )


validate_phone_number = PhoneNumberValidator()

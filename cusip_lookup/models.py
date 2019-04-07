import logging
import re

from django.core.validators import RegexValidator
from django.db import models

from kmcdermott_ej.settings import LOG_FILE, LOG_FORMAT


logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=logging.DEBUG)


STRICT_CUSIP_REGEX = r'^[0-9A-Z]{9}$'
strict_cusip_pattern = re.compile(STRICT_CUSIP_REGEX)
strict_cusip_validator = RegexValidator(STRICT_CUSIP_REGEX, 'invalid CUSIP')


class MuniBond(models.Model):
    # TODO: discuss expectations for uniqueness and add constraints as needed

    # fields corresponding to OpenFIGI fields
    name = models.CharField(max_length=100, blank=True)
    ticker = models.CharField(max_length=100, blank=True)
    market_sector = models.CharField(max_length=100, blank=True)
    exchange_code = models.CharField(max_length=100, blank=True)
    security_type_1 = models.CharField(max_length=100, blank=True)
    security_type_2 = models.CharField(max_length=100, blank=True)

    # fields not returned by OpenFIGI
    updated = models.DateTimeField(auto_now=True)
    cusip = models.CharField(max_length=9, validators=[strict_cusip_validator])

    @staticmethod
    def clean_cusip(cusip):
        """
        Normalize a CUSIP that may have been entered with hyphens, etc.
        """
        cusip = (cusip or "").strip().upper().replace("-", "")

        return cusip if strict_cusip_pattern.match(cusip) else None

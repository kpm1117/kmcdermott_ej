"""
Mutable mappings should be accessed via function calls.
"""
from collections import OrderedDict


def map_openfigi_to_munibond_fields():
    return OrderedDict((
        ("name", "name"),
        ("ticker", "ticker"),
        ("marketSector", "market_sector"),
        ("exchCode", "exchange_code"),
        ("securityType", "security_type_1"),
        ("securityType2", "security_type_2"),
    ))

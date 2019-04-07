from kmcdermott_ej import settings  # TODO: update __init__

SQLITE_FILE = '/home/kevin/development/python-projects/kmcdermott_ej/db.sqlite3'

OPEN_FIGI_API_URL = "https://api.openfigi.com/v2/mapping"

# Limits pertaining to non-authenticated users
MAX_CUSIPS_PER_EXTERNAL_REQUEST = 5
MAX_CUSIPS_PER_MINUTE = 25
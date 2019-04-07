import json
import logging
import pandas as pd
import requests

from kmcdermott_ej.settings import LOG_FILE, LOG_FORMAT
from .constants import OPEN_FIGI_API_URL, MAX_CUSIPS_PER_EXTERNAL_REQUEST
from .mappings import map_openfigi_to_munibond_fields
from .models import MuniBond
from .utils import deduplicate_list


logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=logging.DEBUG)

BAD_RESPONSE = "bad response"
SIZE_MISMATCH = "size of result does not match request"
MUNI_BOND_INDICATORS = {
    "security_type_2": ["Muni"]
}


class CusipLookupExtractError(Exception):
    pass


class CusipLookupTransformError(Exception):
    pass


class CusipLookupLoadError(Exception):
    pass


class CusipLookupEtl:
    def __init__(self, preformatted_cusips):
        self.cusips = deduplicate_list(preformatted_cusips)
        self.cusip_count = len(self.cusips)
        self.muni_df = pd.DataFrame(columns=["data", "error"])
        self.error_df = pd.DataFrame(columns=["cusip", "error"])
        self.etl_error = None  # for sub-exception anomalies

        try:
            self._extract()
        except Exception as e:
            msg = str(e)
            logging.debug(msg)
            raise CusipLookupExtractError(msg)

        try:
            self._transform()
        except Exception as e:
            msg = str(e)
            logging.debug(msg)
            raise CusipLookupTransformError(msg)

        try:
            self._load()
        except Exception as e:
            msg = str(e)
            logging.debug(msg)
            raise CusipLookupLoadError(msg)

    def _extract(self):
        for i in range(0, self.cusip_count, MAX_CUSIPS_PER_EXTERNAL_REQUEST):
            batch = self.cusips[i: i + MAX_CUSIPS_PER_EXTERNAL_REQUEST]
            self._extract_batch(batch)

    def _extract_batch(self, cusip_batch):
        """
        Return OpenFIGI API results per CUSIP
        """
        data = json.dumps(
            [{"idType": "ID_CUSIP", "idValue": c} for c in cusip_batch]
        )
        headers = {"Content-Type": "application/json"}

        response = requests.post(OPEN_FIGI_API_URL, data=data, headers=headers)

        if not response.ok:
            msg = "{}: {}".format(BAD_RESPONSE, {
                key: getattr(response, key)
                for key in ("status_code", "url")
            })
            raise Exception(
                "{}; data={}; see log".format(msg, data)
            )

        batch_df = pd.read_json(response.text)

        req_size, res_size = len(cusip_batch), len(batch_df)
        if req_size != res_size:
            msg = "{}: CUSIPS={}".format(SIZE_MISMATCH, cusip_batch)
            raise Exception("{}; see log".format(msg))

        self.muni_df = self.muni_df.append(batch_df, sort=False)

    def _transform(self):
        if not len(self.muni_df):
            # Bail quickly if no processing needed
            return

        self.muni_df["cusip"] = self.cusips
        self.error_df = self.muni_df[["cusip", "error"]] \
            .loc[pd.notna(self.muni_df["error"])]

        # Remove rows with no data, group by cusip, and unpack the data
        # from each row into one or more rows. Append an empty df with the
        # expected columns (to ensure they exist). Select the relevant rows
        # and columns and strip whitespace.
        field_mapping = map_openfigi_to_munibond_fields()
        df_cols = ["cusip"] + list(field_mapping.values())
        self.muni_df = self.muni_df \
            .dropna(subset=["data"]) \
            .groupby("cusip") \
            .apply(lambda x: pd.DataFrame(x['data'].iloc[0])) \
            .reset_index() \
            .rename(field_mapping, axis=1) \
            .append(pd.DataFrame(columns=df_cols)) \
            .filter(df_cols) \
            .astype({k: str for k in df_cols}) \
            .fillna("") \
            .apply(lambda x: x.str.strip())

        def is_muni(x):
            for field, values in MUNI_BOND_INDICATORS.items():
                if x[field] in values:
                    return True
            return False

        # Identify rows representing muni bonds. Drop the rest.
        self.muni_df = self.muni_df[self.muni_df.apply(is_muni, axis=1)]

    def _load(self):
        # TODO: maybe use SQLAlchemy and generete sql for a bulk upsert
        # (would need to add the timestamp to muni_df)
        if not len(self.muni_df):
            return pd.DataFrame()

        for index, row in self.muni_df.iterrows():
            MuniBond.objects.get_or_create(**row.to_dict())

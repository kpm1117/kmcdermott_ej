import logging
import re

from django import forms

from kmcdermott_ej.settings import LOG_FILE, LOG_FORMAT
from .models import MuniBond


logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=logging.DEBUG)


class CusipForm(forms.Form):
    """
    TODO: Allow for file-based input.
    """
    CUSIPS_PER_FORM = 25
    PROMPT = "Enter up to {} CUSIPS".format(CUSIPS_PER_FORM)
    NOTE = "Separated by newline/space/comma/pipe/semi"
    SEPARATORS = " ,|;\t\n"
    SEP = " "
    INVALID_CUSIP = "invalid CUSIP: '{}' (should be 9 alphanumeric chars)"

    cusips = forms.CharField(
        widget=forms.Textarea,
        max_length=300,
    )

    def __init__(self, *args, **kwargs):
        """
        Define two additional instance variables:

            processed_results: a dictionary that will map each CUSIP to a list
            of results
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.processed_results = []

    def clean_cusips(self):
        """
        Parse and normalize individual CUSIPs using the MuniBond model.
        """
        data = self.cleaned_data["cusips"]

        sub_pattern = re.compile("[{}]+".format(self.SEPARATORS))
        data = sub_pattern.sub(self.SEP, data).strip().split(self.SEP)

        for i, raw_cusip in enumerate(data):
            clean_cusip = MuniBond.clean_cusip(raw_cusip)
            if not clean_cusip:
                raise forms.ValidationError(
                    self.INVALID_CUSIP.format(raw_cusip)
                )

            data[i] = clean_cusip

        return data

from django.views import generic
import datetime

from.cusip_lookup_etl import CusipLookupEtl
from .forms import CusipForm
from django.shortcuts import render, render_to_response


class IndexView(generic.FormView):
    template_name = 'cusip_lookup.html'
    form_class = CusipForm
    success_url = "/cusip"

    def form_valid(self, form):
        cusips = form.cleaned_data["cusips"]
        render_data = self.get_context_data()
        etl = CusipLookupEtl(cusips)
        timestamp = "{} UTC".format(datetime.datetime.utcnow())
        render_data.update({'show_errors': len(etl.error_df)>0,
                            'found_munis': len(etl.muni_df)>0,
                            'error_table': etl.error_df.to_html(index=False),
                            'muni_table': etl.muni_df.to_html(index=False),
                            'timestamp': timestamp,
                            })
        return render(self.request, self.template_name, render_data)


        # except Exception as e:
        #     # TODO: use http status codes to convey this
        #     form.error = e
        #     return HttpResponseServerError(e)

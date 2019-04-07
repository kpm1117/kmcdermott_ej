from django.contrib import admin

from .models import MuniBond


class MuniBondAdmin(admin.ModelAdmin):
    readonly_fields = ('updated',)


admin.site.register(MuniBond, MuniBondAdmin)

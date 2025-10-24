from django.contrib import admin
from main.models import Language, Translation, MaterialsStatus, HelpRequest
# Register your models here.

admin.site.register(Language)
admin.site.register(MaterialsStatus)
admin.site.register(HelpRequest)

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'language', 'value')
    list_filter = ('language',)
    search_fields = ('key', 'value')
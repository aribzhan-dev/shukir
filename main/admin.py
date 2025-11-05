from django.contrib import admin
from django.db.models import Count
from main.models import (
    Language, Translation, MaterialsStatus,
    HelpRequest, HelpCategory, HelpRequestFile
)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "status")
    list_filter = ("status",)
    search_fields = ("title", "code")


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "status")
    list_filter = ("status",)
    search_fields = ("title",)


@admin.register(MaterialsStatus)
class MaterialsStatusAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "status")
    list_filter = ("language", "status")
    search_fields = ("title",)


# 🟢 ASOSIY QISM: Yordam so‘rovlari uchun admin panel
@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "surname",
        "phone_number",
        "help_category",
        "received_other_help_display",
        "status",
    )
    list_filter = (
        "help_category",
        "received_other_help",
        "status",
    )
    search_fields = ("name", "surname", "iin", "phone_number", "address")
    list_per_page = 30
    ordering = ("-id",)


    def received_other_help_display(self, obj):
        return "Да" if obj.received_other_help else "Нет"
    received_other_help_display.short_description = "Получал помощь ранее"


    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_requests = HelpRequest.objects.count()
        total_received_help = HelpRequest.objects.filter(received_other_help=True).count()
        total_not_received_help = total_requests - total_received_help

        extra_context["summary"] = {
            "total": total_requests,
            "received": total_received_help,
            "not_received": total_not_received_help,
        }
        return super().changelist_view(request, extra_context=extra_context)



    change_list_template = "admin/help_request_changelist.html"


@admin.register(HelpRequestFile)
class HelpRequestFileAdmin(admin.ModelAdmin):
    list_display = ("help_request", "file")
    search_fields = ("help_request__name", "help_request__surname")


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("key", "language", "value")
    list_filter = ("language",)
    search_fields = ("key", "value")
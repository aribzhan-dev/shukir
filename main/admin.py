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


# 🟢 ASOSIY QISM
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
    change_list_template = "admin/help_request_changelist.html"

    def received_other_help_display(self, obj):
        return "Да" if obj.received_other_help else "Нет"
    received_other_help_display.short_description = "Получал помощь ранее"

    def changelist_view(self, request, extra_context=None):
        """
        Bu funksiya yordamida admin panelda statistik ma’lumotlarni
        real va filtrlangan holatda ko‘rsatamiz.
        """
        extra_context = extra_context or {}

        # 🔹 Hozirgi filterga qarab querysetni olamiz
        queryset = self.get_queryset(request)

        # 🔹 Umumiy statistika
        total_requests = queryset.count()
        total_received_help = queryset.filter(received_other_help=True).count()
        total_not_received_help = queryset.filter(received_other_help=False).count()

        # 🔹 Toifa bo‘yicha statistikalar
        category_stats = (
            queryset.values("help_category__title")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        extra_context["summary"] = {
            "total": total_requests,
            "received": total_received_help,
            "not_received": total_not_received_help,
            "categories": category_stats,
        }

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(HelpRequestFile)
class HelpRequestFileAdmin(admin.ModelAdmin):
    list_display = ("help_request", "file")
    search_fields = ("help_request__name", "help_request__surname")


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("key", "language", "value")
    list_filter = ("language",)
    search_fields = ("key", "value")
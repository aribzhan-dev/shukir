from django.contrib import admin
from django.db.models import Count
from main.models import (
    Language, Translation, MaterialsStatus,
    HelpRequest, HelpCategory, HelpRequestFile
)
from django.utils.html import format_html


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


from django.db.models import Count
from django.utils.html import format_html


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
        "whatsapp_link",
    )
    list_filter = ("help_category", "received_other_help", "status")
    search_fields = ("name", "surname", "iin", "phone_number", "address")
    list_per_page = 30
    ordering = ("-id",)
    change_list_template = "admin/help_request_changelist.html"

    def received_other_help_display(self, obj):
        return "Да" if obj.received_other_help else "Нет"

    received_other_help_display.short_description = "Получал помощь ранее"

    def whatsapp_link(self, obj):
        if not obj.phone_number:
            return "—"
        phone = (
            str(obj.phone_number)
            .replace("+", "")
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        wa_url = f"https://wa.me/{phone}"
        return format_html(
            '<a href="{}" target="_blank" '
            'style="background-color:#28a745;color:white;'
            'padding:3px 10px;border-radius:6px;'
            'text-decoration:none;font-weight:bold;">WhatsApp</a>',
            wa_url,
        )

    whatsapp_link.short_description = "Связаться в WhatsApp"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)

        total_requests = queryset.count()
        total_received_help = queryset.filter(received_other_help=True).count()
        total_not_received_help = queryset.filter(received_other_help=False).count()

        merged = {}
        all_cats = HelpCategory.objects.all()

        for uz_cat in all_cats.filter(language__code="uz"):
            related_ids = list(all_cats.filter(group_key=uz_cat.group_key).values_list("id", flat=True))
            count = queryset.filter(help_category_id__in=related_ids).count()
            if count > 0:
                merged[uz_cat.title] = count

        no_cat_count = queryset.filter(help_category__isnull=True).count()
        if no_cat_count > 0:
            merged["Без категории"] = no_cat_count

        merged_categories = [
            {"title": title, "total": total}
            for title, total in sorted(merged.items(), key=lambda x: -x[1])
        ]

        extra_context["summary"] = {
            "total": total_requests,
            "received": total_received_help,
            "not_received": total_not_received_help,
            "categories": merged_categories,
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

from django.contrib import admin
from django.db.models import Count, OuterRef, Exists
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter
from .models import (
    Language, Translation, MaterialsStatus,
    HelpRequest, HelpCategory, HelpRequestFile,
    Employee, Archive
)


# ================================
# 1. LANGUAGE
# ================================
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "status")
    list_filter = ("status",)
    search_fields = ("title", "code")

    class Meta:
        verbose_name = "Язык"
        verbose_name_plural = "Языки"


# ================================
# 2. HELP CATEGORY
# ================================
@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "status")
    list_filter = ("status",)
    search_fields = ("title",)

    class Meta:
        verbose_name = "Категория помощи"
        verbose_name_plural = "Категории помощи"


# ================================
# 3. MATERIALS STATUS
# ================================
@admin.register(MaterialsStatus)
class MaterialsStatusAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "status")
    list_filter = ("language", "status")
    search_fields = ("title",)

    class Meta:
        verbose_name = "Статус материала"
        verbose_name_plural = "Статусы материалов"


# ================================
# 4. UZBEK CATEGORY FILTER
# ================================
class UzbekCategoryFilter(admin.SimpleListFilter):
    title = "Категория помощи"
    parameter_name = "help_category_group"

    def lookups(self, request, model_admin):
        lookups = []
        uz_cats = HelpCategory.objects.filter(language__code="uz").order_by("title")
        for cat in uz_cats:
            key = cat.group_key or f"id_{cat.id}"
            lookups.append((key, cat.title))
        lookups.append(("no_category", "Без категории"))
        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        if value == "no_category":
            return queryset.filter(help_category__isnull=True)
        if value.startswith("id_"):
            cat_id = int(value.split("_")[1])
            return queryset.filter(help_category_id=cat_id)
        related_ids = HelpCategory.objects.filter(group_key=value).values_list("id", flat=True)
        return queryset.filter(help_category_id__in=related_ids)


# ================================
# 5. HELP REQUEST FILE INLINE
# ================================
class HelpRequestFileInline(admin.TabularInline):
    model = HelpRequestFile
    extra = 0
    fields = ("file", "view_file")
    readonly_fields = ("view_file",)

    def view_file(self, obj):
        if not obj.pk or not obj.file:
            return "—"
        return format_html(
            '<a href="{}" target="_blank" style="'
            'background:#28a745;color:white;padding:6px 12px;border-radius:8px;'
            'text-decoration:none;font-weight:600;font-size:13px;display:inline-block;'
            '">Смотреть файл</a>',
            obj.file.url
        )
    view_file.short_description = "Файл"


# ================================
# 6. HELP REQUEST
# ================================
@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "surname", "phone_number",
        "help_category_display", "received_other_help_display",
        "status", "whatsapp_link"
    )
    list_filter = (UzbekCategoryFilter, "received_other_help", "status")
    search_fields = ("name", "surname", "iin", "phone_number", "address")
    list_per_page = 30
    ordering = ("-id",)
    change_list_template = "admin/help_request_changelist.html"
    inlines = [HelpRequestFileInline]

    class Meta:
        verbose_name = "Заявка на помощь"
        verbose_name_plural = "Заявки на помощь"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        archived = Archive.objects.filter(help_request=OuterRef("pk"))
        return qs.annotate(is_archived=Exists(archived)).filter(is_archived=False)

    def help_category_display(self, obj):
        if not obj.help_category:
            return "—"
        if obj.help_category.group_key:
            uz_cat = HelpCategory.objects.filter(
                group_key=obj.help_category.group_key, language__code="uz"
            ).first()
            if uz_cat:
                return uz_cat.title
        return obj.help_category.title
    help_category_display.short_description = "Категория помощи"

    def received_other_help_display(self, obj):
        return "Да" if obj.received_other_help else "Нет"
    received_other_help_display.short_description = "Получал помощь ранее"

    def whatsapp_link(self, obj):
        if not obj.phone_number:
            return "—"
        phone = "".join(filter(str.isdigit, str(obj.phone_number)))
        wa_url = f"https://wa.me/{phone}"
        return format_html(
            '<a href="{}" target="_blank" '
            'style="background:#25d366;color:white;padding:4px 10px;border-radius:6px;'
            'text-decoration:none;font-weight:600;font-size:12px;">WhatsApp</a>',
            wa_url
        )
    whatsapp_link.short_description = "Связаться в WhatsApp"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)

        total_requests = queryset.count()
        total_received = queryset.filter(received_other_help=True).count()
        total_not_received = queryset.filter(received_other_help=False).count()

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
            "received": total_received,
            "not_received": total_not_received,
            "categories": merged_categories,
        }
        return super().changelist_view(request, extra_context=extra_context)


# ================================
# 7. HELP REQUEST FILE
# ================================
@admin.register(HelpRequestFile)
class HelpRequestFileAdmin(admin.ModelAdmin):
    list_display = ("help_request", "file")
    search_fields = ("help_request__name", "help_request__surname")

    class Meta:
        verbose_name = "Файл заявки"
        verbose_name_plural = "Файлы заявок"


# ================================
# 8. TRANSLATION
# ================================
@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("key", "language", "value")
    list_filter = ("language",)
    search_fields = ("key", "value")

    class Meta:
        verbose_name = "Перевод"
        verbose_name_plural = "Переводы"


# ================================
# 9. EMPLOYEE
# ================================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "status_display")
    search_fields = ("first_name", "last_name")
    list_filter = ("status",)
    ordering = ("-id",)
    list_per_page = 30

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def status_display(self, obj):
        return "Активен" if obj.status == 0 else "Неактивен"
    status_display.short_description = "Статус"


# ================================
# 10. ARCHIVE
# ================================
@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ("id", "help_category_display", "money", "created_at", "status_display")
    list_filter = (('created_at', DateRangeFilter),)
    search_fields = (
        "help_request__name", "help_request__surname",
        "employee__first_name", "employee__last_name",
        "help_category__title"
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 30

    class Meta:
        verbose_name = "Архив помощи"
        verbose_name_plural = "Архив помощи"

    def help_category_display(self, obj):
        if not obj.help_category:
            return "—"
        if obj.help_category.group_key:
            uz_cat = HelpCategory.objects.filter(
                group_key=obj.help_category.group_key, language__code="uz"
            ).first()
            if uz_cat:
                return uz_cat.title
        return obj.help_category.title
    help_category_display.short_description = "Категория помощи"

    def status_display(self, obj):
        statuses = {0: "Новая", 1: "Одобрена", 2: "Отклонена"}
        return statuses.get(obj.status, "Неизвестно")
    status_display.short_description = "Статус"
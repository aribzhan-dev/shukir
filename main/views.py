from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import HelpRequest, Language, MaterialsStatus, Translation, HelpCategory, HelpRequestFile
import requests
import os
import mimetypes
import re

TELEGRAM_BOT_TOKEN = "8240282392:AAGtvnPfS3A0R6KQFydGXtBy1vuJ6VUuu9M"
TELEGRAM_CHAT_ID = "-1003120018187"


def get_translations(lang_code):
    language = Language.objects.filter(code=lang_code, status=0).first()
    translations = {}
    if language:
        for tr in Translation.objects.filter(language=language, status=0):
            translations[tr.key] = tr.value
    return translations


def _clean_phone_for_wa(phone_str: str) -> str:
    digits = re.sub(r"\D", "", str(phone_str or ""))

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return digits


@csrf_exempt
def index_handler(request, lang_code="uz"):

    languages = Language.objects.filter(status=0)
    language = Language.objects.filter(code=lang_code).first() or Language.objects.filter(code="uz").first()
    translations = get_translations(lang_code)
    statuses = MaterialsStatus.objects.filter(language=language, status=0)
    categories = HelpCategory.objects.filter(status=0, language__code=lang_code)

    if request.method == "POST":

        name = request.POST.get("name")
        surname = request.POST.get("surname")
        age = request.POST.get("age")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        status_id = request.POST.get("material_status")
        category_id = request.POST.get("help_category")
        other_category = request.POST.get("other_category")
        child_count = request.POST.get("child_in_fam")
        address = request.POST.get("address")
        iin = request.POST.get("iin")
        reason = request.POST.get("why_need_help")
        received_help = request.POST.get("received_other_help") == "yes"
        files = request.FILES.getlist("file")

        material_status = MaterialsStatus.objects.filter(id=status_id).first()
        help_category = HelpCategory.objects.filter(id=category_id).first()

        help_request = HelpRequest.objects.create(
            name=name,
            surname=surname,
            age=int(age or 0),
            email=email,
            phone_number=phone,
            material_status=material_status,
            help_category=help_category,
            other_category=other_category,
            child_in_fam=int(child_count or 0),
            address=address,
            iin=iin,
            why_need_help=reason,
            received_other_help=received_help,
            status=0,
        )


        for f in files:
            HelpRequestFile.objects.create(help_request=help_request, file=f)


        category_text = help_category.title if help_category else "-"
        if help_category and getattr(help_category, "is_other", False) and other_category:
            category_text += f" ({other_category})"

        status_text = material_status.title if material_status else "-"

        wa_digits = _clean_phone_for_wa(help_request.phone_number)
        wa_link = f"https://wa.me/{wa_digits}" if wa_digits else None
        phone_html = f'<a href="{wa_link}">{help_request.phone_number}</a>' if wa_link else f"{help_request.phone_number}"

        req_tag = f"HR-{help_request.id}"


        text_labels = {
            "uz": {
                "new_request": "🟢 Янги ёрдам сўрови келди",
                "age": "Ёши",
                "family": "Оилавий ҳолати",
                "children": "Фарзандлар сони",
                "address": "Манзил",
                "iin": "ИИН",
                "category": "Тоифа",
                "received": "Илгари ёрдам олганми",
                "reason": "Сабаб",
                "yes": "Ҳа",
                "no": "Йўқ",
            },
            "ru": {
                "new_request": "🟢 Поступила новая заявка на помощь",
                "age": "Возраст",
                "family": "Семейное положение",
                "children": "Количество детей",
                "address": "Адрес",
                "iin": "ИИН",
                "category": "Категория",
                "received": "Получал ли помощь ранее",
                "reason": "Причина",
                "yes": "Да",
                "no": "Нет",
            },
            "kk": {
                "new_request": "🟢 Жаңа көмек сұрауы түсті",
                "age": "Жасы",
                "family": "Отбасылық жағдайы",
                "children": "Балалар саны",
                "address": "Мекенжай",
                "iin": "ЖСН",
                "category": "Санат",
                "received": "Бұрын көмек алған ба",
                "reason": "Себебі",
                "yes": "Иә",
                "no": "Жоқ",
            },
        }

        lbl = text_labels.get(lang_code, text_labels["uz"])


        message = (
            f"{lbl['new_request']} {req_tag}:\n\n"
            f"👤 {help_request.name} {help_request.surname}\n"
            f"📞 Телефон: {phone_html}\n"
            f"📅 {lbl['age']}: {help_request.age}\n"
            f"🏠 {lbl['family']}: {status_text}\n"
            f"👶 {lbl['children']}: {help_request.child_in_fam}\n"
            f"🏡 {lbl['address']}: {help_request.address}\n"
            f"🆔 {lbl['iin']}: {help_request.iin}\n"
            f"📂 {lbl['category']}: {category_text}\n"
            f"📦 {lbl['received']}: {lbl['yes'] if help_request.received_other_help else lbl['no']}\n"
            f"💬 {lbl['reason']}: {help_request.why_need_help}"
        )


        send_to_telegram(text=message, parse_mode="HTML")


        files_qs = list(help_request.files.all())
        total = len(files_qs)
        for idx, f in enumerate(files_qs, start=1):
            try:
                file_path = f.file.path
                caption = f"{req_tag} • Файл {idx}/{total} — {help_request.name} {help_request.surname}"
                send_to_telegram(file_path=file_path, caption=caption, send_text_also=False)
            except Exception as e:
                print(f"⚠️ Fayl yuborishda xatolik: {e}")

        return redirect(f"/{lang_code}/success/")

    context = {
        "lang_code": lang_code,
        "statuses": statuses,
        "tr": translations,
        "languages": languages,
        "categories": categories,
    }
    return render(request, "index.html", context)


def send_to_telegram(text=None, file_path=None, send_text_also=True, caption=None, parse_mode="HTML"):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    try:

        if text and send_text_also:
            requests.post(
                f"{base_url}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )


        if file_path and os.path.exists(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            file_type = "document"
            if mime_type:
                if mime_type.startswith("image/"):
                    file_type = "photo"
                elif mime_type.startswith("video/"):
                    file_type = "video"

            endpoint = {"photo": "sendPhoto", "video": "sendVideo", "document": "sendDocument"}[file_type]

            with open(file_path, "rb") as f:
                files = {file_type: f}
                data = {"chat_id": TELEGRAM_CHAT_ID}
                if caption:
                    data["caption"] = caption
                    data["parse_mode"] = "HTML"
                resp = requests.post(f"{base_url}/{endpoint}", data=data, files=files, timeout=60)
                resp.raise_for_status()
                print(f"📎 Fayl yuborildi: {os.path.basename(file_path)} — {resp.status_code}")

    except requests.exceptions.Timeout:
        print("⏳ Telegram жавоб бермади (timeout).")
    except requests.exceptions.ConnectionError:
        print("⚠️ Интернет ёки Telegram API блокланган.")
    except Exception as e:
        print(f"❌ Telegram xatolik: {e}")


def success_page(request, lang_code="uz"):
    translations = get_translations(lang_code)
    return render(request, "success.html", {"lang_code": lang_code, "tr": translations})
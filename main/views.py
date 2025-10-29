from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import HelpRequest, Language, MaterialsStatus, Translation, HelpCategory
import requests
import os
import mimetypes

TELEGRAM_BOT_TOKEN = "8240282392:AAGtvnPfS3A0R6KQFydGXtBy1vuJ6VUuu9M"
TELEGRAM_CHAT_ID = "-1003120018187"


def get_translations(lang_code):
    language = Language.objects.filter(code=lang_code, status=0).first()
    translations = {}
    if language:
        qs = Translation.objects.filter(language=language, status=0)
        for tr in qs:
            translations[tr.key] = tr.value
    return translations


@csrf_exempt
def index_handler(request, lang_code="uz"):
    languages = Language.objects.filter(status=0)
    language = Language.objects.filter(code=lang_code).first()
    if not language:
        language = Language.objects.filter(code="uz").first()

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
        file = request.FILES.get("file")

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
            file=file,
            status=0,
        )


        category_text = help_category.title
        if help_category.is_other and other_category:
            category_text += f" ({other_category})"

        if lang_code == "ru":
            message = (
                f"🟢 Поступила новая заявка на помощь:\n\n"
                f"👤 {help_request.name} {help_request.surname}\n"
                f"📞 Телефон: {help_request.phone_number}\n"
                f"📅 Возраст: {help_request.age}\n"
                f"👶 Количество детей: {help_request.child_in_fam}\n"
                f"🏡 Адрес: {help_request.address}\n"
                f"🆔 ИИН: {help_request.iin}\n"
                f"📂 Категория: {category_text}\n"
                f"💬 Причина: {help_request.why_need_help}"
            )
        elif lang_code == "kk":
            message = (
                f"🟢 Жаңа көмек сұрауы түсті:\n\n"
                f"👤 {help_request.name} {help_request.surname}\n"
                f"📞 Телефон: {help_request.phone_number}\n"
                f"📅 Жасы: {help_request.age}\n"
                f"👶 Балалар саны: {help_request.child_in_fam}\n"
                f"🏡 Мекенжай: {help_request.address}\n"
                f"🆔 ЖСН: {help_request.iin}\n"
                f"📂 Санат: {category_text}\n"
                f"💬 Себебі: {help_request.why_need_help}"
            )
        else:
            message = (
                f"🟢 Янги ёрдам сўрови келди:\n\n"
                f"👤 {help_request.name} {help_request.surname}\n"
                f"📞 Телефон рақами: {help_request.phone_number}\n"
                f"📅 Ёши: {help_request.age}\n"
                f"👶 Фарзандлар сони: {help_request.child_in_fam}\n"
                f"🏡 Манзил: {help_request.address}\n"
                f"🆔 ИИН: {help_request.iin}\n"
                f"📂 Тоифа: {category_text}\n"
                f"💬 Сабаб: {help_request.why_need_help}"
            )

        send_to_telegram(message, help_request.file.path if help_request.file else None)
        return redirect(f"/{lang_code}/success/")

    context = {
        "lang_code": lang_code,
        "statuses": statuses,
        "tr": translations,
        "languages": languages,
        "categories": categories,
    }
    return render(request, "index.html", context)







def send_to_telegram(text=None, file_path=None):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    try:

        if file_path is None:
            response = requests.post(
                f"{base_url}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": text or "",
                    "parse_mode": "MarkdownV2",
                },
                timeout=10,
            )
            response.raise_for_status()
            return


        mime_type, _ = mimetypes.guess_type(file_path)
        file_type = "document"  # default

        if mime_type:
            if mime_type.startswith("image/"):
                file_type = "photo"
            elif mime_type.startswith("video/"):
                file_type = "video"


        with open(file_path, "rb") as f:
            files = {file_type: (os.path.basename(file_path), f)}
            endpoint = {
                "photo": "sendPhoto",
                "video": "sendVideo",
                "document": "sendDocument",
            }[file_type]

            response = requests.post(
                f"{base_url}/{endpoint}",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": text or "",
                },
                files=files,
                timeout=30,
            )
            response.raise_for_status()

        print(f"✅ Telegram’га {file_type} муваффақиятли юборилди.")

    except requests.exceptions.Timeout:
        print("⏳ Telegram жавоб бермади (timeout).")
    except requests.exceptions.ConnectionError:
        print("⚠️ Интернет ёки Telegram API блокланган.")
    except Exception as e:
        print(f"❌ Telegram хатолик: {e}")



def success_page(request, lang_code="uz"):
    translations = get_translations(lang_code)
    return render(request, "success.html", {"lang_code": lang_code, "tr": translations})





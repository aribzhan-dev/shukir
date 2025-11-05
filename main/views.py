from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import HelpRequest, Language, MaterialsStatus, Translation, HelpCategory, HelpRequestFile
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
        received_help = request.POST.get("received_other_help") == "yes"
        files = request.FILES.getlist('file')


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
                f"💬 Причина: {help_request.why_need_help}\n"
                f"📦 Получал ли помощь ранее: {'Да' if help_request.received_other_help else 'Нет'}"
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
                f"💬 Себебі: {help_request.why_need_help}\n"
                f"📦 Бұрын көмек алған ба: {'Иә' if help_request.received_other_help else 'Жоқ'}"
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
                f"💬 Сабаб: {help_request.why_need_help}\n"
                f"📦 Илгари бошқа хайрия жамғармаларидан ёрдам олганми: {'Ҳа' if help_request.received_other_help else 'Йўқ'}"
            )


        send_to_telegram(message)

        files = list(help_request.files.all())
        total = len(files)

        for index, f in enumerate(files, start=1):
            try:
                file_path = f.file.path
                caption = f"📎 Файл {index} из {total} — {help_request.name} {help_request.surname}"
                send_to_telegram(file_path=file_path, send_text_also=False, caption=caption)
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






def send_to_telegram(text=None, file_path=None, send_text_also=True, caption=None):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    try:

        if text and send_text_also:
            requests.post(
                f"{base_url}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
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

            endpoint = {
                "photo": "sendPhoto",
                "video": "sendVideo",
                "document": "sendDocument",
            }[file_type]

            with open(file_path, "rb") as f:
                files = {file_type: f}
                data = {"chat_id": TELEGRAM_CHAT_ID}
                if caption:
                    data["caption"] = caption

                response = requests.post(
                    f"{base_url}/{endpoint}",
                    data=data,
                    files=files,
                    timeout=60,
                )
                response.raise_for_status()
                print(f"📎 Fayl yuborildi: {os.path.basename(file_path)} — {response.status_code}")

    except Exception as e:
        print(f"❌ Telegram xatolik: {e}")



def success_page(request, lang_code="uz"):
    translations = get_translations(lang_code)
    return render(request, "success.html", {"lang_code": lang_code, "tr": translations})





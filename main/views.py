from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import HelpRequest, Language, MaterialsStatus, Translation
import requests



TELEGRAM_BOT_TOKEN = "8240282392:AAGtvnPfS3A0R6KQFydGXtBy1vuJ6VUuu9M"
TELEGRAM_CHAT_ID = "-1003120018187"


def get_translations(lang_code):
    language = Language.objects.filter(code=lang_code).first()
    translations = {}
    if language:
        qs = Translation.objects.filter(language=language, status=1)
        for tr in qs:
            translations[tr.key] = tr.value
    return translations


@csrf_exempt
def index_handler(request, lang_code="uz"):
    language = Language.objects.filter(code=lang_code).first()
    translations = get_translations(lang_code)
    statuses = MaterialsStatus.objects.filter(language=language, status=0)

    if request.method == "POST":
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        age = request.POST.get("age")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        status_id = request.POST.get("material_status")
        child_count = request.POST.get("child_in_fam")
        address = request.POST.get("address")
        iin = request.POST.get("iin")
        reason = request.POST.get("why_need_help")

        material_status = MaterialsStatus.objects.get(id=status_id)


        help_request = HelpRequest.objects.create(
            name=name,
            surname=surname,
            age=int(age or 0),
            email=email,
            phone_number=phone,
            material_status=material_status,
            child_in_fam=int(child_count or 0),
            address=address,
            iin=iin,
            why_need_help=reason,
            status=0,
        )

        if lang_code == "ru":
            message = (
                f"🟢 Поступила новая заявка на помощь:\n\n"
                f"👤 {help_request.name} {help_request.surname}\n"
                f"📞 Телефон: {help_request.phone_number}\n"
                f"📅 Возраст: {help_request.age}\n"
                f"👶 Количество детей: {help_request.child_in_fam}\n"
                f"🏡 Адрес: {help_request.address}\n"
                f"🆔 ИИН: {help_request.iin}\n"
                f"💬 Причина обращения: {help_request.why_need_help}"
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
                f"💬 Сабаб: {help_request.why_need_help}"
            )

        send_to_telegram(message)
        return redirect(f"/{lang_code}/success/")


    context = {
        "lang_code": lang_code,
        "statuses": statuses,
        "tr": translations,
    }
    return render(request, "index.html", context)


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("⏳ Telegram жавоб бермади (timeout).")
    except requests.exceptions.ConnectionError:
        print("⚠️ Интернет ёки Telegram API блокланган.")
    except Exception as e:
        print("❌ Номаълум хатолик:", e)



def success_page(request, lang_code="uz"):
    translations = get_translations(lang_code)
    return render(request, "success.html", {"lang_code": lang_code, "tr": translations})





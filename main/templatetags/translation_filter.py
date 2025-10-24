from django import template
from main.models import Translation, Language

register = template.Library()

@register.filter(name='translate')
def translate(key, lang_code):
    try:
        language = Language.objects.filter(code=lang_code).first()
        translation = Translation.objects.filter(language=language, key=key, status=0).first()
        if translation:
            return translation.value
        return key
    except Exception:
        return key
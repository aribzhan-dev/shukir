from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Код языка")
    title = models.CharField(max_length=200, verbose_name="Название языка")
    status = models.IntegerField(default=0, verbose_name="Статус")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Язык"
        verbose_name_plural = "Языки"


class Translation(models.Model):
    key = models.CharField(max_length=200, verbose_name="Ключ перевода")
    language = models.ForeignKey( Language, on_delete=models.CASCADE, verbose_name="Язык")
    value = models.CharField( max_length=200, verbose_name="Перевод")
    position = models.IntegerField( default=0, verbose_name="Позиция")
    status = models.IntegerField( default=0, verbose_name="Статус")

    def __str__(self):
        return f"{self.key} — {self.language.code}"

    class Meta:
        verbose_name = "Перевод"
        verbose_name_plural = "Переводы"


class MaterialsStatus(models.Model):
    language = models.ForeignKey( Language, on_delete=models.CASCADE, verbose_name="Язык")
    title = models.CharField( max_length=100, verbose_name="Семейное положение")
    status = models.IntegerField( default=0, verbose_name="Статус")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Семейное положение"
        verbose_name_plural = "Семейные положения"


class HelpRequest(models.Model):
    name = models.CharField( max_length=200, verbose_name="Имя")
    surname = models.CharField( max_length=200, verbose_name="Фамилия")
    age = models.IntegerField( default=0, blank=True, verbose_name="Возраст")
    email = models.EmailField( blank=True, null=True, verbose_name="Электронная почта")
    phone_number = models.CharField( max_length=20, verbose_name="Номер телефона")
    material_status = models.ForeignKey( MaterialsStatus, on_delete=models.CASCADE, verbose_name="Семейное положение")
    child_in_fam = models.IntegerField( default=0, blank=True, verbose_name="Количество детей")
    address = models.CharField( max_length=200, verbose_name="Адрес")
    iin = models.CharField( max_length=12, blank=True, verbose_name="ИИН")
    why_need_help = models.TextField( verbose_name="Причина обращения за помощью")
    status = models.IntegerField( default=0, verbose_name="Статус")

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        verbose_name = "Заявка на помощь"
        verbose_name_plural = "Заявки на помощь"
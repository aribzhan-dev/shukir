from tkinter.constants import CASCADE

from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

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



class HelpCategory(models.Model):
    title = models.CharField(max_length=250, verbose_name="Название категории помощи")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True)
    is_other = models.BooleanField(default=False, verbose_name="Является 'Другое'")
    group_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Группа категории")
    status = models.IntegerField(default=0, verbose_name="Статус")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория помощи"
        verbose_name_plural = "Категории помощи"


class HelpStatus(models.Model):
    title = models.CharField("Название статуса", max_length=50, unique=True)
    status = models.IntegerField("Статус активности", default=0)

    class Meta:
        verbose_name = "Статус помощи"
        verbose_name_plural = "Статусы помощи"

    def __str__(self):
        return self.title




class HelpRequest(models.Model):
    name = models.CharField( max_length=200, verbose_name="Имя")
    surname = models.CharField( max_length=200, verbose_name="Фамилия")
    age = models.IntegerField( default=0, blank=True, verbose_name="Возраст")
    phone_number = PhoneNumberField(region="KZ", verbose_name="Номер телефона")
    material_status = models.ForeignKey( MaterialsStatus, on_delete=models.CASCADE, verbose_name="Семейное положение")
    help_category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, verbose_name="Категория помощи", blank=True, null=True)
    other_category = models.CharField(max_length=250, blank=True, null=True, verbose_name="Другая категория")
    child_in_fam = models.IntegerField(default=0, blank=True, verbose_name="Количество детей")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    iin = models.CharField(max_length=12, blank=True, verbose_name="ИИН")
    why_need_help = models.TextField(verbose_name="Причина обращения за помощью")
    received_other_help = models.BooleanField(default=False, verbose_name="Получал(а) ли ранее помощь от других фондов")
    help_status = models.ForeignKey(HelpStatus, on_delete=models.CASCADE, verbose_name="Статус помощи", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Создано в")

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        verbose_name = "Заявка на помощь"
        verbose_name_plural = "Заявки на помощь"


class HelpRequestFile(models.Model):
    help_request = models.ForeignKey( HelpRequest, on_delete=models.CASCADE, related_name='files', verbose_name="Заявка на помощь")
    file = models.FileField(upload_to='uploads/', verbose_name="Файл")
    class Meta:
        verbose_name = "Файл заявки"
        verbose_name_plural = "Файлы заявок"

    def __str__(self):
        return f"{self.file.name}"


from django.db import models
from django.utils import timezone

class Employee(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя сотрудника")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия сотрудника")
    status = models.IntegerField(default=0, verbose_name="Статус")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Archive(models.Model):
    help_request = models.ForeignKey('HelpRequest', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Заявка на помощь")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Ответственный сотрудник")
    help_category = models.ForeignKey('HelpCategory', on_delete=models.CASCADE, verbose_name="Категория помощи")
    money = models.DecimalField( default=0.00, max_digits=20, decimal_places=2, verbose_name="Выделенная сумма")
    desc = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    help_status = models.ForeignKey(HelpStatus, on_delete=models.CASCADE, verbose_name="Статус помощи", blank=True, null=True)

    def __str__(self):
        if self.employee:
            return f"{self.employee.first_name} {self.employee.last_name}"
        return f"Архив №{self.id}"

    class Meta:
        verbose_name = "Архив помощи"
        verbose_name_plural = "Архив помощи"








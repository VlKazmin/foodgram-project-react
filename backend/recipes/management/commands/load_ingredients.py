import csv

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from foodgram.settings import INGREDIENT_CSV_FILE_PATH
from recipes.models import Ingredient

MODELS_FILES = {
    "Ingredient": "ingredients.csv",
}


def clear(self):
    """Функция очистки базы данных."""
    Ingredient.objects.all().delete()
    self.stdout.write(self.style.SUCCESS("База данных успешно очищена."))


def load_ingredients(self):
    for model, file in MODELS_FILES.items():
        success = f"Таблица {model} успешно загружена."
        error_load = f"Не удалось загрузить таблицу {model}."
        file_path = f"{INGREDIENT_CSV_FILE_PATH}/{file}"

        try:
            with open(file_path, "r", encoding="utf-8") as csv_file:
                fieldnames = ["name", "measurement_unit"]
                reader = csv.DictReader(csv_file, fieldnames=fieldnames)

                instances_to_create = []

                for data in reader:
                    instance = Ingredient(**data)
                    instances_to_create.append(instance)

                Ingredient.objects.bulk_create(
                    instances_to_create, ignore_conflicts=False
                )
                self.stdout.write(self.style.SUCCESS(success))

        except (FileNotFoundError, IntegrityError, ValueError) as error:
            print(
                self.style.ERROR(f"Ошибка в загрузке. {error}. {error_load}")
            )


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        clear(self)
        load_ingredients(self)

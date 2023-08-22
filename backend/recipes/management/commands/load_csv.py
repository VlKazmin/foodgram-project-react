import csv
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipes.models import Ingredient
from foodgram.settings import INGREDIENT_CSV_FILE_PATH

MODELS_FILES = {
    Ingredient: "ingredients.csv",
}


def clear(self):
    """Функция очистки базы данных."""
    Ingredient.objects.all().delete()
    self.stdout.write(self.style.SUCCESS("База данных успешно очищена."))


def load_csv(self):
    for model, file in MODELS_FILES.items():
        success = f"Таблица {model.__qualname__} успешно загружена."
        error_load = f"Не удалось загрузить таблицу {model.__qualname__}."
        file_path = f"{INGREDIENT_CSV_FILE_PATH}/{file}"

        try:
            with open(file_path, "r", encoding="utf-8") as csv_file:
                fieldnames = ["name", "measurement_unit"]
                reader = csv.DictReader(csv_file, fieldnames=fieldnames)
                instances_to_create = []

                for data in reader:
                    instance = model(**data)
                    instances_to_create.append(instance)

                model.objects.bulk_create(
                    instances_to_create, ignore_conflicts=False
                )
                self.stdout.write(self.style.SUCCESS(success))

        except IntegrityError:
            print(
                self.style.WARNING(
                    "Ошибка уникальности. Конфликтующие значения:"
                )
            )
            for instance in instances_to_create:
                try:
                    instance.save()
                except IntegrityError:
                    print(instance)
                    continue
            print("Конфликтующие значения обработаны.")
            print(self.style.SUCCESS(success))

        except (ValueError, FileNotFoundError) as error:
            print(f"Ошибка в загрузке. {error}. {error_load}")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        clear(self)
        load_csv(self)

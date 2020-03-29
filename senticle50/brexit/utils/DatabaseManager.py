from django.apps import apps
from django.db import models
from django.db import transaction


class DatabaseManager(models.Manager):

    def save_items(self, items, app_name, model_name, overwrite_mode):
        if overwrite_mode:
            self.update_items(items)
        else:
            self.create_bulk(items, app_name, model_name)

    @staticmethod
    @transaction.atomic
    def update_items(item_list):
        for item in item_list:
            item.save()

    @staticmethod
    @transaction.atomic
    def create_bulk(items, app_name, model_name):
        model = apps.get_model(app_name, model_name)
        model.objects.bulk_create(items)

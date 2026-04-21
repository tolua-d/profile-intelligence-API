from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Profile
import json

class Command(BaseCommand):
    def seed_db(self):
        # open data file and write to memory
        with open("seed_profiles.json", "r") as file:
            data = json.load(file)
        self.stdout.write("it has really began")
        profiles = data.get("profiles")
        # check if data already exists and if so, continue
        data_list = []
        for item in profiles:
            self.stdout.write("items in profiles>>>>>>")
            name = item.get("name")
            if Profile.objects.filter(name=name).exists():
                continue
            # append Profile item to list
            data_list.append(Profile(**item))

        self.stdout.write("it has began again>>>>")
        # bulk create to db
        with transaction.atomic():
            Profile.objects.bulk_create(data_list)
            self.stdout.write("has been created")


    def handle(self, *args, **options):
        self.stdout.write("seeding database...")
        self.seed_db()
        self.stdout.write("db populated successfully!", style_func=self.style.SUCCESS)
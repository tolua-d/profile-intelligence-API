from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Profile
import json

class Command(BaseCommand):
    def seed_db(self):
        # open data file and write to memory 
        with open("seed_profiles.json", "r") as file:
            data = json.load(file)
        profiles = data.get("profiles")
        # check if data already exists and if so, continue
        data_list = []
        existing_names = set(
            Profile.objects.values_list("name", flat=True)
        )
        for item in profiles:
            name = item.get("name")
            if name in existing_names:
                continue
            # append Profile item to list
            data_list.append(Profile(**item))

        # bulk create to db
        with transaction.atomic():
            Profile.objects.bulk_create(data_list)


    def handle(self, *args, **options):
        self.stdout.write("seeding database...")
        self.seed_db()
        self.stdout.write("db populated successfully!", style_func=self.style.SUCCESS)
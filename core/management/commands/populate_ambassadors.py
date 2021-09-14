from django.core.management import BaseCommand
from core.models import User
from faker import Faker


class Command(BaseCommand):
    def handle(self, *args, **options):
        faker = Faker()

        for _ in range(30):
            user = User.objects.create(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                password='',
                is_ambassador=True
            )
            user.set_password("1234")
            user.save()

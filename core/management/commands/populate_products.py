from django.core.management import BaseCommand
from core.models import Product
from faker import Faker
from random import randrange

class Command(BaseCommand):
    def handle(self, *args, **options):
        faker = Faker()

        for _ in range(30):
            product = Product.objects.create(
                title=faker.name(),
                description=faker.text(100),
                image=faker.image_url(),
                price=randrange(10,100)
            )

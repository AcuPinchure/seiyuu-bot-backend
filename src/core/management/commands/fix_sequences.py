from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fix PostgreSQL sequences for AutoField primary keys"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Fix core_followers sequence
            cursor.execute(
                """
                SELECT setval('core_followers_id_seq', 
                    (SELECT COALESCE(MAX(id), 1) FROM core_followers), false);
            """
            )

            # Fix core_seiyuu sequence
            cursor.execute(
                """
                SELECT setval('core_seiyuu_id_seq', 
                    (SELECT COALESCE(MAX(id), 1) FROM core_seiyuu), false);
            """
            )

            # Fix core_media sequence (BigAutoField)
            cursor.execute(
                """
                SELECT setval('core_media_id_seq', 
                    (SELECT COALESCE(MAX(id), 1) FROM core_media), false);
            """
            )

            self.stdout.write(self.style.SUCCESS("Successfully fixed all sequences!"))

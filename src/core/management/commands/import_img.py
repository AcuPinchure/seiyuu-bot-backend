import os
from core.models import Media, Seiyuu
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Import new image from ImportQueue to Library, and create Media instance"

    def handle(self, **options):

        for the_seiyuu_instance in Seiyuu.objects.all():
            self.import_image_from_queue(the_seiyuu_instance)

    def import_image_from_queue(self, seiyuu_instance: Seiyuu):
        imgs_path = os.path.join(
            settings.BASE_DIR, "data", "media", "Library", seiyuu_instance.image_folder
        )
        import_path = os.path.join(
            settings.BASE_DIR,
            "data",
            "media",
            "ImportQueue",
            seiyuu_instance.image_folder,
        )

        imgs = os.listdir(imgs_path)
        import_imgs: list[str] = os.listdir(import_path)

        import_len = len(import_imgs)

        for idx, img in enumerate(import_imgs):

            if img in imgs:
                self.stdout.write(
                    self.style.WARNING(
                        f"[{seiyuu_instance.id_name}] {idx+1}/{import_len} - {img} Already exists, skipping"
                    )
                )
                continue

            os.rename(os.path.join(import_path, img), os.path.join(imgs_path, img))

            file_type = "image/jpg"

            if img.lower().endswith(".jpg") or img.lower().endswith(".jpeg"):
                file_type = "image/jpg"
            elif img.lower().endswith(".png"):
                file_type = "image/png"
            elif img.lower().endswith(".mp4"):
                file_type = "video/mp4"
            elif img.lower().endswith(".gif"):
                file_type = "gif/gif"
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"[{seiyuu_instance.id_name}] {idx+1}/{import_len} - {img} Invalid file type: {img.split('.')[-1].lower()}, skipping"
                    )
                )
                continue

            Media.objects.create(
                file_path=os.path.join(seiyuu_instance.image_folder, img),
                seiyuu=seiyuu_instance,
                file_type=file_type,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{seiyuu_instance.id_name}] {idx+1}/{import_len} - {img} Imported"
                )
            )

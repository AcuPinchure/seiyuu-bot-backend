from django.db import models


# Create your models here.
class Seiyuu(models.Model):
    class Meta:
        db_table = "core_seiyuu"

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        help_text="Seiyuu Name, exmaple: 前田佳織里", max_length=20, blank=False
    )
    screen_name = models.CharField(
        help_text="Bot account screen name, example: kaorin__bot",
        max_length=20,
        blank=True,
        null=True,
    )
    id_name = models.CharField(
        help_text="Seiyuu short name, example: kaorin",
        max_length=20,
        blank=True,
        null=True,
    )
    activated = models.BooleanField(help_text="If the bot is activated", default=True)
    interval = models.IntegerField(
        help_text="Interval between tweets in hours", default=1
    )
    image_folder = models.CharField(
        help_text="The folder name of the images", max_length=20, blank=True, null=True
    )

    hidden = models.BooleanField(
        help_text="If the seiyuu should be hidden from website", default=False
    )

    def __str__(self):
        return f"{self.name} @{self.screen_name}"


class Media(models.Model):
    class Meta:
        db_table = "core_media"

    id = models.BigAutoField(primary_key=True)
    file_path = models.CharField(
        help_text="The file path", max_length=1000, blank=False
    )
    file_type = models.CharField(
        max_length=20,
        help_text="The file type",
        choices=[
            ("image/jpg", "JPG"),
            ("image/png", "PNG"),
            ("video/mp4", "MP4"),
            ("gif/gif", "GIF"),
        ],
        default="image/jpg",
    )

    weight = models.FloatField(help_text="Weight for random choice", default=1.0)

    seiyuu = models.ForeignKey(Seiyuu, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.seiyuu.name}-{self.id}"


class Tweet(models.Model):
    class Meta:
        db_table = "core_tweet"

    id = models.CharField(help_text="Tweet ID", primary_key=True)
    post_time = models.DateTimeField(help_text="Tweet time", blank=True, null=True)
    data_time = models.DateTimeField(
        help_text="Data collected time", blank=True, null=True
    )
    like = models.SmallIntegerField(help_text="Likes", blank=True, null=True)
    rt = models.SmallIntegerField(help_text="Retweets", blank=True, null=True)
    reply = models.SmallIntegerField(
        help_text="number of replies", blank=True, null=True
    )
    quote = models.SmallIntegerField(
        help_text="number of quotes", blank=True, null=True
    )

    media = models.ForeignKey(Media, on_delete=models.PROTECT)

    def __str__(self):
        return f"[{self.media.seiyuu.name}]-{self.post_time}-{self.id}"


class Followers(models.Model):
    class Meta:
        db_table = "core_followers"

    id = models.AutoField(primary_key=True)
    seiyuu = models.ForeignKey(Seiyuu, on_delete=models.PROTECT, blank=True, null=True)
    data_time = models.DateTimeField(
        help_text="Data collected time", blank=True, null=True
    )
    followers = models.IntegerField(
        help_text="Current followers", blank=True, null=True
    )

    def __str__(self):
        return f"[{self.seiyuu.name} Followers]-{self.data_time}-{self.followers}"

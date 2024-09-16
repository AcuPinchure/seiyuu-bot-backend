from .models import Seiyuu, Media, Followers, Tweet
from rest_framework import serializers
from django.db.models import Sum


class SeiyuuSerializer(serializers.ModelSerializer):

    last_post = serializers.SerializerMethodField()

    def get_last_post(self, obj):
        if not Tweet.objects.filter(media__seiyuu=obj).exists():
            return "No data"
        return (
            Tweet.objects.filter(media__seiyuu=obj)
            .latest("post_time")
            .post_time.isoformat()
        )

    class Meta:
        model = Seiyuu
        fields = [
            "id",
            "name",
            "screen_name",
            "id_name",
            "activated",
            "interval",
            "last_post",
        ]
        read_only_fields = [
            "id",
            "name",
            "screen_name",
            "id_name",
            "last_post",
        ]


class MediaSerializer(serializers.ModelSerializer):
    total_weight = serializers.SerializerMethodField(read_only=True)
    seiyuu_name = serializers.CharField(source="seiyuu.name", read_only=True)
    seiyuu_screen_name = serializers.CharField(
        source="seiyuu.screen_name", read_only=True
    )
    seiyuu_id_name = serializers.CharField(source="seiyuu.id_name", read_only=True)
    posts = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True)
    rts = serializers.IntegerField(read_only=True)

    def get_total_weight(self, obj) -> int:
        return Media.objects.filter(seiyuu=obj.seiyuu).aggregate(Sum("weight"))[
            "weight__sum"
        ]

    class Meta:
        model = Media
        fields = [
            "id",
            "file_path",
            "file_type",
            "weight",
            "total_weight",
            "seiyuu_name",
            "seiyuu_screen_name",
            "seiyuu_id_name",
            "posts",
            "likes",
            "rts",
        ]
        read_only_fields = [
            "id",
            "file_path",
            "file_type",
            "total_weight",
            "seiyuu_name",
            "seiyuu_screen_name",
            "seiyuu_id_name",
            "posts",
            "likes",
            "rts",
        ]


class StatsQuerySerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    seiyuu = serializers.PrimaryKeyRelatedField(queryset=Seiyuu.objects.all())


class TweetSerializer(serializers.ModelSerializer):

    followers = serializers.SerializerMethodField()

    def get_followers(self, obj) -> int | str:
        if not Followers.objects.filter(
            data_time__lte=obj.post_time, seiyuu=obj.media.seiyuu
        ).exists():
            return "No data"
        return (
            Followers.objects.filter(
                data_time__lte=obj.post_time, seiyuu=obj.media.seiyuu
            )
            .latest("data_time")
            .followers
        )

    class Meta:
        model = Tweet
        fields = [
            "id",
            "post_time",
            "data_time",
            "like",
            "rt",
            "reply",
            "quote",
            "followers",
        ]
        read_only_fields = [
            "id",
            "post_time",
            "data_time",
            "like",
            "rt",
            "reply",
            "quote",
            "followers",
        ]

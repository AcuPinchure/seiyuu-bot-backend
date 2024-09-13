from .models import Seiyuu, Media, Followers, Tweet
from rest_framework import serializers
from django.db.models import Sum


class SeiyuuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seiyuu
        fields = [
            "id",
            "name",
            "screen_name",
            "id_name",
            "activated",
            "interval",
        ]
        read_only_fields = [
            "id",
            "name",
            "screen_name",
            "id_name",
        ]


class MediaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    file_type = serializers.CharField()
    total_weight = serializers.SerializerMethodField()
    seiyuu_name = serializers.CharField(source="seiyuu.name")
    seiyuu_screen_name = serializers.CharField(source="seiyuu.screen_name")
    seiyuu_id_name = serializers.CharField(source="seiyuu.id_name")
    posts = serializers.IntegerField()
    likes = serializers.IntegerField()
    rts = serializers.IntegerField()

    def get_total_weight(self, obj):
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
    id = serializers.CharField()

    followers = serializers.SerializerMethodField()

    def get_followers(self, obj):
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
            "media",
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
            "media",
            "followers",
        ]

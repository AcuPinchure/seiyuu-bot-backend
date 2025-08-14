from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    inline_serializer,
    OpenApiParameter,
)

from rest_framework import serializers
from .serializers import (
    SeiyuuSerializer,
    MediaSerializer,
    StatsQuerySerializer,
    TweetSerializer,
)


def get_status_schema():
    return extend_schema(
        tags=["Stats"],
        parameters=[
            OpenApiParameter(
                name="seiyuu",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Seiyuu id",
            ),
            OpenApiParameter(
                name="start_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Start date in iso format",
            ),
            OpenApiParameter(
                name="end_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="End date in iso format",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Stats response",
                response=inline_serializer(
                    name="StatsResponse",
                    fields={
                        "seiyuu_id": serializers.IntegerField(),
                        "status": serializers.BooleanField(),
                        "start_date": serializers.DateTimeField(),
                        "end_date": serializers.DateTimeField(),
                        "interval": serializers.FloatField(),
                        "posts": serializers.IntegerField(),
                        "scheduled_interval": serializers.IntegerField(),
                        "actual_interval": serializers.FloatField(),
                        "is_active": serializers.BooleanField(),
                        "likes": serializers.IntegerField(),
                        "avg_likes": serializers.FloatField(),
                        "max_likes": serializers.ListField(
                            child=serializers.CharField()
                        ),
                        "rts": serializers.IntegerField(),
                        "avg_rts": serializers.FloatField(),
                        "max_rts": serializers.ListField(child=serializers.CharField()),
                    },
                ),
            )
        },
    )


def get_followers_schema():
    return extend_schema(
        tags=["Stats"],
        parameters=[
            OpenApiParameter(
                name="seiyuu",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Seiyuu id",
            ),
            OpenApiParameter(
                name="start_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Start date in iso format",
            ),
            OpenApiParameter(
                name="end_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="End date in iso format",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Followers response",
                response=inline_serializer(
                    name="FollowerResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "data": inline_serializer(
                            name="Followers",
                            fields={
                                "data_time": serializers.DateTimeField(),
                                "followers": serializers.IntegerField(),
                            },
                            many=True,
                        ),
                    },
                ),
            ),
        },
    )


def get_service_config_schema():
    return extend_schema(
        tags=["Seiyuu"],
        responses={
            200: OpenApiResponse(
                description="Service status response",
                response=inline_serializer(
                    name="SeiyuuResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "data": SeiyuuSerializer(many=True),
                    },
                ),
            )
        },
    )


def update_service_config_schema():
    return extend_schema(
        tags=["Seiyuu"],
        request=OpenApiRequest(request=SeiyuuSerializer, encoding="application/json"),
        responses={
            200: OpenApiResponse(
                description="Service status update response",
                response=inline_serializer(
                    name="SeiyuuUpdateResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "message": serializers.CharField(),
                        "data": SeiyuuSerializer(),
                    },
                ),
            ),
        },
    )


def list_images_schema():
    return extend_schema(
        tags=["Images"],
        parameters=[
            OpenApiParameter(
                name="seiyuu_id_name",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Seiyuu id name",
            ),
            OpenApiParameter(
                name="start_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Start date in iso format",
            ),
            OpenApiParameter(
                name="end_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="End date in iso format",
            ),
            OpenApiParameter(
                name="min_likes",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Minimum number of likes",
            ),
            OpenApiParameter(
                name="max_likes",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Maximum number of likes",
            ),
            OpenApiParameter(
                name="min_rts",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Minimum number of retweets",
            ),
            OpenApiParameter(
                name="max_rts",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Maximum number of retweets",
            ),
            OpenApiParameter(
                name="min_posts",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Minimum number of posts",
            ),
            OpenApiParameter(
                name="max_posts",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Maximum number of posts",
            ),
            OpenApiParameter(
                name="tweet_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Tweet id",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number",
            ),
            OpenApiParameter(
                name="order_by",
                type=str,
                enum=["date", "likes", "rts", "posts"],
                location=OpenApiParameter.QUERY,
                description="order by, default is date, options: date, likes, rts, posts",
            ),
            OpenApiParameter(
                name="order",
                type=str,
                enum=["asc", "desc"],
                location=OpenApiParameter.QUERY,
                description="order, default is desc, options: asc, desc",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Images response",
                response=inline_serializer(
                    name="ImagesResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "count": serializers.IntegerField(),
                        "total_pages": serializers.IntegerField(),
                        "sort_by": serializers.ChoiceField(
                            choices=["date", "likes", "rts", "posts"]
                        ),
                        "order": serializers.ChoiceField(choices=["asc", "desc"]),
                        "page": serializers.IntegerField(),
                        "data": MediaSerializer(many=True),
                    },
                ),
            ),
        },
    )


def list_image_tweets_schema():
    return extend_schema(
        tags=["Images"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Image id",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Image Tweets Response",
                response=inline_serializer(
                    name="ImageTweetsResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "message": serializers.CharField(),
                        "data": TweetSerializer(many=True),
                    },
                ),
            ),
        },
    )


def update_image_weight_schema():
    return extend_schema(
        tags=["Images"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Image id",
            ),
        ],
        request=OpenApiRequest(request=MediaSerializer, encoding="application/json"),
        responses={
            200: OpenApiResponse(
                description="Image Response",
                response=inline_serializer(
                    name="ImageResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "message": serializers.CharField(),
                        "data": MediaSerializer(),
                    },
                ),
            ),
        },
    )


def get_no_data_tweets_schema():
    return extend_schema(
        tags=["Local"],
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Limit number of tweets to return",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="No Data Tweets Response",
                response=inline_serializer(
                    name="NoDataTweetsResponse",
                    fields={
                        "id": serializers.IntegerField(),
                        "post_time": serializers.DateTimeField(),
                        "seiyuu": serializers.CharField(),
                    },
                ),
            ),
        },
    )


def update_tweet_data_schema():
    return extend_schema(
        tags=["Local"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=str,
                location=OpenApiParameter.PATH,
                description="Tweet id",
            ),
        ],
        request=OpenApiRequest(
            request=inline_serializer(
                name="TweetDataUpdate",
                fields={
                    "like": serializers.IntegerField(),
                    "rt": serializers.IntegerField(),
                    "quote": serializers.IntegerField(),
                },
            ),
            encoding="application/json",
        ),
        responses={
            200: OpenApiResponse(
                description="Tweet Response",
                response=inline_serializer(
                    name="TweetResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "message": serializers.CharField(),
                    },
                ),
            ),
        },
    )


def set_followers_schema():
    return extend_schema(
        tags=["Local"],
        request=OpenApiRequest(
            request=inline_serializer(
                name="FollowersData",
                fields={
                    "seiyuu": serializers.CharField(),
                    "followers": serializers.CharField(),
                },
            ),
            encoding="application/json",
        ),
        responses={
            200: OpenApiResponse(
                description="Followers Response",
                response=inline_serializer(
                    name="FollowersResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "message": serializers.CharField(),
                    },
                ),
            ),
        },
    )

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.db.models import Avg, Count, Sum, Max

from core.paginators import StandardResultsSetPagination

from .models import Seiyuu, Tweet, Followers, Media
from .serializers import (
    SeiyuuSerializer,
    MediaSerializer,
    StatsQuerySerializer,
    TweetSerializer,
)
from .utils import get_stats_from_query_options, get_followers_from_query_options

import math

from django.utils import timezone
from datetime import datetime, timedelta

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    inline_serializer,
    OpenApiParameter,
)


# Create your views here.


@extend_schema(
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
                    "max_likes": serializers.ListField(child=serializers.CharField()),
                    "rts": serializers.IntegerField(),
                    "avg_rts": serializers.FloatField(),
                    "max_rts": serializers.ListField(child=serializers.CharField()),
                },
            ),
        )
    },
)
@api_view(["GET"])
def get_stats(request: Request) -> Response:
    """
    get post, like, rt, follower stats, given query options
    """
    serializer = StatsQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    seiyuu = serializer.validated_data["seiyuu"]
    start_date = serializer.validated_data["start_date"]
    end_date = serializer.validated_data["end_date"]

    stats = get_stats_from_query_options(seiyuu, start_date, end_date)

    return Response(stats, status=status.HTTP_200_OK)


@extend_schema(
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
@api_view(["GET"])
def get_followers(request: Request) -> Response:
    """
    get followers, given query options
    """
    serializer = StatsQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    seiyuu = serializer.validated_data["seiyuu"]
    start_date = serializer.validated_data["start_date"]
    end_date = serializer.validated_data["end_date"]

    stats = get_followers_from_query_options(seiyuu, start_date, end_date)

    return Response(
        {
            "status": stats["status"],
            "data": stats["data"],
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
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
@api_view(["GET"])
def get_service_config(request: Request) -> Response:
    """
    load status of all seiyuu
    """
    seiyuu_query = Seiyuu.objects.filter(hidden=False).order_by("id")

    return Response(
        {"status": True, "data": SeiyuuSerializer(seiyuu_query, many=True).data},
        status=status.HTTP_200_OK,
    )


@extend_schema(
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
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_service_config(request: Request, id_name) -> Response:
    """
    update seiyuu status
    """
    data = request.data

    seiyuu = Seiyuu.objects.filter(id_name=id_name).first()

    if not seiyuu:
        return Response(
            {"status": False, "message": "Seiyuu not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Extract the data from the PATCH request using request.data
    serializer = SeiyuuSerializer(
        data=data,
        instance=seiyuu,
    )
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return Response(
        {
            "status": True,
            "message": "Object updated successfully",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_images(request: Request) -> Response:
    """
    list images in the database, given query options
    """
    if request.query_params.get("tweet_id"):
        the_tweet_query = Tweet.objects.filter(id=request.query_params.get("tweet_id"))
        if not the_tweet_query.exists():
            return Response(
                {"status": False, "message": "Tweet not found"},
                status=status.HTTP_200_OK,
            )

        the_image = the_tweet_query.first().media
        image_tweet_set_query = Tweet.objects.filter(media=the_image)
        the_image.posts = image_tweet_set_query.count()
        the_image.likes = (
            image_tweet_set_query.aggregate(max_likes=Max("like"))["max_likes"] or 0
        )
        the_image.rts = (
            image_tweet_set_query.aggregate(max_rts=Max("rt"))["max_rts"] or 0
        )

        serializer = MediaSerializer(the_image, many=False)

        return Response(
            {
                "status": True,
                "count": 1,
                "total_pages": 1,
                "sort_by": "latest_post_time",
                "order": "desc",
                "page": 1,
                "data": [serializer.data],
            },
            status=status.HTTP_200_OK,
        )

    filter_string_list = []

    if request.query_params.get("seiyuu_id_name"):
        filter_string_list.append(
            f"""id_name = '{request.query_params.get("seiyuu_id_name")}'"""
        )

    if request.query_params.get("start_date"):
        filter_string_list.append(
            f"""latest_post_time >= '{request.query_params.get("start_date")}'"""
        )

    if request.query_params.get("end_date"):
        filter_string_list.append(
            f"""earliest_post_time <= '{request.query_params.get("end_date")}'"""
        )

    if request.query_params.get("min_likes"):
        filter_string_list.append(
            f"""likes >= {request.query_params.get("min_likes")}"""
        )

    if request.query_params.get("max_likes"):
        filter_string_list.append(
            f"""likes <= {request.query_params.get("max_likes")}"""
        )

    if request.query_params.get("min_rts"):
        filter_string_list.append(f"""rts >= {request.query_params.get("min_rts")}""")

    if request.query_params.get("max_rts"):
        filter_string_list.append(f"""rts <= {request.query_params.get("max_rts")}""")

    if request.query_params.get("min_posts"):
        filter_string_list.append(
            f"""posts >= {request.query_params.get("min_posts")}"""
        )

    if request.query_params.get("max_posts"):
        filter_string_list.append(
            f"""posts <= {request.query_params.get("max_posts")}"""
        )

    base_raw_query_command = """
            SELECT
                core_media.id,
                core_media.file_path,
                core_media.file_type,
                core_media.weight,
                core_seiyuu.name AS seiyuu_name,
                core_seiyuu.screen_name AS seiyuu_screen_name,
                core_seiyuu.id_name AS seiyuu_id_name,
                tweet_latest_time.post_time AS latest_post_time,
                tweet_earliest_time.post_time AS earliest_post_time,
                tweet_post_count.count AS posts,
                tweet_like_count.count AS likes,
                tweet_rt_count.count AS rts
            FROM core_media
            JOIN core_seiyuu ON core_seiyuu.id = core_media.seiyuu_id
            JOIN
            (
                SELECT
                    media_id,
                    MAX(post_time) AS post_time
                FROM core_tweet
                GROUP BY media_id
            ) AS tweet_latest_time ON core_media.id = tweet_latest_time.media_id
            JOIN
            (
                SELECT
                    media_id,
                    MIN(post_time) AS post_time
                FROM core_tweet
                GROUP BY media_id
            ) AS tweet_earliest_time ON core_media.id = tweet_earliest_time.media_id
            JOIN
            (
                SELECT
                    media_id,
                    COUNT(id) AS count
                FROM core_tweet
                GROUP BY media_id
            ) AS tweet_post_count ON core_media.id = tweet_post_count.media_id
            JOIN
            (
                SELECT
                    media_id,
                    MAX(core_tweet."like") AS count
                FROM core_tweet
                GROUP BY media_id
            ) AS tweet_like_count ON core_media.id = tweet_like_count.media_id
            JOIN
            (
                SELECT
                    media_id,
                    MAX(core_tweet.rt) AS count
                FROM core_tweet
                GROUP BY media_id
            ) AS tweet_rt_count ON core_media.id = tweet_rt_count.media_id
    """

    if filter_string_list:
        base_raw_query_command += " WHERE " + " AND ".join(filter_string_list)

    base_image_query = Media.objects.raw(base_raw_query_command)

    image_count = len(base_image_query)

    sort_by = request.query_params.get("sort_by", None)
    order = request.query_params.get("order", None)

    if not sort_by in [
        "latest_post_time",
        "earliest_post_time",
        "likes",
        "rts",
        "posts",
    ]:
        sort_by = "latest_post_time"
    if not order in ["asc", "desc"]:
        order = "desc"

    raw_query_command_with_order = f"""
        {base_raw_query_command}
        ORDER BY {sort_by} {order.upper()}
    """

    image_query = Media.objects.raw(raw_query_command_with_order)

    if not image_query:
        return Response(
            {
                "status": False,
                "message": "No images found",
                "count": 0,
                "total_pages": 1,
                "sort_by": sort_by,
                "order": order,
                "page": 1,
                "data": [],
            },
            status=status.HTTP_200_OK,
        )

    page = request.query_params.get("page", None)

    try:
        page = int(page)
    except:
        page = 1

    page_size = 20

    total_pages = math.ceil(image_count / page_size) or 1

    page = min(page, total_pages)

    paginated_serializer = MediaSerializer(
        image_query[(page - 1) * page_size : page * page_size], many=True
    )

    return Response(
        {
            "status": True,
            "count": image_count,
            "total_pages": total_pages,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "data": paginated_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
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
@api_view(["GET"])
def list_image_tweets(request: Request, pk) -> Response:
    """
    list tweets that contains the image
    """
    try:
        the_image = Media.objects.get(pk=pk)
    except Media.DoesNotExist:
        return Response(
            {
                "status": False,
                "message": "Image not found",
                "data": [],
            },
            status=status.HTTP_200_OK,
        )

    image_tweet_set_query = Tweet.objects.filter(media=the_image).order_by("-post_time")

    serializer = TweetSerializer(image_tweet_set_query, many=True)

    return Response(
        {
            "status": True,
            "message": "",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
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
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_image_weight(request: Request, pk: int) -> Response:
    """
    update image weight
    """
    try:
        the_image = Media.objects.get(pk=pk)
    except Media.DoesNotExist:
        return Response(
            {"status": False, "message": "Image not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = request.data

    serializer = MediaSerializer(
        data=data,
        instance=the_image,
    )
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return Response(
        {
            "status": True,
            "message": "Object updated successfully",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


########### local api ############


@extend_schema(
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
@api_view(["GET"])
def get_no_data_tweets(request):
    """
    get all tweets that has not been analyzed, api for local only

    [url params]
    limit: limit number of tweets to return, to prevent twitter from blocking

    [return]
    id: tweet id
    post_time: tweet post time
    seiyuu: seiyuu screen name

    """
    if not request.get_host() in settings.LOCAL_HOSTS:
        return Response(
            {"message": "Not allowed host name"}, status=status.HTTP_403_FORBIDDEN
        )

    no_data_tweets = Tweet.objects.select_related("media__seiyuu")

    time_buffer = 72  # hours

    no_data_tweets = no_data_tweets.filter(
        data_time__isnull=True,
        post_time__lte=timezone.now() - timedelta(hours=time_buffer),
    ).order_by("post_time")

    if request.GET.get("limit"):
        limit = int(request.GET.get("limit"))
        no_data_tweets = no_data_tweets[:limit]

    data = no_data_tweets.values("id", "post_time", "media__seiyuu__screen_name")

    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
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
@api_view(["PATCH"])
def update_tweet_data(request, pk):
    """
    write data to a tweet, api for local only

    [body params]
    like: number of likes
    rt: number of retweets
    quote: number of quotes
    """
    if not request.get_host() in settings.LOCAL_HOSTS:
        return Response(
            {"message": "Not allowed host name"}, status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Retrieve the object you want to update based on the 'pk' parameter
        the_tweet = Tweet.objects.get(pk=pk)
    except Tweet.DoesNotExist:
        return Response(
            {"status": False, "message": "Tweet not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Extract the data from the PUT request using request.data
    data = request.data

    # Update the fields of the object with the data from the request
    the_tweet.data_time = timezone.now()
    the_tweet.like = data.get("like")
    the_tweet.rt = data.get("rt")
    # the_tweet.reply = data.get('reply')
    the_tweet.quote = data.get("quote")
    # Add more fields as needed

    # Save the updated object to the database
    the_tweet.save()

    return Response(
        {"status": True, "message": "Object updated successfully"},
        status=status.HTTP_200_OK,
    )


@extend_schema(
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
@api_view(["POST"])
def set_followers(request):
    """
    write current followers to database, api for local only

    [body params]
    seiyuu: seiyuu screen_name
    followers: number of followers
    """
    if not request.get_host() in settings.LOCAL_HOSTS:
        return Response(
            {"status": False, "message": "Not allowed host name"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Extract the data from the POST request using request.data
    data = request.data

    Followers.objects.create(
        data_time=timezone.now(),
        seiyuu=Seiyuu.objects.get(screen_name=data.get("seiyuu")),
        followers=int(data.get("followers")),
    )

    return Response(
        {"status": True, "message": "Object create successfully"},
        status=status.HTTP_200_OK,
    )

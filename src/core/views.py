import math
from datetime import timedelta
from random import choices

from django.conf import settings
from django.db.models import Max
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Followers, Media, Seiyuu, Tweet
from .serializers import (
    MediaSerializer,
    SeiyuuSerializer,
    StatsQuerySerializer,
    TweetSerializer,
)
from .swagger import (
    create_tweet_schema,
    get_auth_token_schema,
    get_followers_schema,
    get_no_data_tweets_schema,
    get_random_media_schema,
    get_service_config_schema,
    get_status_schema,
    list_image_tweets_schema,
    list_images_schema,
    set_followers_schema,
    update_image_weight_schema,
    update_service_config_schema,
    update_tweet_data_schema,
)
from .utils import get_followers_from_query_options, get_stats_from_query_options

# Create your views here.


@get_status_schema()
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


@get_followers_schema()
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


@get_service_config_schema()
@api_view(["GET"])
def get_service_config(request: Request) -> Response:
    """
    load status of all seiyuu
    """

    if request.user.is_authenticated or request.get_host() in settings.LOCAL_HOSTS:
        seiyuu_query = Seiyuu.objects.all().order_by("id")
    else:
        seiyuu_query = Seiyuu.objects.filter(hidden=False).order_by("id")

    return Response(
        {"status": True, "data": SeiyuuSerializer(seiyuu_query, many=True).data},
        status=status.HTTP_200_OK,
    )


@update_service_config_schema()
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


@list_images_schema()
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
    except (TypeError, ValueError):
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


@list_image_tweets_schema()
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


@update_image_weight_schema()
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


@get_no_data_tweets_schema()
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
    if request.get_host() not in settings.LOCAL_HOSTS:
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


@update_tweet_data_schema()
@api_view(["PATCH"])
def update_tweet_data(request, pk):
    """
    write data to a tweet, api for local only

    [body params]
    like: number of likes
    rt: number of retweets
    quote: number of quotes
    """
    if request.get_host() not in settings.LOCAL_HOSTS:
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


@set_followers_schema()
@api_view(["POST"])
def set_followers(request):
    """
    write current followers to database, api for local only

    [body params]
    seiyuu: seiyuu screen_name
    followers: number of followers
    """
    if request.get_host() not in settings.LOCAL_HOSTS:
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


@get_auth_token_schema()
@api_view(["GET"])
def get_auth_token(request: Request, pk: int) -> Response:
    """
    get the auth token of a seiyuu account, api for local only

    [path params]
    pk: seiyuu id

    [return]
    id: seiyuu id
    id_name: seiyuu short name
    screen_name: bot account screen name
    auth_token: the auth token in cookie when login as the account
    """
    if request.get_host() not in settings.LOCAL_HOSTS:
        return Response(
            {"status": False, "message": "Not allowed host name"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        the_seiyuu = Seiyuu.objects.get(pk=pk)
    except Seiyuu.DoesNotExist:
        return Response(
            {"status": False, "message": "Seiyuu not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "status": True,
            "message": "",
            "data": {
                "id": the_seiyuu.id,
                "id_name": the_seiyuu.id_name,
                "screen_name": the_seiyuu.screen_name,
                "auth_token": the_seiyuu.auth_token,
            },
        },
        status=status.HTTP_200_OK,
    )


@get_random_media_schema()
@api_view(["GET"])
def get_random_media(request: Request, pk: int) -> Response:
    """
    pick a random media of a seiyuu by weight, api for local only

    [path params]
    pk: seiyuu id
    """
    if request.get_host() not in settings.LOCAL_HOSTS:
        return Response(
            {"status": False, "message": "Not allowed host name"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        the_seiyuu = Seiyuu.objects.get(pk=pk)
    except Seiyuu.DoesNotExist:
        return Response(
            {"status": False, "message": "Seiyuu not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    media_q = Media.objects.filter(seiyuu=the_seiyuu)
    media_pks = media_q.values_list("pk", flat=True)
    media_weights = media_q.values_list("weight", flat=True)

    if not media_pks or sum(media_weights) <= 0:
        return Response(
            {"status": False, "message": "No media found", "data": None},
            status=status.HTTP_200_OK,
        )

    random_pk = choices(media_pks, media_weights)[0]
    random_media = media_q.get(pk=random_pk)

    return Response(
        {
            "status": True,
            "message": "",
            "data": MediaSerializer(random_media).data,
        },
        status=status.HTTP_200_OK,
    )


@create_tweet_schema()
@api_view(["POST"])
def create_tweet(request: Request) -> Response:
    """
    create a tweet record after posting, api for local only

    [body params]
    id: tweet id
    post_time: tweet post time in iso format, default is now
    media: media id
    """
    if request.get_host() not in settings.LOCAL_HOSTS:
        return Response(
            {"status": False, "message": "Not allowed host name"},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data

    tweet_id = data.get("id")

    if not tweet_id:
        return Response(
            {"status": False, "message": "Tweet id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Tweet.objects.filter(pk=tweet_id).exists():
        return Response(
            {"status": False, "message": "Tweet already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        the_media = Media.objects.get(pk=data.get("media"))
    except (Media.DoesNotExist, TypeError, ValueError):
        return Response(
            {"status": False, "message": "Media not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    post_time = data.get("post_time")

    if post_time:
        post_time = parse_datetime(post_time) if isinstance(post_time, str) else None
        if not post_time:
            return Response(
                {"status": False, "message": "Invalid post_time"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if timezone.is_naive(post_time):
            post_time = timezone.make_aware(post_time)
    else:
        post_time = timezone.now()

    the_tweet = Tweet.objects.create(
        id=tweet_id,
        post_time=post_time,
        media=the_media,
    )

    return Response(
        {
            "status": True,
            "message": "Object create successfully",
            "data": TweetSerializer(the_tweet).data,
        },
        status=status.HTTP_200_OK,
    )

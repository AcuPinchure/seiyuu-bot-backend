from .models import Seiyuu, Tweet, Followers
from datetime import datetime, timedelta
from django.db.models import Avg, Sum


def get_stats_from_query_options(
    seiyuu: Seiyuu,
    start_date: datetime,  # tz aware
    end_date: datetime,  # tz aware
) -> dict:
    """
    Get the stats from the query options
    """
    tweet_query = Tweet.objects.filter(
        media__seiyuu=seiyuu,
        post_time__gte=start_date,
        post_time__lte=end_date,
        data_time__isnull=False,
    ).order_by("data_time")

    if not tweet_query:
        return {"status": False, "message": "No tweets found in the given interval"}

    tweet_count = tweet_query.count()
    interval = (
        tweet_query.last().post_time - tweet_query.first().post_time
    ) / timedelta(hours=1)

    like_count = tweet_query.aggregate(sum_likes=Sum("like"))["sum_likes"] or 0
    avg_likes = tweet_query.aggregate(avg_likes=Avg("like"))["avg_likes"] or 0
    max_likes = map(
        lambda number: str(number),
        tweet_query.order_by("-like").values_list("id", flat=True)[:10],
    )

    rt_count = tweet_query.aggregate(sum_rt=Sum("rt"))["sum_rt"] or 0
    avg_rts = tweet_query.aggregate(avg_rt=Avg("rt"))["avg_rt"] or 0
    max_rts = map(
        lambda number: str(number),
        tweet_query.order_by("-rt").values_list("id", flat=True)[:10],
    )

    return {
        "status": True,
        "start_date": tweet_query.first().post_time.isoformat(),
        "end_date": tweet_query.last().post_time.isoformat(),
        "interval": interval,
        "posts": tweet_count,
        "scheduled_interval": seiyuu.interval,
        "actual_interval": interval / (tweet_count - 1),
        "is_active": seiyuu.activated,
        "likes": like_count,
        "avg_likes": avg_likes,
        "max_likes": max_likes,
        "rts": rt_count,
        "avg_rts": avg_rts,
        "max_rts": max_rts,
    }


def get_followers_from_query_options(
    seiyuu: Seiyuu,
    start_date: datetime,  # tz aware
    end_date: datetime,  # tz aware
) -> dict:

    follower_query = Followers.objects.filter(
        seiyuu=seiyuu, data_time__gte=start_date, data_time__lte=end_date
    ).order_by("data_time")

    if not follower_query:
        return {
            "status": False,
            "message": "No followers found in the given interval",
        }

    # get real start and end date
    start_date = follower_query.first().data_time
    end_date = follower_query.last().data_time
    data_count = follower_query.count()

    # if data points is more than 200, get data with even interval
    if data_count > 200:
        time_anchors = []
        # get time interval in seconds
        interval = (end_date - start_date).total_seconds() / 199
        # get time anchors
        curr_time = start_date
        while curr_time < end_date:
            time_anchors.append(curr_time)
            curr_time += timedelta(seconds=interval)

        time_anchors.append(end_date)

        json_data = []

        curr_diff = 0
        prev_diff = 0
        prev_data_point = follower_query[0]
        # get data with even interval
        for data_point in follower_query[1:]:
            curr_diff = abs(data_point.data_time - time_anchors[0])
            if data_point.data_time > time_anchors[0]:
                if prev_diff and curr_diff > prev_diff:
                    json_data.append(
                        {
                            "data_time": prev_data_point.data_time.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "followers": prev_data_point.followers,
                        }
                    )
                else:
                    json_data.append(
                        {
                            "data_time": data_point.data_time.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "followers": data_point.followers,
                        }
                    )
                time_anchors.pop(0)
            prev_diff = curr_diff
            prev_data_point = data_point
        json_data.append(
            {
                "data_time": end_date.strftime("%Y-%m-%d %H:%M"),
                "followers": follower_query.last().followers,
            }
        )
    else:
        json_data = follower_query.values("data_time", "followers").order_by(
            "data_time"
        )

    return {"status": True, "data": json_data}

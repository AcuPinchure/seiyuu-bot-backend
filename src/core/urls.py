from django.urls import include, path
from . import views


service_config_patterns = [
    path("", views.get_service_config, name="get_service_config"),
    path(
        "update/<str:id_name>/",
        views.update_service_config,
        name="update_service_config",
    ),
]

image_patterns = [
    path("", views.list_images, name="list_images"),
    path("<int:pk>/tweets/", views.list_image_tweets, name="list_image_tweets"),
    path(
        "<int:pk>/update_weight/", views.update_image_weight, name="update_image_weight"
    ),
]

local_patterns = [
    path("get_no_data_tweets/", views.get_no_data_tweets, name="get_no_data_tweets"),
    path(
        "update_tweet_data/<str:pk>/", views.update_tweet_data, name="update_tweet_data"
    ),
    path("set_followers/", views.set_followers, name="set_followers"),
]


urlpatterns = [
    path("stats/", views.get_stats, name="get_stats"),
    path("followers/", views.get_followers, name="get_followers"),
    path("service_config/", include(service_config_patterns)),
    path("images/", include(image_patterns)),
    path("local/", include(local_patterns)),
]

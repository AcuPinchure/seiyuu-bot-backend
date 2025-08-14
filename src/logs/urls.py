from django.urls import include, path
from . import views

urlpatterns = [
    path(
        "backend/<path:path>",
        views.serve_backend_log_file_or_directory,
        name="serve_backend_log_file_or_directory",
    ),
    path(
        "crawler/<path:path>",
        views.serve_crawler_log_file_or_directory,
        name="serve_crawler_log_file_or_directory",
    ),
    path("import/", views.import_log, name="import_log"),
    path("get/<str:pk>/", views.get_log, name="get_log"),
    path("list/", views.list_log, name="list_log"),
]

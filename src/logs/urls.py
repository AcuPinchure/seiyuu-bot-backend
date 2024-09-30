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
]

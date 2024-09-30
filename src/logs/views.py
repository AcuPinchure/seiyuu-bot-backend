import os
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    inline_serializer,
    OpenApiParameter,
)


def load_log_file_or_directory(log_path: str) -> Response:
    # Check if the path exists
    if not os.path.exists(log_path):
        return Response(
            {
                "status": False,
                "message": "Path does not exist",
                "list_dir": [],
                "log": "",
            }
        )

    # Initialize the response structure
    response_data = {"status": True, "list_dir": [], "log": ""}

    # If the path is a directory, list its contents
    if os.path.isdir(log_path):
        try:
            response_data["list_dir"] = os.listdir(log_path)
        except PermissionError:
            return Response(
                {
                    "status": False,
                    "message": "Permission denied",
                    "list_dir": [],
                    "log": "",
                },
                status=403,
            )
        return Response(response_data)

    # If the path is a file, return its content
    elif os.path.isfile(log_path):
        # Check if the file is a .log or .txt file
        if log_path.endswith(".log") or log_path.endswith(".txt"):
            try:
                with open(log_path, "r") as f:
                    response_data["log"] = f.read()
            except Exception as e:
                response_data["status"] = False
                response_data["message"] = str(e)
        else:
            response_data["message"] = "The file is not a text file"
        return Response(response_data)

    # If it's neither a file nor a directory, return status False
    return Response(
        {"status": False, "message": "Invalid path", "list_dir": [], "log": ""},
        status=400,
    )


@extend_schema(
    tags=["Logs"],
    parameters=[
        OpenApiParameter(
            name="path",
            type=str,
            location=OpenApiParameter.PATH,
            required=False,
            description="Path to the log file or directory",
        )
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="LogResponse",
                fields={
                    "status": "boolean",
                    "list_dir": ["string"],
                    "log": "string",
                    "message": "string",
                },
            ),
            examples=[
                OpenApiExample(
                    "LogResponse",
                    value={
                        "status": True,
                        "list_dir": ["file1.log", "file2.log"],
                        "log": "Log content",
                        "message": "",
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            response=inline_serializer(
                name="ErrorResponse", fields={"status": "boolean", "message": "string"}
            ),
            examples=[
                OpenApiExample(
                    "ErrorResponse", value={"status": False, "message": "Invalid path"}
                )
            ],
        ),
        403: OpenApiResponse(
            response=inline_serializer(
                name="ErrorResponse", fields={"status": "boolean", "message": "string"}
            ),
            examples=[
                OpenApiExample(
                    "ErrorResponse",
                    value={"status": False, "message": "Permission denied"},
                )
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serve_backend_log_file_or_directory(request, path=""):
    """
    View to serve the post service log file or directory.
    Path "/logs/backend//" will return the list of files in the BACKEND_LOG_ROOT directory.
    """

    # Ensure the requested path is within the LOG_ROOT
    if path and not path.startswith("..") and not path.startswith("/"):
        log_path = os.path.join(settings.BACKEND_LOG_ROOT, path)
    else:
        log_path = settings.BACKEND_LOG_ROOT

    return load_log_file_or_directory(log_path)


@extend_schema(
    tags=["Logs"],
    parameters=[
        OpenApiParameter(
            name="path",
            type=str,
            location=OpenApiParameter.PATH,
            required=False,
            description="Path to the log file or directory",
        )
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="LogResponse",
                fields={
                    "status": "boolean",
                    "list_dir": ["string"],
                    "log": "string",
                    "message": "string",
                },
            ),
            examples=[
                OpenApiExample(
                    "LogResponse",
                    value={
                        "status": True,
                        "list_dir": ["file1.log", "file2.log"],
                        "log": "Log content",
                        "message": "",
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            response=inline_serializer(
                name="ErrorResponse", fields={"status": "boolean", "message": "string"}
            ),
            examples=[
                OpenApiExample(
                    "ErrorResponse", value={"status": False, "message": "Invalid path"}
                )
            ],
        ),
        403: OpenApiResponse(
            response=inline_serializer(
                name="ErrorResponse", fields={"status": "boolean", "message": "string"}
            ),
            examples=[
                OpenApiExample(
                    "ErrorResponse",
                    value={"status": False, "message": "Permission denied"},
                )
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serve_crawler_log_file_or_directory(request, path=""):
    """
    View to serve the crawler log file or directory.
    Path "/logs/crawler//" will return the list of files in the CRAWLER_LOG_ROOT directory.
    """

    # Ensure the requested path is within the LOG_ROOT
    if path and not path.startswith("..") and not path.startswith("/"):
        log_path = os.path.join(settings.CRAWLER_LOG_ROOT, path)
    else:
        log_path = settings.CRAWLER_LOG_ROOT

    return load_log_file_or_directory(log_path)

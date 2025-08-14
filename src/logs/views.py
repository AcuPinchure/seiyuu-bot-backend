import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    inline_serializer,
    OpenApiParameter,
)

from .serializers import (
    ImportLogSerializer,
    GetLogQuerySerializer,
    ListLogQuerySerializer,
)
from .elasticsearch_client import es_logs_client
from .swagger import (
    import_log_schema,
    get_log_schema,
    list_log_schema,
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


@get_log_schema()
@api_view(["GET"])
def get_log(request: Request, pk: str) -> Response:
    """
    Get a specific log entry
    """
    serializer = GetLogQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    log_type = serializer.validated_data["type"]

    try:
        log_data = es_logs_client.get_log(log_type, str(pk))

        if log_data is None:
            return Response(
                {"status": False, "message": "Log not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(log_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"status": False, "message": f"Failed to get log: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@list_log_schema()
@api_view(["GET"])
def list_log(request: Request) -> Response:
    """
    List log entries with filtering
    """
    serializer = ListLogQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    log_type = serializer.validated_data["type"]
    min_date = serializer.validated_data.get("min_date")
    max_date = serializer.validated_data.get("max_date")
    keyword = serializer.validated_data.get("keyword")
    page = serializer.validated_data.get("page", 1)

    try:
        # Validate page limit
        if page > 50:
            return Response(
                {"status": False, "message": "Page number cannot exceed 50"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert date objects to strings if provided
        min_date_str = min_date.strftime("%Y-%m-%d") if min_date else None
        max_date_str = max_date.strftime("%Y-%m-%d") if max_date else None

        logs = es_logs_client.list_logs(
            log_type=log_type,
            page=page,
            keyword=keyword,
            min_date=min_date_str,
            max_date=max_date_str,
        )

        return Response(logs, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"status": False, "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"status": False, "message": f"Failed to list logs: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@import_log_schema()
@api_view(["POST"])
def import_log(request):
    """
    Import log entry, API for local only
    """
    if request.get_host() not in settings.LOCAL_HOSTS:
        return Response(
            {"status": False, "message": "Not allowed host name"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ImportLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        log_type = serializer.validated_data["type"]
        log_time = serializer.validated_data["log_time"]
        file_name = serializer.validated_data["file_name"]
        content = serializer.validated_data["content"]

        doc_id = es_logs_client.create_log(log_type, log_time, file_name, content)

        return Response(
            {"status": True, "message": f"Log created successfully with ID: {doc_id}"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": False, "message": f"Failed to create log: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

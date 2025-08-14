from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiRequest,
    inline_serializer,
)
from rest_framework import serializers
from .serializers import ImportLogSerializer, LogSerializer


def import_log_schema():
    return extend_schema(
        tags=["Local"],
        request=OpenApiRequest(
            request=ImportLogSerializer, encoding="application/json"
        ),
        responses={
            200: OpenApiResponse(
                description="Import Log Response",
                response=inline_serializer(
                    name="ImportLogResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "message": serializers.CharField(),
                    },
                ),
            ),
        },
    )


def get_log_schema():
    return extend_schema(
        tags=["Logs"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=str,
                location=OpenApiParameter.PATH,
                description="Log id",
            ),
            OpenApiParameter(
                name="type",
                type=str,
                enum=["post", "data"],
                location=OpenApiParameter.QUERY,
                description="Log type",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Log Response",
                response=LogSerializer,
            ),
        },
    )


def list_log_schema():
    return extend_schema(
        tags=["Logs"],
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                enum=["post", "data"],
                location=OpenApiParameter.QUERY,
                description="Log type",
                required=True,
            ),
            OpenApiParameter(
                name="min_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Minimum date in yyyy-mm-dd format",
                required=False,
            ),
            OpenApiParameter(
                name="max_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Maximum date in yyyy-mm-dd format",
                required=False,
            ),
            OpenApiParameter(
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Keyword to search in content",
                required=False,
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number (1-50)",
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Log List Response",
                response=inline_serializer(
                    name="LogListResponse",
                    fields={
                        "status": serializers.BooleanField(),
                        "data": serializers.ListField(),
                    },
                ),
            ),
        },
    )
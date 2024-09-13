from datetime import timedelta
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from django.utils import timezone

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    inline_serializer,
)

# Create your views here.


@extend_schema(
    responses={
        200: OpenApiResponse(
            description="OK",
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "Example 1",
                    value={"detail": "Authentication credentials were not provided."},
                )
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def test_login(request: Request) -> Response:
    """
    Test if the user is authenticated
    """
    return Response(status=status.HTTP_200_OK)


@extend_schema(
    request=OpenApiRequest(
        request=TokenObtainPairSerializer,
        encoding={"application/json": {}},
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "username": "konachi@apollobay.com.jp",
                    "password": "password123",
                },
            )
        ],
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="TokenObtainPairResponse",
                fields={
                    "detail": "Login successful",
                    "user": inline_serializer(
                        name="User",
                        fields={
                            "id": serializers.IntegerField(),
                            "username": serializers.CharField(),
                            "email": serializers.EmailField(),
                        },
                    ),
                },
            ),
        ),
        400: OpenApiResponse(description="Bad Request"),
        401: OpenApiResponse(
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "Example 1",
                    value={
                        "detail": "No active account found with the given credentials"
                    },
                )
            ],
        ),
        404: OpenApiResponse(description="Not Found"),
    },
)
@api_view(["POST"])
@parser_classes([JSONParser])
def login(request: Request) -> Response:
    """
    Set cookie with access token on successful login.
    """

    serializer = TokenObtainPairSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.user

    validated_data = serializer.validated_data

    response = Response(
        {
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        status=status.HTTP_200_OK,
    )

    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=validated_data["access"],
        expires=timezone.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],  # Set to True if using HTTPS
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )

    return response


@api_view(["POST"])
def logout(request: Request) -> Response:
    """
    Clear cookie with access token on logout.
    """

    response = Response(status=status.HTTP_200_OK)

    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value="",
        expires=timezone.now() - timedelta(days=1),
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],  # Set to True if using HTTPS
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )

    return response

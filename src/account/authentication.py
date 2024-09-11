from django.conf import settings
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.authentication import AuthUser, JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


# This class is used to authenticate the user by JWT token in the cookie.
class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> tuple[AuthUser, Token] | None:

        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except AuthenticationFailed:
            # If token validation fails, treat the user as anonymous
            return None

        return self.get_user(validated_token), validated_token

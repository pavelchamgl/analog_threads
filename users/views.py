from drf_yasg import openapi
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users import permissions, serializers
from users.base_views import BaseOtpView, BaseOTPVerifyView
from users.models import User


class UserCreateApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.NotAuthenticate,)
    serializer_class = serializers.SignUpSerializer


class LogoutView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['refresh_token'],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Successfully logged out.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid token or token not provided.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
            ),
        },
        operation_description='Log out by blacklisting the provided refresh token.',
    )
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'})
        except Exception:
            return Response({'detail': 'Invalid token or token not provided.'})


class ForgotPasswordApiView(BaseOtpView):
    permission_classes = [AllowAny]
    serializer = serializers.ForgotPasswordMessageSendSerializer

    subject = "Password Recovery"
    message = "Hi {username}! You can recover you password by using code: {otp}"
    otp_title = "ForgotPassword"


class ConfirmEmailView(BaseOtpView):
    permission_classes = [IsAuthenticated]
    serializer = serializers.ConfirmEmailMessageSendSerializer

    subject = "Email Confirmation"
    message = "Hi {username}! You can confirm you email by using code: {otp}"
    otp_title = "EmailConfirmation"


class ForgotPasswordOTPVerifyView(BaseOTPVerifyView):
    serializer = serializers.OTPSerializer
    permission_classes = [AllowAny]

    otp_title = "ForgotPassword"


class ConfirmEmailOTPVerifyView(BaseOTPVerifyView):
    serializer = serializers.OTPSerializer
    permission_classes = [IsAuthenticated]

    otp_title = "EmailConfirmation"


class ForgotPasswordUpdateApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_INTEGER),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'password2': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'otp', 'password', 'password2'],
        ),
        responses={
            200: openapi.Response(
                description='Password changed successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(
                description='Validation error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
        }
    )
    def put(self, request):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update_password()
            return Response(serializer.data)
        else:
            return Response({'detail': serializer.error_messages})


class ConfirmEmailUpdateApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['email', 'otp'],
        ),
        responses={
            200: openapi.Response(
                description='Email confirm successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(
                description='Validation error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
        }
    )
    def put(self, request):
        serializer = serializers.ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update_email_confirmation()
            return Response(serializer.data)
        else:
            return Response({'detail': serializer.error_messages})

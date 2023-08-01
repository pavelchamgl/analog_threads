from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users import permissions, serializers
from users.utils import send_reset_email


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


class ForgotPasswordApiView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email'],
        ),
        responses={
            200: openapi.Response(
                description='Reset password email sent successfully!',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description='User not found!',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            500: openapi.Response(
                description='Error sending email',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
        }
    )
    def post(self, request):
        email = request.data['email']
        user = User.objects.get(email=email)
        if user:
            otp, is_send = send_reset_email(user.email, user.username)
            if not is_send:
                return Response({"detail": "Error sending email"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
            user.otp = otp
            user.save()
        else:
            return Response({"detail": "User not found"}, status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Reset password email sent successfully!"}, status.HTTP_200_OK)


class ForgotPasswordVerifyApiView(APIView):
    permission_classes = [AllowAny]

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
                description='OTP verified successfully!',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(
                description='User not found or Invalid email or OTP',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
        }
    )
    def post(self, request):
        email = request.data['email']
        otp = request.data['otp']
        if not email or not otp:
            return Response({"detail": "Please provide both email and OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, otp=otp)
        except User.DoesNotExist:
            return Response({"detail": "Invalid email or OTP"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "OTP verified successfully!"})

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




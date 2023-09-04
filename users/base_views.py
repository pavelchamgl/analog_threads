import random

from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.exceptions import OTPExpired
from users.models import User, OTP
from users.utils import send_email, otp_update_or_create


class BaseOtpView(APIView):
    subject = ""
    message = ""
    otp_title = ""

    serializer = None
    otp = random.randint(1000, 9999)

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
                description='Message success!',
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
        serializer = self.serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            if user:
                is_send = send_email(user.email, self.subject, self.message, username=user.username, otp=self.otp)
                otp_update_or_create(self.otp_title, self.otp, email)
                if not is_send:
                    return Response({"detail": "Error sending email"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"detail": "User not found"}, status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Message successfully sent!"}, status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors})


class BaseOTPVerifyView(APIView):
    serializer = serializers.OTPSerializer
    model = OTP

    otp_title = ""

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
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            try:
                otp = OTP.objects.get(user__email=serializer.validated_data['email'], title=self.otp_title,
                                      value=serializer.validated_data['otp'])
                if otp.expired_date < timezone.now():
                    raise OTPExpired()
            except (OTP.DoesNotExist, OTPExpired):
                return Response({"detail": "Invalid email or invalid OTP or expired"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": "OTP verified successfully!"})
        else:
            return Response({"details": serializer.errors})

from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users import permissions, serializers


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

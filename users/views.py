from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users import permissions, serializers
from users.base_views import BaseOtpView, BaseOTPVerifyView
from users.models import User, Follow
from users.serializers import UserProfileDataSerializer, FollowsSerializer


class UserCreateApiView(generics.CreateAPIView):
    """API view for creating new user model instances."""
    queryset = User.objects.all()
    permission_classes = (permissions.NotAuthenticate,)
    serializer_class = serializers.SignUpSerializer


class UserProfileView(generics.RetrieveAPIView):
    """API view to retrieve user profile data."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserProfileDataSerializer


class UserProfileUpdateView(generics.UpdateAPIView):
    """API view to update user profile data."""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileDataSerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        user_id = self.request.user.pk
        queryset = User.objects.get(pk=user_id)
        return queryset


class FollowersListView(generics.ListAPIView):
    """API view to retrieve a list of followers for a given user."""
    permission_classes = (permissions.PublicOrPrivateProfilePermission,)
    serializer_class = FollowsSerializer

    def get_queryset(self):
        followee_id = self.kwargs.get('followee_pk')
        queryset = Follow.objects.filter(followee_id=followee_id, allowed=True)
        return queryset


class FollowersListPendingView(generics.ListAPIView):
    """API view to retrieve a list of pending followers for the authenticated user."""
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowsSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        queryset = Follow.objects.filter(followee_id=user_id, allowed=False)
        return queryset


class FollowingListView(generics.ListAPIView):
    """API view to retrieve a list of users followed by a given follower."""
    permission_classes = (permissions.PublicOrPrivateProfilePermission,)
    serializer_class = serializers.FollowsSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('follower_pk')
        queryset = Follow.objects.filter(follower_id=user_id, allowed=True)
        return queryset


class FollowActionView(APIView):
    """API view for performing a follow action on a user profile."""
    primary_serializer = serializers.FollowActionSerializer
    secondary_serializer = serializers.MutualFollowSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=serializers.FollowActionSerializer,
        responses={status.HTTP_200_OK: serializers.MutualFollowSerializer},
    )
    def post(self, request):
        serializer = self.primary_serializer(data=request.data)
        if serializer.is_valid():
            followee_id = serializer.validated_data['followee'].pk
            followee = get_object_or_404(User, pk=followee_id)
            follower = request.user

            if Follow.objects.filter(followee=followee, follower=follower).exists():
                return Response({'error': 'You already followed this user'}, status=status.HTTP_400_BAD_REQUEST)

            allowed = not followee.is_private
            follow = Follow.objects.create(followee=followee, follower=follower, allowed=allowed)

            mutual_follow_data = self.secondary_serializer(instance=follow).data
            return Response(mutual_follow_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnfollowActionView(APIView):
    """API view for performing an unfollow action on a user profile."""
    serializer = serializers.FollowActionSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=serializers.FollowActionSerializer,
        responses={status.HTTP_200_OK: serializers.FollowActionSerializer},
    )
    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            follower = request.user
            followee = serializer.validated_data['followee']
            follow = get_object_or_404(Follow, follower=follower, followee=followee)
            follow.delete()
            return Response({'action': "unfollowed", 'followee_id': followee.id})
        else:
            return Response({'error': serializer.error_messages}, status=status.HTTP_404_NOT_FOUND)


class DeleteFollowerView(APIView):
    """API view for deleting a follower from the authenticated user's followers list."""
    serializer = serializers.FollowPendingSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=serializers.FollowPendingSerializer,
        responses={status.HTTP_200_OK: serializers.FollowPendingSerializer},
    )
    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            follower = serializer.validated_data['follower']
            follow = get_object_or_404(
                Follow, followee=request.user.id, follower=follower)
            follow.delete()
            return Response({'action': "deleted", 'follower_id': follower.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowPendingConfirm(APIView):
    """API view for confirming pending follow requests."""
    primary_serializer = serializers.FollowPendingSerializer
    secondary_serializer = serializers.MutualFollowSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=serializers.FollowPendingSerializer,
        responses={status.HTTP_200_OK: serializers.MutualFollowSerializer},
    )
    def post(self, request):
        serializer = self.primary_serializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data['follower'].id)
            print(i.follower.pk for i in Follow.objects.filter(followee=request.user.id, allowed=False))
            follow = get_object_or_404(
                Follow, followee=request.user.id, follower=serializer.validated_data['follower'].id, allowed=False)
            follow.allowed = True
            follow.save()

            mutual_follow_serializer_instance = self.secondary_serializer(follow)

            return Response(mutual_follow_serializer_instance.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowPendingDecline(APIView):
    """API view for declining pending follow requests."""
    serializer = serializers.FollowPendingSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=serializers.FollowPendingSerializer,
        responses={status.HTTP_200_OK: serializers.FollowPendingSerializer},
    )
    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            follower = serializer.validated_data['follower']
            follow = get_object_or_404(
                Follow, followee=request.user.id, follower=follower, allowed=False)
            follow.delete()
            return Response({'action': "deleted", 'follower_id': follower.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API view for logging out a user."""

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
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Invalid token or token not provided.'}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordApiView(BaseOtpView):
    """API view for sending password recovery OTP to users."""
    permission_classes = [AllowAny]
    serializer = serializers.ForgotPasswordMessageSendSerializer

    subject = "Password Recovery"
    message = "Hi {username}! You can recover you password by using code: {otp}"
    otp_title = "ForgotPassword"


class ConfirmEmailView(BaseOtpView):
    """API view for sending email confirmation one-time passwords (OTP)."""
    permission_classes = [IsAuthenticated]
    serializer = serializers.ConfirmEmailMessageSendSerializer

    subject = "Email Confirmation"
    message = "Hi {username}! You can confirm you email by using code: {otp}"
    otp_title = "EmailConfirmation"


class ForgotPasswordOTPVerifyView(BaseOTPVerifyView):
    """API view for verifying one-time password (OTP) during the forgot password process."""
    serializer = serializers.OTPSerializer
    permission_classes = [AllowAny]

    otp_title = "ForgotPassword"


class ConfirmEmailOTPVerifyView(BaseOTPVerifyView):
    """API view for verifying the one-time password (OTP) during the password recovery process."""
    serializer = serializers.OTPSerializer
    permission_classes = [IsAuthenticated]

    otp_title = "EmailConfirmation"


class ForgotPasswordUpdateApiView(APIView):
    """API view for updating a user's forgotten password."""
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': serializer.error_messages}, status=status.HTTP_404_NOT_FOUND)


class ConfirmEmailUpdateApiView(APIView):
    """API view for updating email confirmation status."""
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': serializer.error_messages}, status=status.HTTP_404_NOT_FOUND)

import random
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from config.tasks import send_email
from users import validators
from users.exceptions import OTPExpired
from users.models import User, OTP, Follow
from users.utils import otp_update_or_create


class SelfUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'full_name', 'bio', 'website', 'location', 'photo', 'is_private', 'is_email_verify']


class UserProfileDataSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    bio = serializers.CharField(required=False)
    website = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    photo = serializers.URLField(required=False)
    full_name = serializers.CharField(required=False)
    is_private = serializers.BooleanField(required=False)
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['pk', 'username', 'full_name', 'bio', 'website', 'location', 'photo', 'is_private', 'is_followed']

    def get_is_followed(self, obj):
        user_id = self.context['request'].user.id
        followee_id = obj.id

        if user_id == followee_id:
            return "You"
        try:
            follow = Follow.objects.get(followee_id=followee_id, follower_id=user_id)
        except Follow.DoesNotExist:
            follow = None
        try:
            lookup_user_follow = Follow.objects.get(followee_id=user_id, follower_id=followee_id)
        except Follow.DoesNotExist:
            lookup_user_follow = None

        if follow and lookup_user_follow:
            return "Mutual Follow"
        if follow:
            return "Followed" if follow.allowed else "Pending"
        if lookup_user_follow:
            return "Follow in response"
        return "Not Followed"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'full_name', 'bio', 'website', 'location', 'photo', 'is_private']


class FollowersSerializer(serializers.ModelSerializer):
    follower = UserProfileSerializer()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['follower', 'is_followed']

    def get_is_followed(self, obj):
        user_id = self.context['request'].user.id
        followee_id = obj.follower.id

        if user_id == followee_id:
            return "You"
        try:
            follow = Follow.objects.get(followee_id=followee_id, follower_id=user_id)
        except Follow.DoesNotExist:
            return "Not Followed"
        return "Followed" if follow.allowed else "Pending"


class FollowsSerializer(serializers.ModelSerializer):
    followee = UserProfileDataSerializer()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['followee', 'is_followed']

    def get_is_followed(self, obj):
        user_id = self.context['request'].user.id
        followee_id = obj.followee.id

        if user_id == followee_id:
            return "You"
        try:
            follow = Follow.objects.get(followee_id=followee_id, follower_id=user_id)
        except Follow.DoesNotExist:
            return "Not Followed"
        return "Followed" if follow.allowed else "Pending"


class MutualFollowSerializer(serializers.ModelSerializer):
    followee = UserProfileDataSerializer()
    follower = UserProfileDataSerializer()

    class Meta:
        model = Follow
        fields = ['followee', 'follower', 'allowed']


class MutualFollowSubscribeSerializer(serializers.ModelSerializer):
    followee = UserProfileSerializer()
    follower = UserProfileSerializer()

    class Meta:
        model = Follow
        fields = ['followee', 'follower', 'allowed']


class FollowActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['followee']


class FollowPendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['follower']


class OTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )
    otp = serializers.IntegerField(
        required=True,
        validators=[validators.otp_validator]
    )

    class Meta:
        model = OTP
        fields = ['email', 'otp']


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        write_only=True
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        write_only=True
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validators.password_validator])
    password2 = serializers.CharField(write_only=True, required=True)

    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'refresh', 'access')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        username = attrs['username'].lower()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})

        attrs['username'] = username
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        otp = random.randint(1000, 9999)
        subject = "Email Confirmation"
        message = f"Hi {user.username}! You can confirm you email by using code: {otp}"
        otp_title = "EmailConfirmation"

        send_email.delay(user.email, subject, message, username=user.username, otp=otp)
        otp_update_or_create(otp_title, otp, user.email)

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )

    otp = serializers.IntegerField(
        required=True,
        validators=[validators.otp_validator]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validators.password_validator])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'otp', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def update_password(self):
        try:
            otp = OTP.objects.get(user__email=self.validated_data['email'], value=self.validated_data['otp'])
            if otp.expired_date < timezone.now():
                raise OTPExpired
            otp.value = None
            otp.user.set_password(self.validated_data['password'])
            otp.save()
            otp.user.save()
        except (OTP.DoesNotExist, OTPExpired):
            raise serializers.ValidationError({'detail': "This user does not exist or otp incorrect or expired"})


class ForgotPasswordMessageSendSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )

    class Meta:
        model = User
        fields = ['email']


class ConfirmEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )

    otp = serializers.IntegerField(
        required=True,
        validators=[validators.otp_validator]
    )

    class Meta:
        model = User
        fields = ('email', 'otp')

    def update_email_confirmation(self):
        try:
            otp = OTP.objects.get(user__email=self.validated_data['email'], value=self.validated_data['otp'])
            if otp.expired_date < timezone.now():
                raise OTPExpired
            otp.value = None
            otp.user.is_email_verify = True
            otp.save()
            otp.user.save()
        except (OTP.DoesNotExist, OTPExpired):
            raise serializers.ValidationError({'detail': "This user does not exist or otp incorrect or expired"})


class ConfirmEmailMessageSendSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        if self.context['request'].user.email != attrs['email']:
            raise serializers.ValidationError({"email": "You haven't permission to send confirm request to this mail"})

        if self.context['request'].user.is_email_verify:
            raise serializers.ValidationError({"email": "Email already confirmed"})

        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    remember_me = serializers.BooleanField(required=False)

    def validate(self, attrs):
        data = super().validate(attrs)
        remember_me = self.context['request'].data.get('remember_me')
        if remember_me:
            refresh = self.get_token(self.user)
            refresh.set_exp(lifetime=timedelta(days=30))  # Set the refresh token lifetime to 30 days
            data['refresh'] = str(refresh)
        return data


class UserProfilePhotoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['photo']

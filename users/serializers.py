from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users import validators
from users.exceptions import OTPExpired
from users.models import User, OTP, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        models = User
        fields = ['email', 'username']


class UserProfileDataSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    bio = serializers.CharField(required=False)
    website = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['pk', 'username', 'bio', 'website', 'location', 'photo']


class FollowersSerializer(serializers.ModelSerializer):
    follower = UserProfileDataSerializer()
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
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validators.password_validator])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

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

        return user


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
            otp.user.is_e = True
            otp.user.set_password(self.validated_data['password'])
            otp.save()
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
            refresh_token = data['refresh']
            self.context['request'].set_cookie('refresh_token', refresh_token, httponly=True, max_age=3600 * 24 * 7)
        return data

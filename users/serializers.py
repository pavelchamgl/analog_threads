from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users import validators
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        models = User
        fields = ['email', 'username']


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
        user = User.objects.get(email=self.validated_data['email'], otp=self.validated_data['otp'])
        if user:
            user.set_password(self.validated_data['password'])
            user.save()
        else:
            raise serializers.ValidationError({'detail': "This user does not exist or otp incorrect or expired"})

import re

from rest_framework import serializers


def password_validator(password: str):
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$'
    match = re.fullmatch(pattern, password)
    if not match:
        raise serializers.ValidationError(
            'Password must exist at least 8 chars and have one char, number and special char')


def otp_validator(otp: int):
    if type(otp) != int:
        raise serializers.ValidationError(
            'OTP must been an integer'
        )
    if not len(str(otp)) == 4:
        raise serializers.ValidationError(
            'OTP must contain 4 integers'
        )

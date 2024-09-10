from rest_framework import serializers
from rest_framework import serializers
from .models import CustomUser, RoleCodes
from rest_framework import serializers
from books.models import Book, Category, Author, Comment


class VerificationCodeSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=6)


class UserRoleSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleCodes.CHOICES)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'role']


from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        label=_("Password"),
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        style={"input_type": "password"},
        min_length=8,
        label=_("Confirm Password"),
        write_only=True,
    )

    class Meta:
        model = User
        fields = ["id", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": _("Passwords don't match.")})
        attrs.pop("password2", None)
        return attrs

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        if password := validated_data.pop("password", None):
            instance.set_password(password)
        return super().update(instance, validated_data)

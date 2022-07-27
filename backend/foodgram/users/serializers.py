from djoser.serializers import UserSerializer
from users.models import User


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('login', 'password', 'name', 'surname', 'email')

from djoser.views import UserViewSet
from .serializers import CustomUserSerializer
from .models import User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    seriazer_class = CustomUserSerializer

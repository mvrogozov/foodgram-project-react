from django.urls import path

from .views import tag_list


urlpatterns = [
    path('tags/', tag_list, name='api_tag_list')
]

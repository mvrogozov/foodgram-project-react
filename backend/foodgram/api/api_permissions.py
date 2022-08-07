from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, obj):
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

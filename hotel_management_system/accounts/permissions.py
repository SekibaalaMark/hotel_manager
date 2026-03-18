from rest_framework.permissions import BasePermission

class IsManager(BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists()




from rest_framework.permissions import BasePermission


class IsGuest(BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Guest").exists()
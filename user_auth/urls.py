from django.urls import path
from rest_framework.routers import DefaultRouter

from user_auth.views import (
    LoginView,
    RefreshView,
    LogoutView,
    RegisterUserView,
    UpdateUserView,
    DeleteUserView,
    UserViewSet, RoleViewSet, PermissionViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"roles", RoleViewSet, basename="roles")
router.register(r"permissions", PermissionViewSet, basename="permissions")

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("update/", UpdateUserView.as_view(), name="update"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("delete/", DeleteUserView.as_view(), name="delete"),
]

urlpatterns += router.urls

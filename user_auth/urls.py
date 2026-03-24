from django.urls import path
from rest_framework.routers import DefaultRouter

from user_auth.views import (
    LoginView,
    RefreshView,
    LogoutView,
    RegisterUserView,
    UpdateUserView,
    DeleteUserView, UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("update/", UpdateUserView.as_view(), name="update"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("delete/", DeleteUserView.as_view(), name="delete"),
]

urlpatterns += router.urls

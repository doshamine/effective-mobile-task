from django.urls import path
from rest_framework.routers import DefaultRouter

from user_auth.views import UserViewSet, LoginView, RefreshView, LogoutView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

urlpatterns += router.urls

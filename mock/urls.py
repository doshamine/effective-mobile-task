from rest_framework.routers import DefaultRouter

from mock.views import MockView

router = DefaultRouter()
router.register("mocks", MockView, basename="mocks")

urlpatterns = router.urls

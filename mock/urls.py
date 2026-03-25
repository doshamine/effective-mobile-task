from rest_framework.routers import DefaultRouter

from mock.views import MockView

router = DefaultRouter()
router.register(r"items", MockView, basename="items")

urlpatterns = router.urls

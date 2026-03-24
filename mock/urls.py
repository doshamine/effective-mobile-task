from rest_framework.routers import DefaultRouter

from mock.views import MockView

router = DefaultRouter()
router.register("items", MockView, basename="items")

urlpatterns = router.urls

from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from anagram.views import AnagramViewSet, WordAPIView, WordViewSet

router = DefaultRouter()

router.register("words", WordViewSet, basename="words")
router.register("anagrams", AnagramViewSet, basename="anagrams")


urlpatterns = [
    # Default redirect to Swagger UI
    path("", RedirectView.as_view(url=reverse_lazy("swagger-ui")), name="index"),
    # Words / Anagrams related URLs
    path("words.json/", WordAPIView.as_view(), name="words"),
] + router.urls

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet, RecipeLinkAPIView,
    AddToFavoriteAPIView,
    AddToShoppingCartAPIView,
    DownloadPDFAPIView
)


router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('download_shopping_cart/', DownloadPDFAPIView.as_view()),
    path('', include(router.urls)),
    path('<int:id>/get-link/', RecipeLinkAPIView.as_view()),
    path('<int:id>/favorite/', AddToFavoriteAPIView.as_view()),
    path('<int:id>/shopping_cart/', AddToShoppingCartAPIView.as_view())
]

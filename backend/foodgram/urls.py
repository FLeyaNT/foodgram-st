from django.contrib import admin
from django.urls import path, include

from recipes.views import RecipeByShortLinkAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('s/<str:code>/', RecipeByShortLinkAPIView.as_view()),
    path('api/users/', include('users.urls')),
    path('api/ingredients/', include('ingredients.urls')),
    path('api/recipes/', include('recipes.urls')),

    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]

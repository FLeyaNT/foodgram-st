from django.contrib import admin
from django.urls import path, include

from api.views import RecipeByShortLinkAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('s/<str:code>/', RecipeByShortLinkAPIView.as_view()),
    path('api/', include('api.urls')),
]

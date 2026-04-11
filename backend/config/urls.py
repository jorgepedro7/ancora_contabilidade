from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from backend.apps.core.views import CustomTokenObtainPairView

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/core/', include('backend.apps.core.urls')),
    path('api/empresas/', include('backend.apps.empresas.urls')),
    path('api/cadastros/', include('backend.apps.cadastros.urls')),
    path('api/fiscal/', include('backend.apps.fiscal.urls')),
    path('api/financeiro/', include('backend.apps.financeiro.urls')),
    path('api/estoque/', include('backend.apps.estoque.urls')),
    path('api/folha/', include('backend.apps.folha.urls')),
    path('api/contabil/', include('backend.apps.contabil.urls')),
    path('api/obrigacoes/', include('backend.apps.obrigacoes.urls')),
    path('api/intake/', include('backend.apps.intake.urls')),
    path('api/relatorios/', include('backend.apps.relatorios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

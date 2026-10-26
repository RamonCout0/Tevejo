from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Renova o access token JWT emitido pelo Login (CDU001)
    path("api/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),

    path("api/comunidades/", include("comunidades.urls")),
    path('api/conteudos/', include('conteudos.urls')),
    path('api/usuarios/', include('usuarios.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Uploads (fotos, ícones, banners). O `static()` do Django só funciona com
    # DEBUG=True; servimos sempre para a imagem Docker também exibir as mídias.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

"""myzone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static, serve
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from .settings import STATIC_ROOT, MEDIA_ROOT

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', serve, { 'document_root': STATIC_ROOT }),
    re_path(r'^media/(?P<path>.*)$', serve, { 'document_root': MEDIA_ROOT }),
]

urlpatterns += i18n_patterns(
    path('', include('myzoneapp.urls')),
    path('admin/', admin.site.urls),
    path('vditor/', include('vditor.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

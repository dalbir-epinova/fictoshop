"""
URL configuration for fictoshop_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("django-admin/", RedirectView.as_view(pattern_name="admin:index", permanent=False)),
    path("", include("shop.urls")),
]

if settings.ASSETS_DIR.exists():
    urlpatterns += [
        re_path(r"^assets/(?P<path>.*)$", serve, {"document_root": settings.ASSETS_DIR}),
    ]

if settings.IMAGES_DIR.exists():
    urlpatterns += [
        re_path(r"^images/(?P<path>.*)$", serve, {"document_root": settings.IMAGES_DIR}),
    ]

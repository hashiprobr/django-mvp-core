from django.contrib import admin
from django.urls import path, include

from .utils import build_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += build_urlpatterns()

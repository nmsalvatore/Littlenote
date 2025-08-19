from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("src.apps.pages.urls")),
    path("notes/", include("src.apps.notes.urls")),
    path("admin/", admin.site.urls),
]

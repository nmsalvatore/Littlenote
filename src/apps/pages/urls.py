from django.urls import path

from .views.front_page import FrontPageView

app_name = "pages"

urlpatterns = [
    path("", FrontPageView.as_view(), name="front"),
]

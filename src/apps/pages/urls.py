from django.urls import path

from .views.front_page import FrontPageView
from .views.dashboard import DashboardView

app_name = "pages"

urlpatterns = [
    path("", FrontPageView.as_view(), name="front"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

from django.urls import path

from .views import FrontPageView, DashboardView

app_name = "pages"

urlpatterns = [
    path("", FrontPageView.as_view(), name="front"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

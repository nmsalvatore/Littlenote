from django.conf import settings


def site_settings(request):
    return {
        "SITE_TITLE": getattr(settings, "SITE_TITLE", "Site title not set")
    }

def back_button_context(request):
    return {
        "previous_url": request.session.get("previous_url", "/")
    }

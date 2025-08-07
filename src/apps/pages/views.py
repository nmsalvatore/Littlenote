from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        passcode = request.POST.get("passcode")

        if email and not passcode:
            # TODO: send code

            if request.headers.get("HX-Request"):
                return render(request, "pages/partials/otp_form.html", {
                    "email": email
                })

            else:
                return render(request, self.template_name, {
                    "otp_sent": True,
                    "email": email,
                })

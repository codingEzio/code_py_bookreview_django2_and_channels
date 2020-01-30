from django.views.generic.edit import FormView
from main import forms


class ContactUsView(FormView):
    """
    [Notes]
    FromView is a generic class-based views for form processing.
    """

    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)

import logging

from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages

from main import forms
from main import models


logger = logging.getLogger(name=__name__)


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


class ProductListView(ListView):
    """
    This view could be used for displaying products by kind or simply all.

    [Note]
    You might found that there are lots of never-appeared variable names in
    the templates, it actually all derived from the pagination part, the
    file is: 'YOUR_ENV/lib/python3.?/site-packages/Django/core/paginator.py'.
    """

    template_name = "product_list.html"
    paginate_by = 3

    def get_queryset(self):
        arg_tag = self.kwargs["tag"]
        self.tag = None

        if arg_tag != "all":
            self.tag = get_object_or_404(models.ProductTag, slug=arg_tag)

        if self.tag:
            products = models.Product.objects.active().filter(tags=self.tag)
        else:
            products = models.Product.objects.active()

        return products.order_by("name")


class SignupView(FormView):
    """
    A signup view built based on customized version of UserCreationForm.
    """
    template_name = "signup.html"
    form_class = forms.UserCreationForm  # my own version of it

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")

        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form=form)
        form.save()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(f"New signup for email={email} through SignupView")

        user = authenticate(email=email, password=raw_password)
        login(request=self.request, user=user)

        form.send_mail()

        messages.info(
            request=self.request, message="You signed up successfully."
        )

        return response

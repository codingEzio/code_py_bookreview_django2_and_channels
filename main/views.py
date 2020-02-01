from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from main import forms
from main import models


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

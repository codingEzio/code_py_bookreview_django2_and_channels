import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)

from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django import forms as django_forms
from django.db import models as django_models

import django_filters
from django_filters.views import FilterView

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


class AddressListView(LoginRequiredMixin, ListView):
    """
    The name of the templates should conform to the parent views.
    """

    model = models.Address
    context_object_name = "address_list"  # default: object_list

    def get_queryset(self):
        """
        Limit what users could see (their own addresses only).
        """
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    """
    The name of the templates should conform to the parent views.
    """

    model = models.Address

    fields = ["name", "address1", "address2", "postal_code", "city", "country"]
    success_url = reverse_lazy(viewname="main:address_list")

    def form_valid(self, form):
        """
        Add one more thing (user) to the form.
        """
        obj = form.save(commit=False)

        obj.user = self.request.user
        obj.save()

        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """
    The name of the templates should conform to the parent views.
    """

    model = models.Address

    fields = ["name", "address1", "address2", "postal_code", "city", "country"]
    success_url = reverse_lazy(viewname="main:address_list")

    def get_queryset(self):
        """
        Limit what users could see (their own addresses only).
        """
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """
    The name of the templates should conform to the parent views.
    """

    model = models.Address

    success_url = reverse_lazy(viewname="main:address_list")

    def get_queryset(self):
        """
        Limit what users could see (their own addresses only).
        """
        return self.model.objects.filter(user=self.request.user)


class AddressSelectonView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy(viewname="main:checkout_done")

    def get_form_kwargs(self):
        """
        We extracts the user from the request and returns it in a dictionary.
        Then the form (AddressSelectionForm) would receive the `user` for
        further uses.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):
        del self.request.session["basket_id"]

        basket = self.request.basket
        basket.create_order(
            billing_address=form.cleaned_data["billing_address"],
            shipping_address=form.cleaned_data["shipping_address"],
        )

        return super().form_valid(form)


def add_to_basket(request):
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )
    basket = request.basket

    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id

    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )

    if not created:
        basketline.quantity += 1
        basketline.save()

    return HttpResponseRedirect(
        redirect_to=reverse(viewname="main:product", args=(product.slug,))
    )


def manage_basket(request):
    # No baskets yet
    if not request.basket:
        return render(
            request=request,
            template_name="basket.html",
            context={"formset": None},
        )

    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )

        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(instance=request.basket)

    # Do "have" basket but nothing was added yet
    if request.basket.is_empty():
        return render(
            request=request,
            template_name="basket.html",
            context={"formset": None},
        )

    # Basket with some products
    return render(
        request=request,
        template_name="basket.html",
        context={"formset": formset},
    )


class DateInput(django_forms.DateInput):
    """
    The format would respects format localization (e.g. 02/02/2020).
    """

    input_type = "date"


class OrderFilter(django_filters.FilterSet):
    """
    Basically, django-filter allows users to filter down a query set based on
    a model's fields, AND displaying the form to let them do this.
    """

    class Meta:
        model = models.Order

        fields = {
            "user__email": ["icontains"],
            "status": ["exact"],
            "date_updated": ["gt", "lt"],
            "date_added": ["gt", "lt"],
        }
        filter_overrides = {
            django_models.DateTimeField: {
                "filter_class": django_filters.DateFilter,
                "extra": lambda f: {"widget": DateInput},
            }
        }


class OrderView(UserPassesTestMixin, FilterView):
    """
    We didn't specify the template's location cuz django-filter has its own
    convention, i.e. '<app>/<model>_filter.html' ('order_filter' in our case).
    """

    filterset_class = OrderFilter  # attribute of FilterView
    login_url = reverse_lazy(viewname="main:login")

    def test_func(self):
        return self.request.user.is_staff is True

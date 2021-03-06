from django.urls import path, include
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import views as auth_views

from rest_framework import routers as rest_routers

from main import views, forms
from main import models
from main import endpoints

app_name = "main"

router = rest_routers.DefaultRouter()
router.register(r"orderlines", endpoints.PaidOrderLineViewSet)
router.register(r"orders", endpoints.PaidOrderViewSet)

urlpatterns = [
    # Basket
    path(
        route="add_to_basket/", view=views.add_to_basket, name="add_to_basket",
    ),
    path(route="basket/", view=views.manage_basket, name="basket"),
    # Product
    path(
        route="products/<slug:tag>/",
        view=views.ProductListView.as_view(),
        name="products",
    ),
    path(
        route="product/<slug:slug>/",
        view=DetailView.as_view(model=models.Product),
        name="product",
    ),
    # Product Address
    path(
        route="address/",
        view=views.AddressListView.as_view(),
        name="address_list",
    ),
    path(
        route="address/create/",
        view=views.AddressCreateView.as_view(),
        name="address_create",
    ),
    path(
        route="address/<int:pk>/",
        view=views.AddressUpdateView.as_view(),
        name="address_update",
    ),
    path(
        route="address/<int:pk>/delete/",
        view=views.AddressDeleteView.as_view(),
        name="address_delete",
    ),
    # Order
    path(
        route="order/address_select/",
        view=views.AddressSelectonView.as_view(),
        name="address_select",
    ),
    path(
        route="order-dashboard/",
        view=views.OrderView.as_view(),
        name="order_dashboard",
    ),
    path(
        route="order/done/",
        view=TemplateView.as_view(template_name="order_done.html"),
        name="checkout_done",
    ),
    # Auth
    path(route="signup/", view=views.SignupView.as_view(), name="signup",),
    path(
        route="login/",
        view=auth_views.LoginView.as_view(
            template_name="login.html", form_class=forms.AuthenticationForm,
        ),
        name="login",
    ),
    # API (rest_framework)
    path(route="api/", view=include(router.urls)),
    # Base
    path(
        route="customer-service/<int:order_id>/",
        view=views.room,
        name="customer_service_chat",
    ),
    path(
        route="contact-us/",
        view=views.ContactUsView.as_view(),
        name="contact_us",
    ),
    path(
        route="about-us/",
        view=TemplateView.as_view(template_name="about_us.html"),
        name="about_us",
    ),
    path(
        route="",
        view=TemplateView.as_view(template_name="home.html"),
        name="index",
    ),
]

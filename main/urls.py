from django.urls import path
from django.views.generic import TemplateView, DetailView

from main import views, models

app_name = "main"

urlpatterns = [
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

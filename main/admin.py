from datetime import datetime, timedelta
import logging

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum  # noqa
from django.urls import path
from django.template.response import TemplateResponse
from django import forms

from . import models


logger = logging.getLogger(name=__name__)


""" The "actions" for admin site """


def make_active(self, request, queryset):
    queryset.update(active=True)


def make_inactive(self, request, queryset):
    """
    Basically it's like a soft-delete almost for any Django ORM objects.
    """
    queryset.update(active=False)


make_active.short_description = "Mark selected item as active"
make_inactive.short_description = "Mark selected item as inactive"


""" The generic admin sites """


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")},),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")},),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "in_stock", "price")
    list_filter = ("active", "in_stock", "date_updated")
    list_editable = ("in_stock",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("tags",)
    actions = [make_active, make_inactive]

    def get_readonly_fields(self, request, obj=None):
        """
        About the field 'slug':
          it's an important field for our site, it is used in all the product
          URLs. We want to limit the ability to change this ONLY TO the owners
          of the company.
        """
        if request.user.is_superuser:
            return self.readonly_fields

        return list(self.readonly_fields) + ["slug", "name"]

    def get_prepopulated_fields(self, request, obj=None):
        """
        Required for 'get_readonly_fields' to work.
        """
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}


class DispatchersProductAdmin(ProductAdmin):
    readonly_fields = ("description", "price", "tags", "active")
    prepopulated_fields = {}
    autocomplete_fields = ()


class ProductTagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    list_filter = ("active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        return list(self.readonly_fields) + ["slug", "name"]

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}


class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail_tag",
        "product_name",
    )
    search_fields = ("product__name",)
    readonly_fields = ("thumbnail",)

    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                format_string=f'<img src="{obj.thumbnail.url}" />'
            )
        return "-"

    def product_name(self, obj):
        return obj.product.name

    thumbnail_tag.short_description = "Thumbnail"


class BasketLineInLine(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ("product",)


class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInLine,)


class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("product",)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (OrderLineInline,)

    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_postal_code",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_postal_code",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )


class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "address1",
        "address2",
        "city",
        "country",
    )
    readonly_fields = ("user",)


""" The role-specific classes """


class CentralOfficeOrderLineInline(admin.TabularInline):
    model = models.OrderLine
    readonly_fields = ("product",)


class CentralOfficeOrderAdmin(admin.ModelAdmin):
    """
    Employees (aka. Central Office) need a custom version of the `order` views
    because they aren't allowed to change products that already purchased
    without adding and removing lines.
    """

    list_display = (
        "id",
        "user",
        "status",
    )
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)

    fieldsets = (
        (None, {"fields": ("user", "status",)}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_postal_code",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_postal_code",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )


class DispatchersOrderAdmin(admin.ModelAdmin):
    """
    Dispatchers do not need to see the billing address in the fields.
    """

    list_display = (
        "id",
        "shipping_name",
        "date_added",
        "status",
    )
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_postal_code",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )

    def get_queryset(self, request):
        """
        Dispatchers r only allowed to see orders that are ready to be shipped.
        """
        qs = super().get_queryset(request)
        return qs.filter(status=models.Order.PAID)


""" A form that gonna be used later """


class PeriodSelectForm(forms.Form):
    PERIODS = (
        (30, "30 days"),
        (60, "60 days"),
        (90, "90 days"),
    )
    period = forms.TypedChoiceField(choices=PERIODS, coerce=int, required=True)


""" Classes that will be used multiple times (for different roles) """


class ColoredAdminSite(admin.sites.AdminSite):
    """
    Pass a couple of values to the Django Admin templates (including our own).
    """

    def each_context(self, request):
        context = super().each_context(request)

        context["site_header_color"] = getattr(self, "site_header_color", None)
        context["module_caption_color"] = getattr(
            self, "module_caption_color", None
        )

        return context


class ReportingColoredAdminSite(ColoredAdminSite):
    """
    Add reporting views to the list of available urls and will list them from
    the index page (I don't quite understand what is "list from").
    """

    def get_urls(self):
        urls = super().get_urls()

        my_urls = [
            path(
                route="orders_per_day/",
                view=self.admin_view(self.orders_per_day),
            ),
            path(
                route="most_bought_products/",
                view=self.admin_view(self.most_bought_products),
                name="most_bought_products",
            ),
        ]

        return my_urls + urls

    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)

        # Notes on this long expression:
        # 1. Use `str(order_data`.query)` to get the actual SQL code
        # 2. TruncDay here is simply used to "chunk down" the precision :)
        # 3. The `.values` behaves just like the one for dict (a list of dicts)
        order_data = (
            models.Order.objects.filter(date_added__gt=starting_day)
            .annotate(day=TruncDay("date_added"))
            .values("day")
            .annotate(c=Count("id"))
        )

        # => labels: [ '2020-02-07' ]
        # => values: 2  (the amount of orders in THAT day)
        labels = [x["day"].strftime("%Y-%m-%d") for x in order_data]
        values = [x["c"] for x in order_data]

        context = dict(
            self.each_context(request),
            title="Orders per day",
            labels=labels,
            values=values,
        )

        return TemplateResponse(
            request=request, template="orders_per_day.html", context=context
        )

    def most_bought_products(self, request):
        if request.method == "POST":
            form = PeriodSelectForm(request.POST)

            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(days=days)

                data = (
                    models.OrderLine.objects.filter(
                        order__date_added__gt=starting_day
                    )
                    .values("product__name")
                    .annotate(c=Count("id"))
                )

                logger.info(msg=f"most_bought_products query: {data.query}")

                labels = [x["product__name"] for x in data]
                values = [x["c"] for x in data]

        else:
            form = PeriodSelectForm()
            labels = None
            values = None

        context = dict(
            self.each_context(request),
            title="Most bought products",
            form=form,
            labels=labels,
            values=values,
        )

        return TemplateResponse(
            request=request,
            template="most_bought_products.html",
            context=context,
        )

    def index(self, request, extra_context=None):
        reporting_pages = [
            {"name": "Orders per day", "link": "orders_per_day/"},
            {"name": "Most bought products", "link": "most_bought_products/"},
        ]

        if not extra_context:
            extra_context = {}
        extra_context = {"reporting_pages": reporting_pages}

        return super().index(request, extra_context)


""" Define the instances of AdminSite, each with their own perms and colors """


class OwnersAdminSite(ReportingColoredAdminSite):
    site_header = "Booktime owners administration"
    site_header_color = "black"
    module_caption_color = "grey"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


class CentralOfficeAdminSite(ReportingColoredAdminSite):
    site_header = "Booktime central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_employee


class DispatchersAdminSite(ReportingColoredAdminSite):
    site_header = "Booktime central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_dispatcher


""" Register the admin sites """


admin.site.register(models.User, UserAdmin)

main_admin = OwnersAdminSite()
central_office_admin = CentralOfficeAdminSite("central_office_admin")
dispatchers_admin = DispatchersAdminSite("dispatchers-admin")

main_admin.register(models.Product, ProductAdmin)
main_admin.register(models.ProductTag, ProductTagAdmin)
main_admin.register(models.ProductImage, ProductImageAdmin)
main_admin.register(models.User, UserAdmin)
main_admin.register(models.Address, AddressAdmin)
main_admin.register(models.Basket, BasketAdmin)
main_admin.register(models.Order, OrderAdmin)

central_office_admin.register(models.Product, ProductAdmin)
central_office_admin.register(models.ProductTag, ProductTagAdmin)
central_office_admin.register(models.ProductImage, ProductImageAdmin)
central_office_admin.register(models.Address, AddressAdmin)
central_office_admin.register(models.Order, CentralOfficeOrderAdmin)

dispatchers_admin.register(models.Product, DispatchersProductAdmin)
dispatchers_admin.register(models.ProductTag, ProductTagAdmin)
dispatchers_admin.register(models.Order, DispatchersOrderAdmin)

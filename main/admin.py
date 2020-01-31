from django.contrib import admin
from django.utils.html import format_html

from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "in_stock", "price")
    list_filter = ("active", "in_stock", "date_updated")
    list_editable = ("in_stock",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductTagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    list_filter = ("active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


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


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ProductTag, ProductTagAdmin)
admin.site.register(models.ProductImage, ProductImageAdmin)

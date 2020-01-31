from django.db import models


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class Product(models.Model):
    objects = ActiveManager()

    name = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """This model requires 'Pillow' installed first.
    """

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(upload_to="product-thumbnails", null=True)


class ProductTag(models.Model):
    products = models.ManyToManyField(to=Product, blank=True)
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

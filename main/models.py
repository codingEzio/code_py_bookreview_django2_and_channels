from django.db import models


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class ProductTagManager(models.Manager):
    """
    Accompanied with newly added 'natural_key' in class `ProductTag`.
    Both can be used for './manage.py [dumpdata|loaddata]'.
    """

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ProductTag(models.Model):
    objects = ProductTagManager()

    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class Product(models.Model):
    """
    Examples
    >> ./manage.py dumpdata --indent 2 main.ProductTag --natural-primary
    >> ./manage.py dumpdata --indent 2 main.ProductTag --output hello.json
    >> ./manage.py loaddata
    """

    objects = ActiveManager()

    name = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(to=ProductTag, blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """This model requires 'Pillow' installed first.
    """

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(upload_to="product-thumbnails", null=True)

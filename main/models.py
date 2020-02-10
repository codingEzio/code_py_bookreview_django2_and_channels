import logging

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator

from main import exceptions

logger = logging.getLogger(name=__name__)


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


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have 'is_stuff=True'")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have 'is_superuser=True'")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Changing to a custom user model SHOULD be done in the beginning.
    The reason we're ABLE to do this right now is that none of our models have
    relations to the `User` yet and the product data could be easily imported.

    Do note that all of migrations & the actual database need to be DELETED
    since it's REQUIRED when changing the `User` model.
    """

    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_employee(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Employees").exists()
        )

    @property
    def is_dispatcher(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Dispatchers").exists()
        )


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


class Address(models.Model):
    SUPPORTED_COUNTRIES = (
        ("uk", "United Kingdom"),
        ("us", "United States of America"),
    )

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address1 = models.CharField(verbose_name="Address line 1", max_length=60)
    address2 = models.CharField(
        verbose_name="Address line 2", max_length=60, blank=True
    )
    postal_code = models.CharField(verbose_name="Postal code", max_length=12)
    city = models.CharField(max_length=60)

    # How to get the actual items in the template?
    # e.g. {{ INSTANCE.get_MODELFIELD_display }}
    country = models.CharField(max_length=2, choices=SUPPORTED_COUNTRIES)

    def __str__(self):
        return ", ".join(
            [
                self.name,
                self.address1,
                self.address2,
                self.postal_code,
                self.city,
                self.country,
            ]
        )


class Basket(models.Model):
    """
    Also known as 'Shopping Cart', the cornerstone of e-commerce site.
    """

    OPEN = 10
    SUBMITTED = 20
    STATUSES = ((OPEN, "Open"), (SUBMITTED, "Submitted"))

    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, blank=True, null=True
    )
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.basketline_set.all().count == 0

    def count(self):
        return sum(bl.quantity for bl in self.basketline_set.all())

    def create_order(self, billing_address, shipping_address):
        """
        The "check out" flow:
        1. Logging info about basket and addresses
        2. Creating Order instance      (one record, mostly info)
        3. Creating OrderLine instances (multiple records, actual products)
        4. Logging info about order and the amounts of products were bought
        5. Mark the process of the "basket"'s side has end (and.. save the obj)
        """
        if not self.user:
            raise exceptions.BasketException(
                "Cannot create order without user!"
            )

        logger.info(
            f"Creating order for basket_id={self.id}, "
            f"shipping_address={shipping_address.id}, "
            f"billing_address={billing_address.id}"
        )

        order_data = {
            "user": self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_postal_code": billing_address.postal_code,
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name,
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_postal_code": shipping_address.postal_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country,
        }
        order = Order.objects.create(**order_data)

        # For the BasketLine part, we're simply inserting the records line by
        # line.
        lines_count = 0
        for basket_line in self.basketline_set.all():
            for item in range(basket_line.quantity):
                order_line_data = {
                    "order": order,
                    "product": basket_line.product,
                }
                order_line = OrderLine.objects.create(**order_line_data)
                lines_count += 1

        logger.info(
            f"Created order with id={order.id} and lines_count={lines_count}"
        )

        # Mark the process of the "basket"'s side has ended (), the actual
        # payment can be implemented in the `Order` model.
        self.status = Basket.SUBMITTED
        self.save()

        return order


class BasketLine(models.Model):
    """
    Represent specfic product and its quantity in the basket.
    """

    basket = models.ForeignKey(to=Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )


class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = (
        (NEW, "New"),
        (PAID, "Paid"),
        (DONE, "Done"),
    )

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)

    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60, blank=True)
    billing_postal_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_country = models.CharField(max_length=3)

    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True)
    shipping_postal_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_country = models.CharField(max_length=3)

    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)


class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = (
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (SENT, "Sent"),
        (CANCELLED, "Cancelled"),
    )

    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(to=Product, on_delete=models.PROTECT)

    status = models.IntegerField(choices=STATUSES, default=NEW)

from io import BytesIO
import logging
from PIL import Image

from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from .models import ProductImage, Basket

THUMBNAIL_SIZE = (300, 300)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(msg=f"Generating thumbnail for product {instance.product.id}")

    image = Image.open(instance.image)
    # image = image.convert("RGB")
    # image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    image.thumbnail(THUMBNAIL_SIZE)
    temp_thumbnail = BytesIO()
    image.save(fp=temp_thumbnail, format="JPEG")
    temp_thumbnail.seek(0)

    # Give thumbnail a bit different name
    thumbnail_name = instance.image.name.replace("jpg", "thumb.jpg")

    # Set `save=False`, otherwise it'll run in an infinite loop (quote).
    instance.thumbnail.save(
        thumbnail_name, ContentFile(temp_thumbnail.read()), save=False
    )
    temp_thumbnail.close()


@receiver(signal=user_logged_in)
def merge_baskets_if_found(sender, user, request, **kwargs):
    """
    Part of the job was done by our own middleware (basket_middleware).
    """
    anonymous_basket = getattr(request, "basket", None)
    if anonymous_basket:
        try:
            loggedin_basket = Basket.objects.get(user=user, status=Basket.OPEN)

            for basket_line in anonymous_basket.basketline_set.all():
                basket_line.basket = loggedin_basket
                basket_line.save()

            anonymous_basket.delete()
            request.basket = loggedin_basket

            logger.info(f"Merged basket to id {loggedin_basket.id}")
        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()

            logger.info(f"Assigned user to basket id {anonymous_basket.id}")

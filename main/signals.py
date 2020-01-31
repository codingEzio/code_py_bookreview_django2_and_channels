from io import BytesIO
import logging
from PIL import Image

from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import ProductImage

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

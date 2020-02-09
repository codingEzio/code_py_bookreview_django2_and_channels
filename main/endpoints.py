from rest_framework import serializers, viewsets
from . import models


# STATUS: not working
class OrderLineSerializer(serializers.HyperlinkedModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = models.OrderLine
        fields = ("id", "order", "product", "status")
        read_only_fields = ("id", "order", "product")


# STATUS: not working
class PaidOrderLineViewSet(viewsets.ModelViewSet):
    serializer_class = OrderLineSerializer
    filter_fields = ("order", "status")

    # fmt: off
    queryset = models.OrderLine.objects \
        .filter(order__status=models.Order.PAID) \
        .order_by("-order__date_added")


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Order
        fields = (
            "shipping_name",
            "shipping_address1",
            "shipping_address2",
            "shipping_postal_code",
            "shipping_city",
            "shipping_country",
            "date_updated",
            "date_added",
        )


class PaidOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    # fmt: off
    queryset = models.Order.objects \
        .filter(status=models.Order.PAID) \
        .order_by("-date_added")

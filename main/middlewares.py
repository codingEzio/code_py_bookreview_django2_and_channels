import logging
from . import models

logger = logging.getLogger(__name__)


def basket_middleware(get_response):
    """
    The original implementation provided in the book was incomplete, here's an
    improved version which is written by 'Spartak-Belov-Floresku' (the link:
    https://github.com/Spartak-Belov-Floresku/practical-django2-and-channels2).

    Some of the issues might actually caused by the browsers' cache, do clean
    it up before testing this!
    """

    def middleware(request):
        user = request.user

        if "basket_id" in request.session:
            basket_id = request.session["basket_id"]

            try:
                basket = models.Basket.objects.get(id=basket_id)
                request.basket = basket
            except Exception as err:

                try:
                    basket = models.Basket.objects.get(
                        user=user, status=models.Basket.OPEN
                    )
                    request.basket = basket
                except Exception as err:
                    del request.session["basket_id"]
        else:
            try:
                basket = models.Basket.objects.get(
                    user=user, status=models.Basket.OPEN
                )
                request.basket = basket
            except Exception as err:
                request.basket = None

        response = get_response(request)

        return response

    return middleware

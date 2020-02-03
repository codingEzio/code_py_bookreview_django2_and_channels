from . import models

__doc__ = """Modify
- requests as they come in to the views     (view)
- responses as they come out of the views   (template)"""


def basket_middleware(get_response):
    def middleware(request):
        if "basket_id" in request.session:
            basket_id = request.session["basket_id"]
            basket = models.Basket.objects.get(id=basket_id)
            request.basket = basket
        else:
            request.basket = None

        response = get_response(request)

        return response

    return middleware

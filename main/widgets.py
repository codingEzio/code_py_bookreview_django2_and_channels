from django.forms.widgets import Widget


class PlusMinusNumberInput(Widget):
    """
    A better widget for basket quantities.
    """

    template_name = "widgets/plusminusnumber.html"

    class Media:
        css = {"all": ("app_main/css/plusminusnumber.css",)}
        js = ("app_main/js/plusminusnumber.js",)

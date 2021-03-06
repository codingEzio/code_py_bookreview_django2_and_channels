import logging
from os import getenv

from django import forms
from django.forms import inlineformset_factory
from django.core.mail import send_mail
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
    UsernameField,
)
from django.contrib.auth import authenticate

from . import models
from . import widgets


logger = logging.getLogger(__name__)


# This formset is used to build forms for all basket lines that connected to
# the basket specified.
BasketLineFormSet = inlineformset_factory(
    parent_model=models.Basket,
    model=models.BasketLine,
    fields=("quantity",),
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)


class ContactForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    message = forms.CharField(max_length=600, widget=forms.Textarea)

    def send_mail(self):
        logger.info("Sending email to customer service..")

        message = (
            f"From:"
            f"{self.cleaned_data['name']}\n"
            f"{self.cleaned_data['message']}"
        )
        send_mail(
            subject="Site message",
            message=message,
            from_email=getenv("EMAIL_ADMIN"),
            recipient_list=[getenv("EMAIL_CUSTOMER_SERVICE")],
            fail_silently=False,
        )


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        """
        This inner Meta class needs to be overriden when there is a custom User
        model implemented (quote).
        """

        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info(
            f"Sending signup email for email={self.cleaned_data['email']}"
        )

        message = f"Welcome {self.cleaned_data['email']}"
        send_mail(
            subject="Welcome to Booktime",
            message=message,
            from_email=getenv("EMAIL_ADMIN"),
            recipient_list=[self.cleaned_data["email"]],
            fail_silently=True,
        )


class AuthenticationForm(forms.Form):
    """
    Templates we'll be using
    * main/templates/login.html
    * main/templates/includes/field.html (newly added to simplifying stuff)
    """

    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Add custom validation (& more) for fields by implementing this method.
        """
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(
                request=self.request, email=email, password=password
            )

            if self.user is None:
                raise forms.ValidationError(
                    "Invalid email/password combination"
                )

            logger.info(f"Authentication successful for email={email}")

        return self.cleaned_data

    def get_user(self):
        """
        I guess this method would be used by 'LoginView' in the urls.py?
        """
        return self.user


class AddressSelectionForm(forms.Form):
    # You can actually assign a queryset object to them as the "choices".
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We would receive the param `user` from the view (get_from_kwargs).
        queryset = models.Address.objects.filter(user=user)

        # The attribute `queryset` was evaluated when the form is rendered
        self.fields["billing_address"].queryset = queryset
        self.fields["shipping_address"].queryset = queryset

from io import StringIO
import tempfile

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings

from main import models


class TestImport(TestCase):
    pass

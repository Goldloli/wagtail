from django.test import TestCase
from django.utils import translation
from django.utils.functional import Promise

from wagtail.snippets.widgets import (
    AdminSnippetChooser,
    SnippetChooserAdapter,
)
from wagtail.test.testapp.models import Advert
from wagtail.test.utils import WagtailTestUtils


class TestAdminSnippetChooserWidget(WagtailTestUtils, TestCase):
    def test_adapt(self):
        widget = AdminSnippetChooser(Advert)

        js_args = SnippetChooserAdapter().js_args(widget)

        self.assertEqual(len(js_args), 3)
        self.assertInHTML(
            '<input type="hidden" name="__NAME__" id="__ID__">', js_args[0]
        )
        self.assertIn("Choose advert", js_args[0])
        self.assertEqual(js_args[1], "__ID__")

    def test_labels_stay_lazy(self):
        # https://github.com/wagtail/wagtail/issues/14709
        # Interpolating the lazy translation with % would force it into a plain
        # string using the language active at instantiation time, instead of
        # leaving it to be resolved against the current user's language at
        # render time.
        widget = AdminSnippetChooser(Advert)

        for attr in (
            "choose_one_text",
            "choose_another_text",
            "link_to_chosen_text",
        ):
            self.assertIsInstance(getattr(widget, attr), Promise)

        # Still resolve to the expected text
        self.assertEqual(widget.choose_one_text, "Choose advert")
        self.assertEqual(widget.choose_another_text, "Choose another advert")
        self.assertEqual(widget.link_to_chosen_text, "Edit this advert")

    def test_labels_resolve_in_current_language(self):
        # https://github.com/wagtail/wagtail/issues/14709
        # The labels are resolved at render time, against the active language,
        # even when the widget was instantiated under a different one.
        with translation.override("pl"):
            widget = AdminSnippetChooser(Advert)
            with translation.override("en"):
                self.assertEqual(widget.choose_one_text, "Choose advert")
            with translation.override("pl"):
                self.assertEqual(widget.choose_one_text, "Wybierz advert")

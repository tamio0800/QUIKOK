from django.test import TestCase
from account.forms import ItemForm


class ItemFormTest(TestCase):


    def test_form_renders_item_text_input(self):
        form = ItemForm()
        self.fail(form.as_p())


    def test_form_item_input_has_placeholder_and_css_classes(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item."', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())
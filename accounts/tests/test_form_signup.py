from django.test import TestCase
from ..forms import SignUpForm


class SignUpFormTest(TestCase):
    ''' 确保表单中的字段符合预期 '''
    def test_form_has_fields(self):
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'password2', ]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)

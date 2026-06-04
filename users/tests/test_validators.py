from django.test import TestCase
from django.core.exceptions import ValidationError
from users.validators import validate_phone_number



class PhoneNumberValidatorTestCase(TestCase):
    def test_valid_phone_number_passes(self):
        try:
            validate_phone_number("+201122334455")
        except ValidationError:
            self.fail("validate_phone_number raised ValidationError unexpectedly!")

    def test_invalid_phone_numbers_raise_error(self):
        invalid_cases = [
            "+2011223344556677889900", # long
            "+2010",                   # short
            "0201122334455",           # start without +
            "+20112233xx55"            # contain chars
        ]

        for number in invalid_cases:
            with self.subTest(number=number):
                with self.assertRaises(ValidationError) as context:
                    validate_phone_number(number)
                self.assertEqual(context.exception.message, 
                                "Phone number must start with + and contain exactly 12 digits after it.")
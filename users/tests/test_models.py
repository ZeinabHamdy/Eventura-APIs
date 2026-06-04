from django.test import TestCase 
from users.models import User



class UserModelTestCase(TestCase):
    def test_email_is_lowercased_on_save(self):
        user = User.objects.create_user(
            email = "ZeINAB@EvenTura.COM",
            password = "Zeinab1234",
            name = "Zeinab"
        )
        user.refresh_from_db()
        self.assertEqual(user.email, "zeinab@eventura.com")


class UserManagerTestCase(TestCase):
    def test_create_user_successfully(self):
        original_password = "Zeinab1234"
        user = User.objects.create_user(
            email = "Zeinab@Eventura.com",
            password = original_password,
            name = "Zeinab"
        )
        self.assertEqual(User.objects.count(), 1) # check if it saved on db
        self.assertNotEqual(user.password, original_password)
        self.assertTrue(user.check_password(original_password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser_successfully(self):
        original_password = "Zeinab1234"
        user = User.objects.create_superuser(
            email = "Zeinab@Eventura.com",
            password = original_password,
            name = 'Zeinab'
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertNotEqual(user.password, original_password)
        self.assertTrue(user.check_password(original_password))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
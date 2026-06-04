from django.test import TestCase
from rest_framework.test import APIRequestFactory

from users.models import User
from users.serializers import(
    CustomTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)



class UserRegisterSerializerTestCase(TestCase):
    def test_register_with_valid_data(self):
        data  = {
            "email" : "Zeinab@eventura.com",
            "password" : "Zeinab1234",
            "password2" : "Zeinab1234",
            "name" : "Zeinab",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, "zeinab@eventura.com")  # type: ignore
    
    def test_register_with_password_mismatch(self):
        data  = {
            "email" : "Zeinab@eventura.com",
            "password" : "Zeinab1234",
            "password2" : "Zeinab123456",
            "name" : "Zeinab",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertEqual(serializer.errors["password"][0], "Passwords do not match.")  # type: ignore


class UserProfileSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name = "Zeinab",
            email = "Zeinab@eventura.com",
            password = "Zeinab1234",
            phone_number = "+201122334455"
        )

    def test_profile_serialization_output(self): 
        serializer = UserProfileSerializer(instance = self.user)
        self.assertEqual(serializer.data["name"], "Zeinab")  # type: ignore
        self.assertEqual(serializer.data["email"], "zeinab@eventura.com")  # type: ignore
        self.assertEqual(serializer.data["phone_number"], "+201122334455")  # type: ignore
        self.assertNotIn("password", serializer.data)

    def test_email_is_read_only(self):
        data = {"name": "Updated Name", "email": "hacker@eventura.com"}
        serializer = UserProfileSerializer(instance = self.user, data=data, partial=True) 
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated Name")
        self.assertEqual(self.user.email, "zeinab@eventura.com") # not change in email


class ChangePasswordSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name = "Zeinab",
            email = "Zeinab@eventura.com",
            password = "Zeinab1234",
            phone_number = "+201122334455"
        )
        factory = APIRequestFactory()
        self.request = factory.put('/dummy-url/')
        self.request.user = self.user 


    def test_change_password_successfully(self):
        data = {
            "old_password": "Zeinab1234",
            "new_password": "Zeinab12345678",
            "new_password2": "Zeinab12345678"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self.request})
        self.assertTrue(serializer.is_valid())

    def test_old_password_invalid(self):
        data = {
            "old_password": "OLDPASSWORD",
            "new_password": "Zeinab12345678",
            "new_password2": "Zeinab12345678"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)
        self.assertEqual(serializer.errors["old_password"][0], "Old password is incorrect.") # type: ignore


class CustomTokenObtainPairSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Zeinab",
            email="zeinab@eventura.com",
            password="Zeinab1234",
            is_active=True,
            phone_number="+201122334455"
        )

    def test_email_is_lowercased_before_validation(self):
        data = {
            "email": "ZeiNaB@EvEnTuRa.CoM",
            "password": "Zeinab1234"
        }
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn("access", serializer.validated_data) # type: ignore
        self.assertIn("refresh", serializer.validated_data) # type: ignore


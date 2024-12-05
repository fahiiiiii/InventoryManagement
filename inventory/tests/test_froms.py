from django.test import TestCase
from inventory.forms import AccommodationForm, PropertyOwnerSignUpForm
from inventory.models import Location
from django.contrib.auth.models import User


class AccommodationFormTest(TestCase):

    def test_accommodation_form_valid(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center="POINT(40.7128 -74.0060)",
        )

        form_data = {
            "title": "Test Property",
            "country_code": "US",
            "bedroom_count": 2,
            "review_score": 4.5,
            "usd_rate": 100.00,
            "center": "POINT(40.7128 -74.0060)",  # Geospatial data
            "location": location.id,
            "published": True,
        }
        form = AccommodationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_accommodation_form_invalid_data(self):
        form_data = {
            "title": "",  # Invalid: title is required
            "country_code": "US",
            "bedroom_count": 2,
            "review_score": 4.5,
            "usd_rate": 100.00,
            "center": "POINT(40.7128 -74.0060)",
            "location": "1",
            "published": True,
        }
        form = AccommodationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class PropertyOwnerSignUpFormTest(TestCase):

    def test_signup_form_valid(self):
        form_data = {
            "username": "newuser",
            "email": "user@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
            "phone": "1234567890",
            "location": "New York",
        }
        form = PropertyOwnerSignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_signup_form_invalid_passwords(self):
        form_data = {
            "username": "newuser",
            "email": "user@example.com",
            "password1": "securepassword123",
            "password2": "differentpassword123",
            "phone": "1234567890",
            "location": "New York",
        }
        form = PropertyOwnerSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_form_invalid_phone(self):
        form_data = {
            "username": "newuser",
            "email": "user@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
            "phone": "not_a_number",
            "location": "New York",
        }
        form = PropertyOwnerSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

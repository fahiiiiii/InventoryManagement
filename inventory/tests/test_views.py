from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import Point
from inventory.models import Location, Accommodation
from django.core.files.uploadedfile import SimpleUploadedFile


class ViewsTest(TestCase):

    def setUp(self):
        """Set up users and initial data for the tests."""
        # Create superuser (admin)
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.property_owner_user = User.objects.create_user(
            username="owner", password="password", email="owner@example.com"
        )
        property_owner_group = Group.objects.create(name="Property Owners")
        self.property_owner_user.groups.add(property_owner_group)

        # Create Location
        self.location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(-74.0060, 40.7128),
        )

    def test_property_owner_signup(self):
        """Test property owner signup functionality."""
        response = self.client.post(
            reverse("property_owner_signup"),
            {
                "username": "newowner",
                "email": "newowner@example.com",
                "password1": "password123",
                "password2": "password123",
                "phone": "1234567890",
                "location": "New York",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after signup
        self.assertTrue(User.objects.filter(username="newowner").exists())

    def test_property_owner_signup_invalid_password(self):
        """Test invalid property owner signup with mismatched passwords."""
        response = self.client.post(
            reverse("property_owner_signup"),
            {
                "username": "newowner",
                "email": "newowner@example.com",
                "password1": "password123",
                "password2": "password456",
                "phone": "1234567890",
                "location": "New York",
            },
        )
        self.assertFormError(response, "form", "password2", "Passwords do not match")

    def test_property_owner_add_property(self):
        """Test if property owner can add a property."""
        self.client.login(username="owner", password="password")
        response = self.client.post(
            reverse("add_property"),
            {
                "title": "Owner Property",
                "country_code": "US",
                "bedroom_count": 2,
                "review_score": 4.5,
                "usd_rate": 150.00,
                "center": "POINT(40.7128 -74.0060)",
                "location": self.location.id,
                "published": True,
            },
        )
        self.assertRedirects(
            response, reverse("property_list")
        )  # After creation, redirect to property list
        self.assertEqual(
            Accommodation.objects.count(), 1
        )  # Ensure property was created

    def test_property_owner_update_property(self):
        """Test if property owner can update their property."""
        self.client.login(username="owner", password="password")

        # Create property for the owner
        accommodation = Accommodation.objects.create(
            id="1",
            title="Old Property",
            country_code="US",
            bedroom_count=2,
            review_score=3.0,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",
            location=self.location,
            user=self.property_owner_user,
            published=True,
        )

        # Update property data
        response = self.client.post(
            reverse("update_property", args=[accommodation.id]),
            {
                "title": "Updated Property",
                "country_code": "US",
                "bedroom_count": 3,
                "review_score": 5.0,
                "usd_rate": 200.00,
                "center": "POINT(40.7128 -74.0060)",
                "location": self.location.id,
                "published": True,
            },
        )
        self.assertRedirects(
            response, reverse("property_list")
        )  # After updating, redirect to property list
        accommodation.refresh_from_db()
        self.assertEqual(accommodation.title, "Updated Property")  # Verify the update

    def test_property_owner_delete_property(self):
        """Test if property owner can delete their property."""
        self.client.login(username="owner", password="password")

        # Create property for the owner
        accommodation = Accommodation.objects.create(
            id="1",
            title="Property to Delete",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=150.00,
            center="POINT(40.7128 -74.0060)",
            location=self.location,
            user=self.property_owner_user,
            published=True,
        )

        # Ensure property exists
        self.assertEqual(Accommodation.objects.count(), 1)

        # Delete the property
        response = self.client.post(reverse("delete_property", args=[accommodation.id]))
        self.assertEqual(Accommodation.objects.count(), 0)  # Property should be deleted
        self.assertRedirects(
            response, reverse("property_list")
        )  # Redirect after deletion

    def test_property_owner_access_own_properties(self):
        """Test that property owners can only see their own properties."""
        self.client.login(username="owner", password="password")

        # Create property for the owner
        accommodation = Accommodation.objects.create(
            id="1",
            title="Owner's Property",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=150.00,
            center="POINT(40.7128 -74.0060)",
            location=self.location,
            user=self.property_owner_user,
            published=True,
        )

        # Ensure property owner only sees their own property
        response = self.client.get(reverse("property_list"))
        self.assertContains(response, "Owner's Property")
        self.assertNotContains(
            response, "Admin Property"
        )  # Admin Property should not be visible to the property owner

    def test_property_list_for_logged_in_user(self):
        """Test property list for logged-in users."""
        self.client.login(username="owner", password="password")

        # Create property for the logged-in user
        accommodation = Accommodation.objects.create(
            id="1",
            title="User's Property",
            country_code="US",
            bedroom_count=2,
            review_score=4.0,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",
            location=self.location,
            user=self.property_owner_user,
            published=True,
        )

        response = self.client.get(reverse("property_list"))
        self.assertContains(
            response, "User's Property"
        )  # Ensure the property is listed

    def test_import_csv_view(self):
        """Test the custom CSV import view for Location model."""
        self.client.login(username="admin", password="password")

        # Make sure the custom import CSV view is accessible
        response = self.client.get(reverse("admin:location_import_csv"))
        self.assertEqual(response.status_code, 200)

        # Prepare a mock CSV file (we'll simulate the file upload in the test)
        csv_data = "title,country_code,location_type,center\nTest Location,US,Country,POINT(40.7128 -74.0060)"
        csv_file = SimpleUploadedFile("locations.csv", csv_data.encode("utf-8"))

        # POST the file data to the view
        response = self.client.post(
            reverse("admin:location_import_csv"), {"csv_file": csv_file}
        )

        # Verify successful import message
        self.assertContains(response, "CSV imported successfully.")

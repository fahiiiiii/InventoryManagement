from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.contrib import admin
from inventory.models import Location, Accommodation
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError


class AdminTest(TestCase):

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

    def test_admin_can_create_property(self):
        """Test if admin can create properties through the admin interface."""
        self.client.login(username="admin", password="password")

        # Access the add property page
        response = self.client.get(reverse("admin:inventory_accommodation_add"))
        self.assertEqual(response.status_code, 200)

        # Post data to create a new accommodation
        response = self.client.post(
            reverse("admin:inventory_accommodation_add"),
            {
                "title": "Admin Property",
                "country_code": "US",
                "bedroom_count": 2,
                "review_score": 4.5,
                "usd_rate": 150.00,
                "center": "POINT(40.7128 -74.0060)",
                "location": self.location.id,
                "published": True,
            },
        )
        # Ensure it redirects after creation
        self.assertRedirects(
            response, reverse("admin:inventory_accommodation_changelist")
        )

    def test_admin_can_update_property(self):
        """Test if admin can update a property."""
        self.client.login(username="admin", password="password")

        # Create a sample accommodation
        accommodation = Accommodation.objects.create(
            id="1",
            title="Old Property",
            country_code="US",
            bedroom_count=2,
            review_score=3.0,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",
            location=self.location,
            user=self.admin_user,
            published=True,
        )

        # Access the property change page
        response = self.client.get(
            reverse("admin:inventory_accommodation_change", args=[accommodation.id])
        )
        self.assertEqual(response.status_code, 200)

        # Update property data
        response = self.client.post(
            reverse("admin:inventory_accommodation_change", args=[accommodation.id]),
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
        # Check if it redirects after updating
        self.assertRedirects(
            response, reverse("admin:inventory_accommodation_changelist")
        )

    def test_admin_can_delete_property(self):
        """Test if admin can delete properties."""
        self.client.login(username="admin", password="password")

        # Create a property
        accommodation = Accommodation.objects.create(
            id="1",
            title="Property to Delete",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=150.00,
            center="POINT(40.7128 -74.0060)",
            location=self.location,
            user=self.admin_user,
            published=True,
        )

        # Check that property exists
        self.assertEqual(Accommodation.objects.count(), 1)

        # Access the delete page for the property
        response = self.client.post(
            reverse("admin:inventory_accommodation_delete", args=[accommodation.id])
        )
        # Ensure the property is deleted
        self.assertEqual(Accommodation.objects.count(), 0)
        self.assertRedirects(
            response, reverse("admin:inventory_accommodation_changelist")
        )

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

    def test_custom_admin_permissions_for_property_owner(self):
        """Test custom admin permissions: Property Owners can only see their own properties."""
        self.client.login(username="owner", password="password")

        # Create property for property owner
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

        # Ensure property owner only sees their own property in the list
        response = self.client.get(reverse("admin:inventory_accommodation_changelist"))
        self.assertContains(response, "Owner's Property")
        self.assertNotContains(
            response, "Admin Property"
        )  # Admin Property should not be visible to the property owner

    def test_admin_can_view_and_edit_locations(self):
        """Test if admin can view and edit locations."""
        self.client.login(username="admin", password="password")

        # Create a location
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center="POINT(40.7128 -74.0060)",
        )

        # Ensure admin can view the location
        response = self.client.get(
            reverse("admin:inventory_location_change", args=[location.id])
        )
        self.assertEqual(response.status_code, 200)

        # Update location
        response = self.client.post(
            reverse("admin:inventory_location_change", args=[location.id]),
            {
                "title": "Updated Location",
                "country_code": "US",
                "location_type": "State",
                "center": "POINT(40.7128 -74.0060)",
            },
        )
        self.assertRedirects(response, reverse("admin:inventory_location_changelist"))

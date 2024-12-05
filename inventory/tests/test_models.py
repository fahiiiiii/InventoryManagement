from django.test import TestCase
from django.contrib.auth.models import User
from inventory.models import Location, Accommodation, LocalizeAccommodation
from django.contrib.gis.geos import Point


class LocationModelTest(TestCase):

    def test_location_creation(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(
                -74.0060, 40.7128
            ),  # Example geospatial data (Longitude, Latitude)
        )
        self.assertEqual(location.title, "Test Location")
        self.assertEqual(location.country_code, "US")
        self.assertEqual(location.location_type, "Country")
        self.assertTrue(
            isinstance(location.center, Point)
        )  # Check if center is a valid Point

    def test_location_missing_fields(self):
        # Test missing fields during location creation
        with self.assertRaises(ValueError):
            Location.objects.create(
                id="2",
                title="Test Location Without Country Code",
                location_type="Country",
                center=Point(-74.0060, 40.7128),
            )


class AccommodationModelTest(TestCase):

    def test_accommodation_creation(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(-74.0060, 40.7128),
        )

        accommodation = Accommodation.objects.create(
            id="1",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",  # Geolocation in WKT format
            location=location,
            user=None,  # You can assign a user if needed
            published=True,
        )

        self.assertEqual(accommodation.title, "Test Accommodation")
        self.assertEqual(accommodation.bedroom_count, 2)
        self.assertEqual(accommodation.review_score, 4.5)
        self.assertEqual(accommodation.usd_rate, 100.00)
        self.assertTrue(accommodation.published)

    def test_accommodation_missing_data(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(-74.0060, 40.7128),
        )

        # Test missing review_score and usd_rate, these should be handled by default
        accommodation = Accommodation.objects.create(
            id="2",
            title="Property Without Price",
            country_code="US",
            bedroom_count=2,
            center="POINT(40.7128 -74.0060)",
            location=location,
            user=None,
            published=True,
        )

        self.assertEqual(accommodation.review_score, 0)  # Default review score
        self.assertEqual(accommodation.usd_rate, None)  # No USD rate set

    def test_accommodation_update(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(-74.0060, 40.7128),
        )

        accommodation = Accommodation.objects.create(
            id="1",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",
            location=location,
            user=None,
            published=True,
        )

        accommodation.title = "Updated Property Title"
        accommodation.save()
        updated_accommodation = Accommodation.objects.get(id="1")

        self.assertEqual(updated_accommodation.title, "Updated Property Title")


class LocalizeAccommodationModelTest(TestCase):

    def test_localize_accommodation_creation(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(-74.0060, 40.7128),
        )

        accommodation = Accommodation.objects.create(
            id="1",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",
            location=location,
            user=None,
            published=True,
        )

        localize = LocalizeAccommodation.objects.create(
            property=accommodation,
            language="en",
            description="English description",
            policy={"pet_policy": "Allowed"},
        )

        self.assertEqual(localize.language, "en")
        self.assertEqual(localize.description, "English description")
        self.assertTrue("pet_policy" in localize.policy)

    def test_unique_localize_accommodation(self):
        location = Location.objects.create(
            id="1",
            title="Test Location",
            country_code="US",
            location_type="Country",
            center=Point(-74.0060, 40.7128),
        )

        accommodation = Accommodation.objects.create(
            id="1",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=100.00,
            center="POINT(40.7128 -74.0060)",
            location=location,
            user=None,
            published=True,
        )

        LocalizeAccommodation.objects.create(
            property=accommodation,
            language="en",
            description="English description",
            policy={"pet_policy": "Allowed"},
        )

        with self.assertRaises(
            Exception
        ):  # Trying to insert the same language for the same property
            LocalizeAccommodation.objects.create(
                property=accommodation,
                language="en",
                description="Duplicate English description",
                policy={"pet_policy": "Not Allowed"},
            )

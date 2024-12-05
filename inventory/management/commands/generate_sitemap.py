import json
from django.core.management.base import BaseCommand
from inventory.models import Location  # Corrected import path
from django.utils.text import slugify
from collections import defaultdict

class Command(BaseCommand):
    help = 'Generates a sitemap.json file for all country locations grouped by country code.'

    def handle(self, *args, **kwargs):
        # Initialize a dictionary to store locations by country code
        country_locations = defaultdict(list)

        # Load locations from the database based on your fixtures
        locations = Location.objects.all().order_by('country_code', 'title')

        # Group locations by country code
        for location in locations:
            # Use 3 uppercase letters for the country code
            country_code_slug = location.country_code.upper()[:3]  # First 3 letters in uppercase

            # Create the location slug (lowercase and hyphenated)
            location_slug = slugify(location.title)

            # Create the location URL in the format: "country_code/location_slug"
            location_url = f"{country_code_slug.lower()}/{location_slug}"

            # Add the location to the list for the given country code
            country_locations[location.country_code].append(
                {location.title: location_url}  # Each location in its own dictionary
            )

        # Build the sitemap structure
        sitemap = []

        for country_code, locations in country_locations.items():
            country_data = {
                country_code.upper(): country_code.lower(),  # Country code as 3 uppercase letters and slug as lowercase
                "locations": locations  # List of locations (each in its own dictionary)
            }
            sitemap.append(country_data)

        # Sort the countries alphabetically by country code
        sitemap = sorted(sitemap, key=lambda x: list(x.keys())[0])

        # Output the sitemap to a JSON file
        with open('sitemap.json', 'w') as f:
            json.dump(sitemap, f, indent=4)

        self.stdout.write(self.style.SUCCESS('Successfully generated sitemap.json'))

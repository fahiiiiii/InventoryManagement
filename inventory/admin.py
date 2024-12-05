import csv
from django.contrib.auth.models import Group
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ExportMixin
from .models import Location, Accommodation, LocalizeAccommodation
from django.contrib import admin, messages
from django.urls import path, reverse
from django.core.exceptions import ValidationError


# Define a resource for Location model
class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = ("id", "title", "country_code", "location_type", "parent", "center")


@admin.register(Location)
class LocationAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "country_code",
        "location_type",
        "parent",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "country_code", "city")
    list_filter = ("location_type", "country_code")
    resource_class = LocationResource

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv),
                name="location_import_csv",
            ),
        ]
        return custom_urls + urls

    def import_csv_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Import CSV</a>',
            reverse("admin:location_import_csv"),
        )

    import_csv_button.short_description = "Import CSV"

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions["import_csv"] = (self.import_csv, "import_csv", "Import CSV")
        return actions

    def import_csv(self, request):
        from django.contrib import messages
        from django.shortcuts import render, redirect
        from django.contrib.gis.geos import Point
        import csv

        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")

            if not csv_file or not csv_file.name.endswith(".csv"):
                self.message_user(
                    request,
                    "Invalid file format. Please upload a .csv file.",
                    level=messages.ERROR,
                )
                return redirect("..")

            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)

                for row in reader:
                    title = row.get("title")
                    country_code = row.get("country_code")
                    location_type = row.get("location_type", "")
                    parent_id = row.get("parent", None)
                    center = row.get("center")

                    if not all([title, country_code, center]):
                        continue  # Skip rows with missing data

                    # Convert center to Point (longitude, latitude)
                    try:
                        longitude, latitude = map(
                            float, center.strip("POINT()").split()
                        )
                        location_point = Point(longitude, latitude)
                    except (ValueError, TypeError):
                        continue  # Skip rows with invalid center data

                    # Create or update Location object
                    Location.objects.update_or_create(
                        title=title,
                        country_code=country_code,
                        defaults={
                            "location_type": location_type,
                            "parent_id": parent_id,
                            "center": location_point,
                        },
                    )

                self.message_user(
                    request, "CSV imported successfully.", level=messages.SUCCESS
                )
                return redirect("..")

            except Exception as e:
                self.message_user(
                    request, f"Error importing CSV: {str(e)}", level=messages.ERROR
                )
                return redirect("..")

        # Render upload form
        return render(request, "admin/csv_upload.html")



# Custom admin for Accommodation
@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "country_code",
        "bedroom_count",
        "review_score",
        "usd_rate",
        "published",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "country_code")
    list_filter = ("country_code", "published", "bedroom_count")

    # Make non-editable fields read-only
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",  # Displayed as read-only
                    "feed",
                    "title",
                    "country_code",
                    "bedroom_count",
                    "review_score",
                    "usd_rate",
                    "center",
                    "published",
                )
            },
        ),
        (
            "Images and Amenities",
            {
                "fields": ("images", "amenities"),
                "classes": ("collapse",),
            },
        ),
        (
            "Location and User",
            {
                "fields": ("location", "user"),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Only return accommodations for the logged-in user unless the user is a superuser.
        Superusers should be able to see all properties, while admin users can only see their own properties.
        """
        queryset = super().get_queryset(request)

        # If the user is a superuser (admin), show all properties
        if request.user.is_superuser:
            return queryset
        elif request.user.is_staff:
            # Admins can only see their own properties
            return queryset.filter(user=request.user)
        
        # Non-staff users (Property Owners) can only see their own properties
        return queryset.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        """
        If the user is a superuser, assign them as the user for all properties created by others.
        Otherwise, associate the logged-in user with the property.
        """
        if request.user.is_superuser:
            # Allow superuser to create properties under their own account
            obj.user = request.user
        elif request.user.is_staff:
            # Staff members should be able to see and manage only their properties
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        """
        Allow superusers to delete any property.
        Staff members (admins) can only delete their own properties.
        """
        if request.user.is_superuser:
            return True  # Superusers can delete any property
        if obj and obj.user == request.user:
            return True  # Admin can delete only their own property
        return False  # Admin can't delete other admin properties

    def has_change_permission(self, request, obj=None):
        """
        Allow superusers to change any property.
        Staff members (admins) can only edit their own properties.
        """
        if request.user.is_superuser:
            return True  # Superusers can edit any property
        if obj and obj.user == request.user:
            return True  # Admin can edit only their own property
        return False  # Admin can't edit other admin properties

    def has_view_permission(self, request, obj=None):
        """
        Allow superusers to view any property.
        Staff members (admins) can only view their own properties.
        """
        if request.user.is_superuser:
            return True  # Superusers can view any property
        if obj and obj.user == request.user:
            return True  # Admin can view only their own property
        return False  # Admin can't view other admin properties



# Custom admin for LocalizeAccommodation
@admin.register(LocalizeAccommodation)
class LocalizeAccommodationAdmin(admin.ModelAdmin):
    list_display = ("property", "language", "description")
    search_fields = ("property__title", "language")
    list_filter = ("language",)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "show_users")

    def show_users(self, obj):
        url = f"/admin/auth/group/{obj.id}/users/"
        return format_html('<a href="{}">View Users</a>', url)

    show_users.short_description = "Users"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:group_id>/users/",
                self.admin_site.admin_view(self.view_group_users),
                name="group_users",
            ),
        ]
        return custom_urls + urls

    def view_group_users(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        users = group.user_set.all()
        context = {
            "group": group,
            "users": users,
        }
        return render(request, "admin/group_users.html", context)


# Unregister and re-register Group with the custom GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

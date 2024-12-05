from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Accommodation, Location
from .forms import AccommodationForm, PropertyOwnerSignUpForm
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.files.storage import default_storage
import os
import uuid

# views.py
from django.shortcuts import render
from .models import Location

import uuid
from django.shortcuts import render, redirect, get_object_or_404  # type: ignore
from .forms import AccommodationForm
from django.contrib.auth.decorators import login_required  # type: ignore
from .models import Accommodation  # Assuming Accommodation is the model
from django.contrib import messages  # type: ignore
from django.contrib.auth.models import User, Group  # type: ignore
from django.contrib.auth.views import LoginView  # type: ignore
import os
import uuid
from django.conf import settings  # type: ignore
from django.core.files.uploadedfile import InMemoryUploadedFile  # type: ignore
from django.core.files.storage import default_storage  # type: ignore
from django.core.files.base import ContentFile  # type: ignore
from .forms import PropertyOwnerSignUpForm

import json


@login_required
def add_property(request):
    if request.method == "POST":
        form = AccommodationForm(
            request.POST, request.FILES
        )  # Include request.FILES for file uploads
        if form.is_valid():
            # Save the property with the logged-in user
            accommodation = form.save(commit=False)
            # accommodation.id = generate_unique_id()  # Generate the unique ID
            accommodation.user = (
                request.user
            )  # Associate property with the logged-in user
            accommodation.save()
            return redirect("property_list")  # Redirect to the property list view
        else:
            messages.error(
                request, "There was an error with your form."
            )  # Display a form error
    else:
        form = AccommodationForm()

    return render(request, "add_property.html", {"form": form})


def handle_uploaded_image(image):
    """
    Handles uploading and saving an image file
    """
    ext = os.path.splitext(image.name)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join("property_images", filename)
    saved_path = default_storage.save(filepath, image)
    return saved_path


import os
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from .forms import AccommodationForm
from .models import Accommodation


@login_required
def update_property(request, pk):
    property = get_object_or_404(
        Accommodation, pk=pk
    )  # Get the property instance safely
    if property.user != request.user:
        messages.error(
            request, "You do not have permission to edit this property."
        )  # Permission check
        return redirect(
            "property_list"
        )  # Redirect if the user is not the owner of the property

    if request.method == "POST":
        form = AccommodationForm(
            request.POST, request.FILES, instance=property
        )  # Bind form with the existing object

        if form.is_valid():
            # Save the property with the logged-in user
            accommodation = form.save(commit=False)
            # accommodation.id = generate_unique_id()  # Generate the unique ID
            accommodation.user = (
                request.user
            )  # Associate property with the logged-in user
            accommodation.save()
            return redirect("property_list")
        # if form.is_valid():
        #     print(form.cleaned_data)  # Add this to check the submitted form data
        #     form.save()
        #     messages.success(request, "Property  successfully!")
        #     return redirect('property_list')
        else:
            messages.error(
                request, "There was an error with your form."
            )  # Display form error message
    else:
        form = AccommodationForm(
            instance=property
        )  # Prepopulate the form with existing data

    return render(
        request, "update_property.html", {"form": form}
    )  # Render the form to the template


# @login_required
# def property_list(request):
#     properties = Accommodation.objects.filter(user=request.user)
#     return render(request, 'property_list.html', {'properties': properties})


@login_required
def property_list(request):
    properties = Accommodation.objects.filter(
        user=request.user
    )  # Only the user's properties

    # Check if the user is a staff (admin) or has specific permissions
    is_admin = request.user.is_staff
    can_create = is_admin  # Staff can create, update, and delete properties
    can_update = is_admin
    can_delete = is_admin

    return render(
        request,
        "property_list.html",
        {
            "properties": properties,
            "can_create": can_create,
            "can_update": can_update,
            "can_delete": can_delete,
        },
    )


@login_required
def delete_property(request, pk):
    property = get_object_or_404(Accommodation, pk=pk)

    if property.user != request.user:  # Ensure the logged-in user is the owner
        messages.error(request, "You do not have permission to delete this property.")
        return redirect("property_list")

    property.delete()  # Delete the property if the user is the owner
    messages.success(request, "Property deleted successfully!")
    return redirect("property_list")


def property_owner_signup(request):
    if request.method == "POST":
        form = PropertyOwnerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.set_password(form.cleaned_data["password1"])  # Encrypt the password
            user.save()  # Now save the user object
            property_owner_group = Group.objects.get(name="Property Owners")
            user.groups.add(property_owner_group)
            messages.success(
                request, "Sign-up successful! Your request will be reviewed shortly."
            )
            return redirect("login")  # Redirect to login page after successful sign-up
        else:
            messages.error(request, "There was an error with your sign-up request.")
    else:
        form = PropertyOwnerSignUpForm()

    return render(request, "property_owner_signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "login.html"  # Specify the template you want to use for login


def users_in_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    users = group.user_set.all()
    return render(request, "admin/group_users.html", {"group": group, "users": users})


def location_detail(request, location_slug):
    location = Location.objects.get(slug=location_slug)
    return render(request, "location_detail.html", {"location": location})


import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.gis.geos import Point
from .models import Location


def import_csv(self, request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        # Validate file type
        if not csv_file.name.endswith(".csv"):
            self.message_user(
                request,
                "Invalid file format. Please upload a .csv file.",
                level=messages.ERROR,
            )
            return redirect("..")

        try:
            # Read and decode the CSV file
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # Extract data from each row
                title = row.get("title")
                country_code = row.get("country_code")
                location_type = row.get("location_type", "")
                parent_id = row.get("parent", None)
                center = row.get("center")

                # Validate required fields
                if not title or not country_code or not center:
                    raise ValidationError(
                        "Missing required fields in CSV: title, country_code, or center."
                    )

                # Convert center to Point (longitude, latitude)
                longitude, latitude = map(float, center.strip("POINT()").split())
                location_point = Point(longitude, latitude)

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
                request, f"Error importing CSV: {e}", level=messages.ERROR
            )

    # Render upload form
    return render(request, "admin/csv_upload.html")

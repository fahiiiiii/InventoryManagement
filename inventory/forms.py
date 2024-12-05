
from django import forms # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.core.exceptions import ValidationError # type: ignore
from django.core.validators import MinValueValidator, MaxValueValidator # type: ignore
from django.contrib.gis.forms import PointField # type: ignore

from .models import Accommodation, LocalizeAccommodation, Location

class BasePropertyForm(forms.ModelForm):
    """
    Base form for property-related models with common validations
    """
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        help_text="Upload property images (max 5MB per image)"
    )

    def clean_images(self):
        """
        Validate uploaded images
        """
        images = self.files.getlist('images')
        if images:
            for img in images:
                # 5MB file size limit
                if img.size > 5 * 1024 * 1024:  
                    raise ValidationError(f"Image {img.name} exceeds 5MB size limit")
        return images

    def clean_review_score(self):
        """
        Validate review score is between 0 and 5
        """
        review_score = self.cleaned_data.get('review_score')
        if review_score is not None and (review_score < 0 or review_score > 5):
            raise ValidationError("Review score must be between 0 and 5")
        return review_score

    def clean_bedroom_count(self):
        """
        Validate bedroom count is between 1 and 20
        """
        bedroom_count = self.cleaned_data.get('bedroom_count')
        if bedroom_count is not None and (bedroom_count < 1 or bedroom_count > 20):
            raise ValidationError("Bedroom count must be between 1 and 20")
        return bedroom_count

class PropertyForm(BasePropertyForm):
    """
    Form for Property model with enhanced validations
    """
    class Meta:
        model = Accommodation
        fields = [
            'feed', 'title', 'country_code', 'bedroom_count', 
            'review_score', 'usd_rate', 'center', 'images', 
            'location', 'amenities', 'published'
        ]

class AccommodationForm(forms.ModelForm):
    # Add an additional constructor to accept the request object
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Accept the request object
        super().__init__(*args, **kwargs)

    class Meta:
        model = Accommodation
        fields = ['id', 'title', 'country_code', 'bedroom_count', 'review_score', 'usd_rate', 'center', 'images', 'location', 'amenities']
        exclude = ['id']
    def save(self, commit=True):
        accommodation = super().save(commit=False)
        if commit and self.request:
            accommodation.user = self.request.user  # Set the user to the currently logged-in user
            accommodation.save()
        return accommodation
class PropertyOwnerSignUpForm(forms.ModelForm):
    """
    Registration form for property owners with comprehensive validation
    """
    password1 = forms.CharField(
        widget=forms.PasswordInput(), 
        label="Password", 
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(), 
        label="Confirm Password"
    )
    phone = forms.CharField(
        max_length=15,
        label="Phone Number",
        help_text="Numeric phone number"
    )
    location = forms.CharField(
        max_length=100,
        label="Location"
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        """
        Validate password confirmation
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        return password2

    def clean_phone(self):
        """
        Validate phone number is numeric
        """
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit():
            raise ValidationError("Phone number must contain only digits")
        return phone

    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use")
        return email

    def save(self, commit=True):
        """
        Create user with hashed password
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
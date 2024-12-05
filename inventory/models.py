from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.contrib.gis.db import models
import uuid
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.gis.db import models
# from .models import Accommodation  # or the correct path if it's in another file

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.gis.db import models as gis_models



# Location model (if it doesn't exist already)
from django.db import models
from django.contrib.gis.db import models as gis_models



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.contrib.gis.db import models as gis_models
import uuid
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models as gis_models
from django.utils.text import slugify

class Location(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    # id = models.CharField(max_length=20, primary_key=True, default=lambda: str(uuid.uuid4())[:20], editable=False)
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=100)
    # slug = models.SlugField(unique=True, blank=True)  # Add this field
    # slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    center = gis_models.PointField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    location_type = models.CharField(max_length=20)
    country_code = models.CharField(max_length=2)
    state_abbr = models.CharField(max_length=3, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # def save(self, *args, **kwargs):
    #     if not self.slug:  # Automatically generate the slug from the title if it is blank
    #         self.slug = slugify(self.title)
    #     super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return self.title



class Accommodation(models.Model):
    # ID with UUID default
    # id = models.CharField(max_length=20, primary_key=True, default=lambda: str(uuid.uuid4())[:20], editable=False)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField(max_length=20, primary_key=True, default=lambda: str(uuid.uuid4())[:20], editable=False)

    feed = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    # bedroom_count = models.PositiveIntegerField()
    bedroom_count = models.PositiveIntegerField(null=True, blank=True)
    review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    center = models.CharField(max_length=255)  # Placeholder for PostGIS point
    images = models.JSONField(default=list)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    amenities = models.JSONField(default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())[:20]  # Generate a truncated UUID as id if not set
        if not self.created_at:
            self.created_at = timezone.now()  # Ensure created_at is set if not present
        super().save(*args, **kwargs)

class LocalizeAccommodation(models.Model):
    id = models.AutoField(primary_key=True)
    # property = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    property = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    language = models.CharField(max_length=2)
    description = models.TextField(blank=True, null=True)
    policy = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'language'], name='unique_localization_per_language')
        ]



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved_as_property_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username




from django.urls import path
from . import views
from .views import CustomLoginView
from .views import users_in_group
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import import_csv
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('property/add/', views.add_property, name='add_property'),
    # path('property/update/<int:pk>/', views.update_property, name='update_property'),
    # path('property/list/', views.property_list, name='property_list'),
    path('property-owner-signup/', views.property_owner_signup, name='property_owner_signup'),
    # path('login/', views.LoginView.as_view(), name='login'),  # Assuming you use Django's built-in LoginView
    path('login/', CustomLoginView.as_view(), name='login'),  # Link the URL to the custom login view
    path('property-list/', views.property_list, name='property_list'),  
    path('property/delete/<str:pk>/', views.delete_property, name='delete_property'),
    path('property/update/<str:pk>/', views.update_property, name='update_property'),
    # path('property/update/<str:pk>/', views.update_property, name='update_property'),
    path('admin/auth/group/<int:group_id>/users/', users_in_group, name='group_users'),
    # path('property/<uuid:property_id>/', views.property_detail, name='property_detail'),
    # path('add_property/', views.add_property, name='add_property'),
    # path('property_list/', views.property_list, name='property_list'),
    path('location/<slug:location_slug>/', views.location_detail, name='location_detail'),
    path('import_csv/', import_csv, name='import_csv'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

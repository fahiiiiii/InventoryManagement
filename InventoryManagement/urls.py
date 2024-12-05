
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    # path('accounts/', include('django.contrib.auth.urls')), 
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     # ... your other URLs
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# # Serve media files during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)










#     from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     # ... your other URLs
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
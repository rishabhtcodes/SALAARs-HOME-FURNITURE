from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Custom showroom admin panel directly at /admin/ and /showroom-admin/
    path('admin/', lambda request: redirect('/showroom-admin/', permanent=False)),
    # Dedicated SQLite / Django Database Admin portal
    path('db-admin/', admin.site.urls),
    path('sqlite-admin/', lambda request: redirect('/db-admin/', permanent=False)),
    path('django-backend/', lambda request: redirect('/db-admin/', permanent=False)),
    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'store.views.not_found_view'

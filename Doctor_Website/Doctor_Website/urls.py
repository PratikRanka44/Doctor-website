from django.contrib import admin
from django.urls import path
from website.views import index, login, register,patient_dashboard,doctor_dashboard,logout
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
    path('logout/', logout, name='logout'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

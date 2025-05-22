from django.contrib import admin
from django.urls import path
# Import your renamed views from website.views
from website.views import (
    index,
    custom_login_view,  # Renamed login view
    register,
    patient_dashboard,
    doctor_dashboard,
    custom_logout_view, # Renamed logout view
    doctor_create_blog_post, # Don't forget to import this too!
    doctor_my_blogs,  
    doctor_edit_blog_post,
    doctor_delete_blog_post,
    patient_blog_list,
    patient_blog_detail
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', custom_login_view, name='login_view'), # Use the renamed view and name the URL pattern
    path('register/', register, name='register'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
    path('logout/', custom_logout_view, name='logout_view'), # Use the renamed view and name the URL pattern

    # Add the blog post URLs
    path('doctor/blog/new/', doctor_create_blog_post, name='doctor_create_blog_post'),
    path('doctor/my-blogs/', doctor_my_blogs, name='doctor_my_blogs'),
    
     # Add this new URL pattern for editing blog posts:
    path('doctor/blog/edit/<int:pk>/', doctor_edit_blog_post, name='doctor_edit_blog_post'),
     path('doctor/blog/delete/<int:pk>/', doctor_delete_blog_post, name='doctor_delete_blog_post'),
     path('patient/blog/', patient_blog_list, name='patient_blog_list'),
    path('patient/blog/<int:pk>/', patient_blog_detail, name='patient_blog_detail'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
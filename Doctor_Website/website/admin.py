from django.contrib import admin
from .models import UserRegistration,BlogCategory,BlogPost

admin.site.register(UserRegistration)
admin.site.register(BlogCategory)
admin.site.register(BlogPost)



# your_app/models.py
from django.db import models

class UserRegistration(models.Model):
    USER_ROLES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    role = models.CharField(max_length=10, choices=USER_ROLES, default='patient')
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100) # Consider using Django's PasswordField with hashing
    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) # Make optional

    def __str__(self):
        return f"{self.get_role_display()}: {self.fname} {self.lname}"
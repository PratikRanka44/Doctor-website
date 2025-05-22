# website/models.py (Replace 'your_app' with 'website' if that's your app name)
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings # Needed if you link to AUTH_USER_MODEL in other models (like BlogPost)

# Custom User Manager (REQUIRED for AbstractBaseUser)
class UserRegistrationManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # Use set_password to hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Superusers are usually active

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Your UserRegistration model, now inheriting from AbstractBaseUser and PermissionsMixin
class UserRegistration(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField(unique=True) # Email is now the unique identifier
    password = models.CharField(max_length=128) # Django will hash this, max_length for hashed password
    address = models.CharField(max_length=255, blank=True, null=True) # Changed to CharField for consistency, or keep TextField if preferred
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Required fields for AbstractBaseUser and PermissionsMixin
    is_active = models.BooleanField(default=True) # Indicates if the user account is active
    is_staff = models.BooleanField(default=False) # Indicates if the user can log into the Django admin site
    date_joined = models.DateTimeField(auto_now_add=True) # Automatically set when user is created

    objects = UserRegistrationManager() # Link the custom manager

    USERNAME_FIELD = 'email'  # This tells Django to use 'email' as the unique identifier for login
    REQUIRED_FIELDS = ['fname', 'lname', 'role'] # These fields will be prompted when creating a user via createsuperuser

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.fname} {self.lname}"

    def get_short_name(self):
        return self.fname

    # These methods are part of PermissionsMixin, often needed for Django's admin/permissions
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_active and self.is_superuser # Or customize based on your needs

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_active and self.is_superuser # Or customize based on your needs

    class Meta:
        verbose_name = 'User Registration'
        verbose_name_plural = 'User Registrations'


# Blog Category Model
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="A short label for URL") # Ensure slug is here

    class Meta:
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name

# Blog Post Model
class BlogPost(models.Model):
    # Use settings.AUTH_USER_MODEL to refer to your custom user model
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Refer to the user model defined in settings.py
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='blog_posts'
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True) # Added blank=True
    summary = models.TextField()
    content = models.TextField()
    is_draft = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_truncated_summary(self, word_limit=15):
        words = self.summary.split()
        if len(words) > word_limit:
            return ' '.join(words[:word_limit]) + '...'
        return self.summary
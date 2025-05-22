import json
from sqlite3 import IntegrityError
from .models import UserRegistration, BlogPost, BlogCategory
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
# from django.contrib.auth.models import User # You don't seem to be using this, can remove
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Import Django's authentication functions, but rename your custom ones to avoid conflict
from django.contrib.auth import authenticate as django_authenticate, login as django_login, logout as django_logout
import re
from django.contrib.auth.decorators import  user_passes_test
from django.contrib.auth.mixins import AccessMixin

# Create your views here.
def add_errors_to_context(context, field_name, message):
    if 'errors' not in context: # Fixed typo: 'not not' to 'not'
        context['errors'] = {}
    if field_name not in context['errors']:
        context['errors'][field_name] = []
    context['errors'][field_name].append(message)
    return context

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('Password') # Note the capital 'P'
        address = request.POST.get('Address')
        state = request.POST.get('State')
        city = request.POST.get('City')
        picture = request.FILES.get('Picture')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            # You might want to re-render the form with existing data here
            return render(request, 'registration.html', {'error': "Passwords do not match"})

        # Basic validation for required fields
        if not all([role, fname, lname, email, password]):
            messages.error(request, "Please fill in all required fields (Role, First Name, Last Name, Email, Password).")
            return render(request, 'registration.html', request.POST) # Pass POST data back to re-fill form

        try:
            user = UserRegistration(
                role=role,
                fname=fname,
                lname=lname,
                email=email,
                address=address,
                state=state,
                city=city,
                picture=picture
            )
            # Use set_password to hash the password
            user.set_password(password)
            user.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login_view')
        except IntegrityError: # Catches unique constraint violations (e.g., duplicate email)
            messages.error(request, "An account with this email already exists.")
            return render(request, 'registration.html', request.POST)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during registration: {e}")
            return render(request, 'registration.html', request.POST)

    # Context for initial GET request
    states_json = json.dumps({
        "MH": [["MH-01", "Mumbai"], ["MH-02", "Pune"]], # Example: Populate with actual data
        # Add other states and cities as needed
    })
    cities_json = json.dumps({
        "MH": [["MH-01", "Mumbai"], ["MH-02", "Pune"]]
    })
    return render(request, 'registration.html', {'states': states_json, 'cities': cities_json})


# Renamed your login view to avoid conflict
def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Use Django's authenticate function which correctly checks hashed passwords
        user = django_authenticate(request, username=email, password=password)

        if user is not None:
            # If authentication is successful, log the user in
            django_login(request, user)
            messages.success(request, f"Welcome, {user.fname}!")

            if user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')
            else:
                messages.error(request, "Unknown user role.")
                django_logout(request) # Log them out if role is invalid
                return redirect('login_view')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def custom_logout_view(request):
    django_logout(request) # This handles clearing Django's auth session
    # Clear your custom session variables
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_role' in request.session:
        del request.session['user_role']
    messages.info(request, "You have been logged out.")
    return redirect('login_view')


# --- Dashboard views ---

def is_patient(user):
    # Assuming user.role == 'patient' based on your UserRegistration model
    return user.is_authenticated and user.role == 'patient'

@login_required(login_url='login_view') # Ensure user is logged in
@user_passes_test(is_patient, login_url='login_view') # Ensure user is a patient
def patient_dashboard(request):
    # Fetch all published blog posts (is_draft=False)
    # Order them by most recently published first
    published_blog_posts = BlogPost.objects.filter(is_draft=False).order_by('-published_at')

    # Fetch all blog categories for filtering
    categories = BlogCategory.objects.all().order_by('name')

    # Handle category filtering if a category is selected via GET parameter
    selected_category_id = request.GET.get('category')
    selected_category_name = None # To display the selected category name

    if selected_category_id:
        try:
            # Filter posts by the selected category
            published_blog_posts = published_blog_posts.filter(category__id=selected_category_id)
            selected_category_name = BlogCategory.objects.get(id=selected_category_id).name
        except BlogCategory.DoesNotExist:
            messages.error(request, "Invalid category selected. Displaying all published posts.")
            selected_category_id = None # Reset to show all if category is invalid
            selected_category_name = None

    context = {
        'published_blog_posts': published_blog_posts,
        'categories': categories,
        'selected_category_id': int(selected_category_id) if selected_category_id else None,
        'selected_category_name': selected_category_name, # Pass name for display
        'user_profile': request.user, # The logged-in patient's UserRegistration instance
    }
    return render(request, 'patient_dashboard.html', context)


@login_required
@user_passes_test(is_patient, login_url='/access-denied/') # Redirect if not a patient
def patient_blog_list(request):
    # Get all published blog posts (is_draft=False)
    # Prefetch related categories to reduce database queries
    blog_posts = BlogPost.objects.filter(is_draft=False).select_related('category').order_by('-published_at') # <-- CHANGED HERE

    # Group posts by category
    categorized_posts = {}
    for post in blog_posts:
        category_name = post.category.name if post.category else 'Uncategorized'
        if category_name not in categorized_posts:
            categorized_posts[category_name] = []
        categorized_posts[category_name].append(post)

    context = {
        'categorized_posts': categorized_posts,
    }
    return render(request, 'patient_blog_list.html', context)

@login_required
@user_passes_test(is_patient, login_url='/access-denied/')
def patient_blog_detail(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk, is_draft=False)
    context = {
        'blog_post': blog_post,
    }
    return render(request, 'patient_blog_detail.html', context)




@login_required
def doctor_dashboard(request):
    # request.user is now your UserRegistration instance
    user_profile = request.user

    # Perform role check
    if user_profile.role != 'doctor':
        messages.error(request, "You are not authorized to view the doctor dashboard.")
        django_logout(request) # Log out if unauthorized role tries to access
        return redirect('custom_login_view')

    return render(request, 'doctor_dashboard.html', {'user_profile': user_profile})

# Corrected is_doctor check, assuming user_passes_test is used with this function
def is_doctor(user):
    return user.is_authenticated and user.role == 'doctor'

# --- Doctor-Specific Views ---
@login_required(login_url='login_view')
@user_passes_test(is_doctor, login_url='login_view')
def doctor_create_blog_post(request):
    categories = BlogCategory.objects.all().order_by('name')

    context = {
        'categories': categories,
        'user_profile': request.user,
        'is_edit': False, # Indicate this is a create operation
        'errors': {},
    }

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        is_draft = 'is_draft' in request.POST
        # Correctly get the image file from request.FILES
        image_file = request.FILES.get('image_file')

        errors = {}

        # Basic Validation
        if not title:
            errors.setdefault('title', []).append("Title is required.")
        if not category_id:
            errors.setdefault('category', []).append("Category is required.")
        if not summary:
            errors.setdefault('summary', []).append("Summary is required.")
        if not content:
            errors.setdefault('content', []).append("Content is required.")

        # --- Image Validation (Optional but Recommended) ---
        if not image_file: # Image is required for new posts (or if not provided, use default)
            # You can make image required, or allow it to be optional and rely on a default.
            # If required:
            # errors.setdefault('image_file', []).append("Blog image is required.")
            pass # For now, we'll assume it's optional on creation if not provided

        if errors:
            context['errors'] = errors
            # Populate old_data so form retains user input on error
            context['old_data'] = {
                'title': title,
                'category': category_id,
                'summary': summary,
                'content': content,
            }
            context['old_is_draft'] = is_draft
            messages.error(request, "Please correct the errors below.")
        else:
            try:
                category = get_object_or_404(BlogCategory, pk=category_id)
                new_blog_post = BlogPost(
                    title=title,
                    author=request.user, # Assign the current logged-in doctor as author
                    category=category,
                    summary=summary,
                    content=content,
                    is_draft=is_draft,
                )
                # Assign the image file ONLY if it was provided
                if image_file:
                    new_blog_post.image = image_file

                new_blog_post.save() # Save the new blog post

                messages.success(request, "Blog post created successfully!")
                return redirect('doctor_my_blogs') # Redirect to the doctor's blog list

            except IntegrityError:
                # Handle cases where a unique field (e.g., title) might conflict
                messages.error(request, "A blog post with this title already exists.")
                context['errors']['title'] = ["A blog post with this title already exists."]
                context['old_data'] = { # Re-populate for display
                    'title': title,
                    'category': category_id,
                    'summary': summary,
                    'content': content,
                }
                context['old_is_draft'] = is_draft
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                # You might want to log the full exception: logging.exception("Error creating blog post")

    # For GET request or if there were errors on POST and we need to re-render the form
    return render(request, 'doctor_create_blog.html', context)


@login_required
def doctor_my_blogs(request):
    # request.user is now your UserRegistration instance
    user_profile = request.user

    # Ensure only doctors can access this view
    if user_profile.role != 'doctor':
        messages.error(request, "You are not authorized to view this page.")
        django_logout(request)
        return redirect('custom_login_view')

    my_posts = BlogPost.objects.filter(author=user_profile).order_by('-published_at')

    context = {
        'my_posts': my_posts,
        'user_profile': user_profile,
    }
    return render(request, 'doctor_my_blogs.html', context)

# Updated doctor_edit_blog_post view (Manual Form Handling)
@login_required(login_url='login_view')
@user_passes_test(is_doctor, login_url='login_view')
def doctor_edit_blog_post(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    categories = BlogCategory.objects.all().order_by('name')
    
    context = {
        'blog_post': blog_post,
        'categories': categories,
        'user_profile': request.user,
        'is_edit': True, # Flag for template
        'errors': {},
        'current_image': blog_post.image, # Pass current image for display
    }

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        new_image = request.FILES.get('image') # New image upload
        clear_image = request.POST.get('clear_image') == 'on' # Check if clear checkbox is checked
        is_draft = request.POST.get('is_draft') == 'on'

        # Retain user input in case of errors
        context['old_data'] = request.POST.copy()
        context['old_is_draft'] = is_draft
        context['old_image'] = new_image # Store new image if provided but validation fails

        # --- Manual Validation ---
        validation_errors = {}
        if not title:
            validation_errors['title'] = "Title is required."
        if not summary:
            validation_errors['summary'] = "Summary is required."
        if not content:
            validation_errors['content'] = "Content is required."
        if not category_id:
            validation_errors['category'] = "Category is required."
        else:
            try:
                selected_category = BlogCategory.objects.get(id=category_id)
            except BlogCategory.DoesNotExist:
                validation_errors['category'] = "Invalid category selected."

        if validation_errors:
            context['errors'] = validation_errors
            messages.error(request, "Please correct the errors below.")
            return render(request, 'doctor_create_blog.html', context)
        
        # If validation passes
        try:
            blog_post.title = title
            blog_post.category = selected_category
            blog_post.summary = summary
            blog_post.content = content
            blog_post.is_draft = is_draft

            if clear_image:
                blog_post.image = None # Clear image field
            elif new_image:
                blog_post.image = new_image # Update with new image
            # If no new_image and clear_image is not checked, retain existing image

            blog_post.save()
            messages.success(request, "Blog post updated successfully!")
            return redirect('doctor_my_blogs')
        except IntegrityError:
            messages.error(request, "A blog post with this title might already exist or there was a database error.")
            context['errors']['general'] = ["A blog post with this title might already exist or there was a database error."]
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            context['errors']['general'] = [f"An unexpected error occurred: {e}"]

    else: # GET request
        # Populate old_data with current blog_post data for initial form display
        context['old_data'] = {
            'title': blog_post.title,
            'category': blog_post.category.id if blog_post.category else '', # Get category ID
            'summary': blog_post.summary,
            'content': blog_post.content,
        }
        context['old_is_draft'] = blog_post.is_draft
        # current_image is already in context from initial setup

    return render(request, 'doctor_create_blog.html', context)


# doctor_delete_blog_post remains the same
@login_required(login_url='login_view')
@user_passes_test(is_doctor, login_url='login_view')
def doctor_delete_blog_post(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk, author=request.user)

    if request.method == 'POST':
        blog_post.delete()
        messages.success(request, "Blog post deleted successfully.")
        return redirect('doctor_my_blogs')
    else:
        # Render a confirmation page
        return render(request, 'blog_post_confirm_delete.html', {'blog_post': blog_post, 'user_profile': request.user})

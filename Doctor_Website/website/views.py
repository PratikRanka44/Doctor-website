import json
from .models import UserRegistration
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re



# Create your views here.

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
        address = request.POST.get('Address')       # Note the capital 'A'
        state = request.POST.get('State')           # Note the capital 'S'
        city = request.POST.get('City')             # Note the capital 'C'
        picture = request.FILES.get('Picture')

        # Basic password matching (you might want more robust validation)
        if password == confirm_password:
            try:
                user = UserRegistration(
                     role=role,
                    fname=fname,
                    lname=lname,
                    email=email,
                    password=password,
                    address=address,
                    state=state,
                    city=city,
                    picture=picture
                )
                user.save()
                return render(request, 'registration.html')
            except Exception as e:
                # Handle database errors (e.g., unique email constraint)
                error_message = f"Error saving registration: {e}"
                return render(request, 'registration.html', {'error': error_message})
        else:
            return render(request, 'registration.html', {'error': "Passwords do not match"})

    return render(request, 'registration.html')



def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserRegistration.objects.get(email=email)
            if user.password == password:  # WARNING: Insecure password check!
                request.session['user_id'] = user.id  # Store user ID in session
                if user.role == 'patient':
                    return redirect('patient_dashboard')
                elif user.role == 'doctor':
                    return redirect('doctor_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except UserRegistration.DoesNotExist:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')

@login_required  # You'll need to import this from django.contrib.auth.decorators if you still want to use it for dashboard access
def patient_dashboard(request):
    try:
        user_profile = UserRegistration.objects.get(id=request.session.get('user_id'))
        return render(request, 'patient_dashboard.html', {'user_profile': user_profile})
    except UserRegistration.DoesNotExist:
        return redirect('login') # Or handle the error appropriately

@login_required  # Same as above
def doctor_dashboard(request):
    try:
        user_profile = UserRegistration.objects.get(id=request.session.get('user_id'))
        return render(request, 'doctor_dashboard.html', {'user_profile': user_profile})
    except UserRegistration.DoesNotExist:
        return redirect('login') # Or handle the error appropriately
    
def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return redirect('login') # Redirect to the login page after logout
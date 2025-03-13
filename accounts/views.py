from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from grocery.models import Order

# User Registration
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password')

        if password != password_confirm:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'accounts/register.html')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        # Create user profile
        UserProfile.objects.create(user=user)
        user.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')  # Redirect to login page

    return render(request, 'accounts/register.html')

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirect to homepage after login
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})
    return render(request, 'accounts/login.html')

# User Logout
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    
    if request.method == 'POST':
        user_profile.phone_number = request.POST.get('phone_number', '')
        user_profile.address = request.POST.get('address', '')
        user_profile.save()
        
        # Update user information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
        
    return render(request, 'accounts/profile.html', {
        'profile': user_profile,
        'orders': orders
    })

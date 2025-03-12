from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

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

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.views import View
from .forms import LoginForm, PasswordRecoveryForm

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Fetch user to check lockout
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password.")
                return render(request, 'accounts/login.html', {'form': form})
            
            # Check lockout
            if user.check_lockout():
                time_left = user.locked_until - timezone.now()
                minutes = int(time_left.total_seconds() / 60) + 1
                messages.error(request, f"Account is locked. Please try again after {minutes} minutes.")
                return render(request, 'accounts/login.html', {'form': form})
            
            # Authenticate
            authenticated_user = authenticate(username=username, password=password)
            
            if authenticated_user is not None:
                # Success
                authenticated_user.reset_failed_attempts()
                authenticated_user.last_ip = get_client_ip(request)
                authenticated_user.save()
                
                login(request, authenticated_user)
                return redirect('dashboard')
            else:
                # Failed login
                user.register_failed_attempt()
                if user.is_locked:
                    messages.error(request, "Too many failed attempts. Your account has been locked for 15 minutes.")
                else:
                    attempts_left = 5 - user.failed_login_attempts
                    messages.error(request, f"Invalid username or password. {attempts_left} attempts remaining.")
                
        return render(request, 'accounts/login.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Logged out successfully.")
        return redirect('login')

class PasswordRecoveryView(View):
    def get(self, request):
        form = PasswordRecoveryForm()
        return render(request, 'accounts/recovery.html', {'form': form})

    def post(self, request):
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            
            try:
                user = User.objects.get(username=username, email=email)
                user.set_password(new_password)
                user.reset_failed_attempts()  # Unlock if it was locked
                user.save()
                messages.success(request, "Password reset successfully. You can now login.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "User with specified username and email not found.")
                
        return render(request, 'accounts/recovery.html', {'form': form})

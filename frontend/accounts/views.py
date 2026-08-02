from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from .forms import LoginForm, RegisterForm, ProfileForm
from .forms.profile_form import PasswordChangeForm
from .services.auth_service import login_user, register_user


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            register_user(form, request)
            messages.success(request, 'Account created successfully! Welcome.')
            return redirect('my_tickets:list')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.email}!')
            next_url = request.GET.get('next', '')
            # Validate next is a safe local path (no external redirects)
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
            return redirect('home:index')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home:index')


@login_required
def profile_view(request):
    from frontend.ticket_sales.models import Ticket

    user = request.user
    profile_form = ProfileForm(instance=user)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the errors below.')

        elif action == 'change_password':
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the password errors below.')

    from django.db.models import Count, Q
    from core.constants import TICKET_ACTIVE, TICKET_CANCELLED
    stats = Ticket.objects.filter(owner=user).aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status=TICKET_ACTIVE)),
        cancelled=Count('id', filter=Q(status=TICKET_CANCELLED)),
    )

    initials = (
        (user.first_name[0] if user.first_name else '') +
        (user.last_name[0] if user.last_name else '')
    ).upper() or (user.email[0].upper() if user.email else '?')

    context = {
        'form': profile_form,
        'password_form': password_form,
        'stats': stats,
        'initials': initials,
    }
    return render(request, 'accounts/profile.html', context)

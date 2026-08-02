from django.contrib.auth import authenticate, login, logout


def login_user(request, email: str, password: str) -> bool:
    user = authenticate(request, username=email, password=password)
    if user:
        login(request, user)
        return True
    return False


def logout_user(request):
    logout(request)


def register_user(form, request=None):
    user = form.save()
    if request:
        login(request, user)
    return user

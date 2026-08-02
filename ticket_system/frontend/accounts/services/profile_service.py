def update_profile(user, form):
    """Save profile form data to the user."""
    form.save()
    return user

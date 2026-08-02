from django.conf import settings

# Cache at module level — EVENT_NAME and EVENT_DATE are startup constants
# and never change, so there's no need to rebuild the dict on every request.
_SITE_CONTEXT: dict | None = None


def site_settings(request):
    """Inject global site context into every template."""
    global _SITE_CONTEXT
    if _SITE_CONTEXT is None:
        _SITE_CONTEXT = {
            'EVENT_NAME': settings.EVENT_NAME,
            'EVENT_DATE': settings.EVENT_DATE,
            # STRIPE_PUBLISHABLE_KEY is intentionally NOT injected globally —
            # it is only added to the payment view context to limit exposure.
        }
    return _SITE_CONTEXT

from .settings import *

# Lightweight test settings override used when running the test suite in CI
# or locally where MySQL is not available. Uses SQLite in-memory DB by default.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use the in-memory email backend to avoid external SMTP during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Reduce logging noise in test runs
LOGGING['root']['level'] = 'ERROR'

# Monkeypatch Django's BaseContext.__copy__ to avoid incompatibility with
# the Python copy() behavior introduced in some environments. The default
# implementation in the installed Django package calls copy(super()) which
# can fail. This patch is only applied for tests (this file is the test
# settings module) and is safe because it performs a shallow copy of the
# context object and its dict stack.
try:
    import copy as _copy
    from django.template import context as _template_context

    def _basecontext_copy(self):
        # Create an empty instance without calling __init__
        duplicate = object.__new__(self.__class__)
        # Shallow-copy attributes, but copy the dicts list itself
        for k, v in getattr(self, "__dict__", {}).items():
            if k == "dicts":
                setattr(duplicate, "dicts", v[:])
            else:
                try:
                    setattr(duplicate, k, _copy.copy(v))
                except Exception:
                    setattr(duplicate, k, v)
        return duplicate

    _template_context.BaseContext.__copy__ = _basecontext_copy
except Exception:
    # If anything goes wrong (Django not present yet or unexpected API),
    # don't crash test setup — the real test run will reveal issues.
    pass



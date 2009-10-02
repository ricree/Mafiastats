import django.dispatch

profile_link = django.dispatch.Signal(providing_args=["user","player"])
profile_unlink  = django.dispatch.Signal(providing_args=["user","player"])

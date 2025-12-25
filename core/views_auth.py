from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    # Allow GET/POST logout without 405, then go to login page
    logout(request)
    return redirect("/login/")

from django.shortcuts import render
from django.http import JsonResponse
from firebase_admin import auth
import json

# Login page
def login_view(request):
    return render(request, 'login.html')

# Register page
def register_view(request):
    return render(request, 'register.html')

# Dashboard page
def dashboard_view(request):
    return render(request, 'dashboard.html')

def academic_view(request):
    return render(request, 'academic.html')

def tools_view(request):
    return render(request, 'tools.html')

def appointments_view(request):
    return render(request, 'appointments.html')

def forum_view(request):
    return render(request, 'forum.html')

def analytics_view(request):
    return render(request, 'analytics.html')

def analytics_view(request):
    return render(request, 'analytics.html')

def users_management_view(request):
    return render(request, 'users-management.html')

def profile_view(request):
    return render(request, 'profile.html')

# Token verification
def verify_token(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        id_token = body.get('idToken')
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            return JsonResponse({'message': 'Authentication successful', 'uid': uid})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=401)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

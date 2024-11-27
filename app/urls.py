from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('academic/', views.academic_view, name='academic'),
    path('tools/', views.tools_view, name='tools'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('forum/', views.forum_view, name='forum'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('users-management/', views.users_management_view, name='users-management'),
    path('profile/', views.profile_view, name='profile'),
    path('api/verify-token/', views.verify_token, name='verify-token'),
]

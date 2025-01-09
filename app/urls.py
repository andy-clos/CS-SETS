from django.urls import path
from . import views
from .views import getPosts, viewPost,submit_comment

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('academic/', views.academic_view, name='academic'),
    path('academic/<str:semester_year>/<str:course_code>/', views.course_detail_view, name='course-detail'),
    path('academic/<str:semester_year>/<str:course_code>/delete/', views.delete_course_view, name='delete-course'),
    path('tools/', views.tools_view, name='tools'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('forum/', views.forum_view, name='forum'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('analytics/<str:semester_year>/<str:course_code>/', views.analytics_detail_view, name='analytics-detail'),
    path('users-management/', views.users_management_view, name='users-management'),
    path('profile/', views.profile_view, name='profile'),
    path('api/verify-token/', views.verify_token, name='verify-token'),
    path('createPost/', views.createpost_view, name='createpost'),
    path('forum/', getPosts, name='forum'),
    path('forum/view/<int:post_id>', viewPost, name='view_post'),
    path('forum/submit_comment/<int:post_id>/', submit_comment, name='submit_comment'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('download-timetable/', views.download_timetable, name='download_timetable'),
    path('cgpa/', views.cgpa_view, name='cgpa'),
    path('delete-profile/', views.delete_profile, name='delete-profile'),
    path('check-course/', views.check_course, name='check-course'),
    path('check-student-course/', views.check_student_course, name='check-student-course'),
    path('academic/<str:semester_year>/<str:course_code>/update-marks/<str:student_email>/', views.update_marks, name='update-marks'),
    path('unenroll-student/', views.unenroll_student, name='unenroll-student'),
]

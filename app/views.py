import joblib
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from firebase_admin import auth, db as admin_db
import json
import pyrebase
from datetime import datetime
import pytz
from django.contrib import messages
import random
import colorsys
from io import BytesIO
import xhtml2pdf.pisa as pisa
import datetime
from django.core.exceptions import ValidationError
from functools import wraps
import logging
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
import re
from firebase_admin import auth, firestore, credentials, initialize_app
from django.views.decorators.http import require_POST
import csv
from io import TextIOWrapper
import time
import base64
from django.core.files.base import ContentFile
from django.views.decorators.http import require_GET
import uuid
import requests



logger = logging.getLogger(__name__)

config = {
    "apiKey": "AIzaSyCqHVyxf6nbxfEWIf_YbccJvjursSwIRcc",
    "authDomain": "cs-sets.firebaseapp.com",
    "databaseURL": "https://cs-sets-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "projectId": "cs-sets",
    "storageBucket": "cs-sets.firebasestorage.app",
    "messagingSenderId": "918781841486",
    "appId": "1:918781841486:web:528cd96da7ba9a9f84b31f",
    "measurementId": "G-77X9SZ0DJ6"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate('cs-sets-firebase-adminsdk-iqxvr-c5c5c8c3c6.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Login page
def login_view(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            try:
                # Check if user exists in database first
                encoded_email = email.replace('.', '-dot-').replace('@', '-at-')
                user_exists = database.child("users").child(encoded_email).get().val()
                
                if not user_exists:
                    return JsonResponse({
                        'status': 'error',
                        'message': "User not found. Please check your email or register."
                    })
                
                try:
                    # Firebase authentication
                    user = authe.sign_in_with_email_and_password(email, password)
                    user_data = user_exists  # Use the data we already retrieved
                    
                    # Set session data
                    session_data = {
                        'user_email': email,
                        'user_name': user_data.get('name'),
                        'user_id': user['localId'],
                        'user_role': user_data.get('role'),
                        'id_token': user['idToken']
                    }
                    
                    # Update session
                    request.session.update(session_data)
                    request.session['welcome_message'] = f"Welcome back, {user_data.get('name', email)}!"
                    request.session.modified = True
                    
                    return JsonResponse({
                        'status': 'success',
                        'redirect_url': '/dashboard/'
                    })
                    
                except Exception as pwd_error:
                    return JsonResponse({
                        'status': 'error',
                        'message': "Incorrect password. Please try again."
                    })
                
            except Exception as auth_error:
                logger.error(f"Authentication error: {str(auth_error)}")
                return JsonResponse({
                    'status': 'error',
                    'message': handle_firebase_error(auth_error)
                })
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': "An unexpected error occurred. Please try again."
            })
            
    return render(request, 'login.html')

def is_valid_email(email):
    """Validate email format"""
    try:
        from django.core.validators import validate_email
        validate_email(email)
        return True
    except ValidationError:
        return False

def handle_firebase_error(e):  # not complete yet, error undetected!!!!
    error_message = str(e)
    if "INVALID_PASSWORD" in error_message:
        return "Invalid password. Please try again."
    elif "EMAIL_NOT_FOUND" in error_message:
        return "Email not found. Please check your email or register."
    elif "INVALID_EMAIL" in error_message:
        return "Invalid email format."
    elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
        return "Too many failed attempts. Please try again later."
    else:
        return "Authentication failed. Please try again."

def logout_view(request):
    """Handle user logout"""
    try:
        # Clear all session data
        request.session.flush()
        messages.success(request, "You have been successfully logged out.")
    except Exception as e:
        messages.error(request, "Error during logout. Please try again.")
    
    return redirect('login')

def is_logged_in(request):
    """Check if user is logged in"""
    return 'user_email' in request.session and 'user_id' in request.session

def get_current_user(request):
    """Get current user's email"""
    return request.session.get('user_email')

def login_required(view_func):
    """Decorator to require login for views"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_logged_in(request):
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Register page
def register_view(request):
    if request.method == 'POST':
        try:
            # Get form data
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            name = request.POST.get('name', '').strip()
            identity = request.POST.get('identity', '').strip()
            gender = request.POST.get('gender', '')
            birthday = request.POST.get('birthday', '')
            is_lecturer = request.POST.get('isLecturer') == 'on'
            
            # Set major based on lecturer status
            major = 'Teaching' if is_lecturer else request.POST.get('major', '')
            matrix = request.POST.get('matrix', '').strip()

            # Validate email domain based on lecturer status
            if is_lecturer:
                if not email.endswith('@usm.my'):
                    messages.error(request, 'Lecturer must use @usm.my email address')
                    return render(request, 'register.html')
                role = 'lecturer'
            else:
                if not email.endswith('@student.usm.my'):
                    messages.error(request, 'Student must use @student.usm.my email address')
                    return render(request, 'register.html')
                role = 'student'

            try:
                # Create users node if it doesn't exist
                if not database.child("users").get().val():
                    database.child("users").set({})

                # Create user in Firebase Authentication using Pyrebase
                user = authe.create_user_with_email_and_password(email, password)
                
                # Encode email for Firebase path (replace @ and . with safe characters)
                encoded_email = email.replace('.', '-dot-').replace('@', '-at-')
                
                # Prepare user data for Realtime Database in specific sequence
                user_data = {
                    'uid': user['localId'],
                    'email': email,
                    'name': name,
                    'role': role,
                    'matrix': matrix,
                    'identity': identity,
                    'major': major,
                    'gender': gender,
                    'birthday': birthday,
                    'profile_picture': ''
                }

                # Save user data to Realtime Database using encoded email as key
                database.child("users").child(encoded_email).set(user_data)

                # Set session data after successful registration
                session_data = {
                    'user_email': email,
                    'user_id': user['localId'],
                    'user_role': role,
                    'id_token': user['idToken']
                }
                request.session.update(session_data)
                request.session['welcome_message'] = f"Welcome, {name}! Your registration was successful."
                request.session.modified = True

                messages.success(request, 'Registration successful! You will be redirected to login page in 2 seconds.')
                response = render(request, 'register.html')
                response['Refresh'] = '2;url=/login'
                return response

            except Exception as auth_error:
                # If there's an error, attempt to delete the user if it was created
                try:
                    if 'user' in locals():
                        auth.delete_user(user['localId'])
                except:
                    pass
                
                error_message = str(auth_error)
                if "EMAIL_EXISTS" in error_message:
                    messages.error(request, 'This email is already registered')
                else:
                    messages.error(request, f'Registration failed: {error_message}')
                return render(request, 'register.html')

        except Exception as e:
            messages.error(request, f'Server error: {str(e)}')
            return render(request, 'register.html')

    return render(request, 'register.html')

# Dashboard page
@login_required
def dashboard_view(request):
    try:
        # Handle POST request for creating announcement
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                selected_course = data.get('selected_course')
                title = data.get('add-title')
                content = data.get('add-content')
                current_user = request.session.get('user_name')
                
                # Get latest academic year and semester
                courses_data = database.child("course").get().val()
                sorted_years = sorted(courses_data.keys(), reverse=True)
                current_year = sorted_years[0]  # Get latest year
                current_semester = get_latest_semester(courses_data, current_year)
                
                # Create announcement data
                announcement_data = {
                    'title': title,
                    'content': content,
                    'author': current_user,
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                print(f"Creating announcement:")
                print(f"Course: {selected_course}")
                print(f"Year: {current_year}")
                print(f"Semester: {current_semester}")
                print(f"Data: {announcement_data}")
                
                # Push the announcement to Firebase
                database.child("course")\
                       .child(current_year)\
                       .child(current_semester)\
                       .child(selected_course)\
                       .child('announcements')\
                       .push(announcement_data)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Announcement posted successfully'
                })
                
            except Exception as e:
                print(f"Error posting announcement: {e}")
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })

        # Handle GET request - Your existing code
        courses_data = database.child("course").get().val()
        latest_courses = []
        lecturer_latest_courses =[]
        announcements = []
        
        if courses_data:
            sorted_years = sorted(courses_data.keys(), reverse=True)
            current_year = sorted_years[0]  # Get latest year
            current_semester = get_latest_semester(courses_data, current_year)
            
            # Get courses for the latest semester
            semester_courses = courses_data[current_year][current_semester]
            
            # Process each course
            for course_code, course_info in semester_courses.items():
                print(f"\nProcessing course: {course_code}")
                print(f"Course info: {course_info}")
                
                # Create course_data for admin view
                course_data = {
                    'course_code': course_code,
                    'course_name': course_info.get('course_name', '')
                }
                latest_courses.append(course_data)
                
                # Check all lecturers entries
                lecturers = course_info.get('lecturers', [])
                print(f"Lecturers data: {lecturers}")
                print(f"Current user email: {request.session.get('user_email')}")
                is_course_lecturer = False
                
                # Loop through the lecturers list
                if isinstance(lecturers, list):
                    print("Processing lecturers list...")
                    for lecturer_entry in lecturers:
                        print(f"Checking lecturer entry: {lecturer_entry}")
                        if lecturer_entry and isinstance(lecturer_entry, dict):
                            lecturer_email = lecturer_entry.get('lecturer_email')
                            print(f"Found lecturer email: {lecturer_email}")
                            print(f"Comparing with current user: {lecturer_email == request.session.get('user_email')}")
                            if lecturer_email == request.session.get('user_email'):
                                is_course_lecturer = True
                                print("Match found!")
                                break
                    else:
                        print(f"Lecturers is not a list, it's a {type(lecturers)}")
                
                print(f"Is course lecturer: {is_course_lecturer}")
                
                # Only add to lecturer_latest_courses if current user is a lecturer for this course
                if is_course_lecturer:
                    lecturer_course_data = {
                        'course_code': course_code,
                        'course_name': course_info.get('course_name', '')
                    }
                    lecturer_latest_courses.append(lecturer_course_data)
                    print(f"Added course {course_code} to lecturer courses")
                
                # Get announcements for this course
                course_announcements = course_info.get('announcements', {})
                if course_announcements:
                    for ann_id, ann_data in course_announcements.items():
                        announcement = {
                            'id': ann_id,
                            'course_code': course_code,
                            'title': ann_data.get('title', ''),
                            'content': ann_data.get('content', ''),
                            'author': ann_data.get('author', ''),
                            'timestamp': ann_data.get('timestamp', '')
                        }
                        announcements.append(announcement)
        
        # Sort announcements by timestamp (newest first)
        announcements.sort(key=lambda x: x['timestamp'], reverse=True)
        
        context = {
            'lecturer_latest_courses': lecturer_latest_courses,
            'latest_courses': latest_courses,
            'announcements': announcements,
            'current_year': current_year,
            'current_semester': current_semester
        }
        
        print("\nFinal Results:")
        print(f"Total courses: {len(latest_courses)}")
        print(f"Lecturer courses: {len(lecturer_latest_courses)}")
        print(f"Lecturer courses list: {lecturer_latest_courses}")
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        print(f"Error in dashboard view: {e}")
        return render(request, 'dashboard.html', {'error': str(e)})

def academic_view(request):
    if request.method == 'POST':
        if 'action' not in request.POST:  # This is for admin adding a course
            try:
                # Get form data
                semester = request.POST.get('semester')
                academic_year = request.POST.get('academic_year').replace('/', '-')
                course_code = request.POST.get('course_code').upper()
                course_name = request.POST.get('course_name').title()

                # Process lecturers
                lecturers = {}
                lecturer_index = 1
                while True:
                    lecturer_name = request.POST.get(f'lecturer_name{lecturer_index}')
                    lecturer_email = request.POST.get(f'lecturer_email{lecturer_index}')
                    if not lecturer_name or not lecturer_email:
                        break
                    lecturers[lecturer_index] = {
                        "lecturer_name": lecturer_name.title(),
                        "lecturer_email": lecturer_email.lower()
                    }
                    lecturer_index += 1

                # Process venue and time
                venue_time = {}
                venue_time_index = 1
                while True:
                    class_venue = request.POST.get(f'class_venue{venue_time_index}')
                    class_day = request.POST.get(f'class_day{venue_time_index}')
                    class_start_time = request.POST.get(f'class_start_time{venue_time_index}')
                    class_end_time = request.POST.get(f'class_end_time{venue_time_index}')
                    if not all([class_venue, class_day, class_start_time, class_end_time]):
                        break
                    venue_time[venue_time_index] = {
                        "class_venue": class_venue.upper(),
                        "class_day": class_day,
                        "class_start_time": class_start_time,
                        "class_end_time": class_end_time
                    }
                    venue_time_index += 1

                # Process courseworks
                courseworks = {}
                coursework_index = 1
                while True:
                    coursework_type = request.POST.get(f'coursework_type{coursework_index}')
                    total_mark = request.POST.get(f'total_mark{coursework_index}')
                    
                    if not coursework_type or not total_mark:
                        break
                        
                    courseworks[f'coursework{coursework_index}'] = {
                        'type': coursework_type,
                        'total_mark': int(total_mark)
                    }
                    coursework_index += 1

                # Create course data structure
                course_data = {
                    "course_name": course_name,
                    "lecturers": lecturers,
                    "venue and time": venue_time,
                    "courseworks": courseworks
                }

                # Save to Firebase
                database.child("course").child(academic_year).child(semester).child(course_code).set(course_data)
                return JsonResponse({
                    'status': 'success',
                    'message': f'Course {course_code} has been successfully added.'
                })

            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

        else:  # This is for student adding a course
            try:
                user_email = get_current_user(request)
                encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
                selected_course = request.POST.get('selected_course')
                
                courses_data = database.child("course").get().val()
                latest_year = sorted(courses_data.keys(), reverse=True)[0]
                latest_semester = max(range(len(courses_data[latest_year])), 
                                   key=lambda x: x if isinstance(courses_data[latest_year][x], dict) else -1)

                course_info = {
                    'academic_year': latest_year,
                    'semester': str(latest_semester),  # Make sure to store the semester
                    'course_code': selected_course
                }
                
                database.child("users").child(encoded_email).child("courses").push(course_info)
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Successfully enrolled in {selected_course}.'
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

    # Get latest courses for student selection
    latest_courses = []
    student_courses = []
    courses = {}
    latest_year = None
    latest_semester = None

    try:
        courses_data = database.child("course").get().val()
        if courses_data:
            # Get all users to count students per course
            users_data = database.child("users").get().val()
            course_student_counts = {}
            
            # Count students for each course, considering semester
            if users_data:
                for user_key, user_info in users_data.items():
                    if user_info.get('role') == 'student' and 'courses' in user_info:
                        for course_key, course_info in user_info['courses'].items():
                            course_code = course_info.get('course_code')
                            course_semester = course_info.get('semester')
                            course_year = course_info.get('academic_year')
                            if course_code and course_semester and course_year:
                                # Create a unique key combining course code, year, and semester
                                unique_course_key = f"{course_code}_{course_year}_{course_semester}"
                                course_student_counts[unique_course_key] = course_student_counts.get(unique_course_key, 0) + 1

            # Get latest academic year
            sorted_years = sorted(courses_data.keys(), reverse=True)
            latest_year = sorted_years[0]
            
            # Get latest semester
            latest_semester = get_latest_semester(courses_data, latest_year)


            # Process all courses for display
            for academic_year in sorted_years:
                year_display = academic_year.replace('-', '/')
                courses[academic_year] = {'display': year_display, 'semesters': {}}
                
                for semester_index, semester_data in enumerate(courses_data[academic_year]):
                    if isinstance(semester_data, dict):
                        semester_courses = []
                        for code, course_info in semester_data.items():
                            unique_course_key = f"{code}_{academic_year}_{semester_index}"
                            lecturers = course_info.get('lecturers', {})
                            lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                            venue_time = course_info.get('venue and time', {})
                            venue_time = [vt for vt in venue_time if vt is not None]
                            lecturer_count = len(lecturers)
                            semester_courses.append({
                                'course_code': code,
                                'course_name': course_info.get('course_name', ''),
                                'lecturers': lecturers,
                                'lecturer_count': lecturer_count,
                                'venue_time': venue_time,
                                'student_count': course_student_counts.get(unique_course_key, 0)  # Use the semester-specific count
                            })
                            
                        if semester_courses:
                            courses[academic_year]['semesters'][str(semester_index)] = semester_courses

            # Get latest courses for dropdown
            if latest_semester is not None:
                latest_semester_courses = courses_data[latest_year][latest_semester]
                if isinstance(latest_semester_courses, dict):
                    for code, course_info in latest_semester_courses.items():
                        latest_courses.append({
                            'course_code': code,
                            'course_name': course_info.get('course_name', '')
                        })
            
            # Get student's courses if user is a student
            if request.session.get('user_role') == 'student':
                user_email = get_current_user(request)
                encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
                user_courses = database.child("users").child(encoded_email).child("courses").get().val()
                student_courses = []
                if user_courses and isinstance(user_courses, dict):
                    for course in user_courses.values():
                        student_courses.append({
                            'course_code': course.get('course_code', ''),
                            'academic_year': course.get('academic_year', ''),
                            'semester': course.get('semester', '')  # Add semester to the data structure
                        })
                    # Sort by academic year to get the earliest year first
                    student_courses.sort(key=lambda x: x['academic_year'])

    except Exception as e:
        print(f"Error fetching courses: {e}")
        print(f"Latest year: {latest_year}")
        print(f"Latest semester: {latest_semester}")
   
    context = {
        'courses': courses,
        'latest_courses': latest_courses,
        'student_courses': student_courses,
        'latest_year': latest_year,
        'latest_semester': latest_semester
    }

    print("this is student courses", student_courses)

    return render(request, 'academic.html', context)

def course_detail_view(request, semester_year, course_code):
    try:
        academic_year, semester = semester_year.split('sem')
        semester = semester[0] 
        academic_year = semester_year[semester_year.index("year") + 4:]

        courses_data = database.child("course").get().val()
        courses = []
        enrolled_students = []
        courseworks_data = {}
        processed_courseworks = []

        # Handle POST request for course update
        if request.method == 'POST':
            try:
                # Get form data
                course_name = request.POST.get('course_name')
                
                # Get lecturer data
                lecturers = []
                i = 1
                while f'lecturer_name{i}' in request.POST:
                    lecturer = {
                        'lecturer_name': request.POST.get(f'lecturer_name{i}'),
                        'lecturer_email': request.POST.get(f'lecturer_email{i}')
                    }
                    lecturers.append(lecturer)
                    i += 1

                # Get venue and time data
                venue_time = []
                i = 1
                while f'class_venue{i}' in request.POST:
                    class_info = {
                        'class_venue': request.POST.get(f'class_venue{i}'),
                        'class_day': request.POST.get(f'class_day{i}'),
                        'class_start_time': request.POST.get(f'class_start_time{i}'),
                        'class_end_time': request.POST.get(f'class_end_time{i}')
                    }
                    venue_time.append(class_info)
                    i += 1

                # Update course in Firebase
                course_ref = database.child("course").child(academic_year).child(semester).child(course_code)
                
                update_data = {
                    'course_name': course_name,
                    'lecturers': lecturers,
                    'venue and time': venue_time
                }
                
                course_ref.update(update_data)

                return JsonResponse({
                    'status': 'success',
                    'message': 'Course updated successfully!'
                }, safe=False)

            except Exception as e:
                print(f"Error updating course: {e}")
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, safe=False)

        # Process course data
        if courses_data:
            for year, semesters in courses_data.items():
                if year == academic_year:
                    for semester_index, courses_in_semester in enumerate(semesters):
                        if str(semester_index) == semester:
                            if isinstance(courses_in_semester, dict):
                                for code, course_info in courses_in_semester.items():
                                    if code == course_code:
                                        # Process courseworks
                                        courseworks_data = course_info.get('courseworks', {})
                                        if isinstance(courseworks_data, dict):
                                            for coursework_id, cw in courseworks_data.items():
                                                if cw and isinstance(cw, dict):
                                                    processed_courseworks.append({
                                                        'type': cw['type'],
                                                        'total_mark': cw['total_mark'],
                                                        'field_name': cw['type'].replace(' ', '_')
                                                    })

                                        # Process course details
                                        courses.append({
                                            'semester_year': semester_year,
                                            'academic_year': year.replace('-', '/'),
                                            'semester': str(semester_index),
                                            'course_code': code,
                                            'course_name': course_info.get('course_name', ''),
                                            'lecturers': [l for l in course_info.get('lecturers', []) if l],
                                            'venue_time': [vt for vt in course_info.get('venue and time', []) if vt],
                                            'courseworks': processed_courseworks
                                        })

        # Process enrolled students
        users = database.child("users").get().val()
        if users:
            for email_key, user_data in users.items():
                if user_data.get('role') == 'student' and 'courses' in user_data:
                    for course_key, course_info in user_data['courses'].items():
                        if (course_info.get('course_code') == course_code and 
                            course_info.get('academic_year') == academic_year and 
                            course_info.get('semester') == semester):
                            
                            student_data = {
                                'name': user_data.get('name', ''),
                                'matrix': user_data.get('matrix', ''),
                                'email': user_data.get('email', ''),
                                'marks': {},
                                'total_mark': 0
                            }
                            
                            coursework_data = course_info.get('coursework', {})
                            
                            if isinstance(coursework_data, dict):
                                for coursework_type, mark in coursework_data.items():
                                    student_data['marks'][coursework_type] = mark
                            
                            student_data['total_mark'] = sum(student_data['marks'].values())

                            enrolled_students.append(student_data)
        
        total_marks = sum(cw['total_mark'] for cw in courses[0]['courseworks'])

        # Always return a response
        context = {
            'courses': courses,
            'course_code': course_code,
            'academic_year': academic_year,
            'semester': semester,
            'semester_year': semester_year,
            'enrolled_students': enrolled_students,
            'error': None if courses else 'Course not found',
            'total_marks': total_marks
        }
        return render(request, 'course-detail.html', context)

    except Exception as e:
        print(f"Error in course detail view: {e}")
        return render(request, 'course-detail.html', {
            'error': f'An error occurred: {str(e)}'
        })
    

def analytics_detail_view(request, semester_year, course_code):
    model_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'model.pkl')

    model = joblib.load(model_path)

    predictions = []

    try:
        if request.method == 'POST':
            data1 = float(request.POST.get('data1'))
            data2 = float(request.POST.get('data2'))
            data3 = float(request.POST.get('data3'))
            data4 = float(request.POST.get('data4'))
            data5 = float(request.POST.get('data5'))
            data6 = float(request.POST.get('data6'))
            data7 = float(request.POST.get('data7'))
            data8 = float(request.POST.get('data8'))
            data9 = float(request.POST.get('data9'))
            data10 = float(request.POST.get('data10'))
            data11 = float(request.POST.get('data11'))
            input_data = [[data1, data2, data3, data4, data5, data6, data7, data8, data9, data10, data11]]

            predictions = model.predict(input_data)

        academic_year, semester = semester_year.split('sem')
        semester = semester[0] 
        academic_year = semester_year[semester_year.index("year") + 4:]

        courses_data = database.child("course").get().val()
        courses = []
        enrolled_students = []
        courseworks_data = {}
        processed_courseworks = []

        # Process course data
        if courses_data:
            for year, semesters in courses_data.items():
                if year == academic_year:
                    for semester_index, courses_in_semester in enumerate(semesters):
                        if str(semester_index) == semester:
                            if isinstance(courses_in_semester, dict):
                                for code, course_info in courses_in_semester.items():
                                    if code == course_code:
                                        # Process courseworks
                                        courseworks_data = course_info.get('courseworks', {})
                                        if isinstance(courseworks_data, dict):
                                            for coursework_id, cw in courseworks_data.items():
                                                if cw and isinstance(cw, dict):
                                                    processed_courseworks.append({
                                                        'type': cw['type'],
                                                        'total_mark': cw['total_mark'],
                                                        'field_name': cw['type'].replace(' ', '_')
                                                    })

                                        # Process course details
                                        courses.append({
                                            'semester_year': semester_year,
                                            'academic_year': year.replace('-', '/'),
                                            'semester': str(semester_index),
                                            'course_code': code,
                                            'course_name': course_info.get('course_name', ''),
                                            'lecturers': [l for l in course_info.get('lecturers', []) if l],
                                            'venue_time': [vt for vt in course_info.get('venue and time', []) if vt],
                                            'courseworks': processed_courseworks
                                        })

        # Process enrolled students
        users = database.child("users").get().val()
        if users:
            for email_key, user_data in users.items():
                if user_data.get('role') == 'student' and 'courses' in user_data:
                    for course_key, course_info in user_data['courses'].items():
                        if (course_info.get('course_code') == course_code and 
                            course_info.get('academic_year') == academic_year and 
                            course_info.get('semester') == semester):
                            
                            student_data = {
                                'name': user_data.get('name', ''),
                                'matrix': user_data.get('matrix', ''),
                                'email': user_data.get('email', ''),
                                'marks': {},
                                'total_mark': 0
                            }
                            
                            coursework_data = course_info.get('coursework', {})
                            
                            if isinstance(coursework_data, dict):
                                for coursework_type, mark in coursework_data.items():
                                    student_data['marks'][coursework_type] = mark
                            
                            student_data['total_mark'] = sum(student_data['marks'].values())

                            enrolled_students.append(student_data)

        total_marks = sum(cw['total_mark'] for cw in courses[0]['courseworks'])

        # Always return a response
        context = {
            'courses': courses,
            'course_code': course_code,
            'academic_year': academic_year,
            'semester': semester,
            'semester_year': semester_year,
            'enrolled_students': enrolled_students,
            'error': None if courses else 'Course not found',
            'predictions': predictions,
            'total_marks': total_marks
        }
        return render(request, 'analytics-detail.html', context)

    except Exception as e:
        print(f"Error in course detail view: {e}")
        return render(request, 'analytics-detail.html', {
            'error': f'An error occurred: {str(e)}'
        })

def delete_course_view(request, semester_year, course_code):
    if request.method == 'POST':
        try:
            # Extract academic year and semester from semester_year
            academic_year = semester_year.replace('sem1year', '').replace('sem2year', '')
            semester = '1' if 'sem1year' in semester_year else '2'
            
            # 1. First, get all users
            users = database.child("users").get().val()
            if users:
                # Iterate through all users
                for user_email, user_data in users.items():
                    if 'courses' in user_data:
                        courses = user_data['courses']
                        # Iterate through user's courses
                        for course_key, course_info in courses.items():
                            # Check if this is the course to be deleted
                            if (course_info.get('course_code') == course_code and 
                                course_info.get('academic_year') == academic_year and 
                                course_info.get('semester') == semester):
                                # Delete this course from user's data
                                database.child("users").child(user_email).child("courses").child(course_key).remove()

            # Check user role
            if request.session.get('user_role') == 'admin':
                # 2. Then delete the course from courses database
                database.child("course").child(academic_year).child(semester).child(course_code).remove()
                message = f'Course {course_code} has been successfully deleted.'
            else:
                message = f'You have been successfully unenrolled from {course_code}.'
            
            return JsonResponse({
                'status': 'success',
                'message': message
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def tools_view(request):
    return render(request, 'Tools/tools.html')

def appointments_view(request):
    return render(request, 'appointments.html')

def forum_view(request):
    user_email = get_current_user(request)
    search_query = request.GET.get('search', '')  # Get the search query from the URL
    posts = getPosts()  # Call the getPosts function to retrieve posts

    # Filter posts based on the search query in title or subject
    if search_query:
        posts = [post for post in posts if search_query.lower() in post['title'].lower() or search_query.lower() in post['subject'].lower()]

    return render(request, "Tools/Forum/forum.html", {"user_email": user_email, "posts": posts, "search_query": search_query})

def getSubject():
    subject = database.child("forum").child("posts").get()

def analytics_view(request):
    # Get latest courses for student selection
    latest_courses = []
    student_courses = []
    courses = {}
    latest_year = None
    latest_semester = None

    try:
        courses_data = database.child("course").get().val()
        if courses_data:
            # Get all users to count students per course
            users_data = database.child("users").get().val()
            course_student_counts = {}
            
            # Count students for each course, considering semester
            if users_data:
                for user_key, user_info in users_data.items():
                    if user_info.get('role') == 'student' and 'courses' in user_info:
                        for course_key, course_info in user_info['courses'].items():
                            course_code = course_info.get('course_code')
                            course_semester = course_info.get('semester')
                            course_year = course_info.get('academic_year')
                            if course_code and course_semester and course_year:
                                # Create a unique key combining course code, year, and semester
                                unique_course_key = f"{course_code}_{course_year}_{course_semester}"
                                course_student_counts[unique_course_key] = course_student_counts.get(unique_course_key, 0) + 1

            # Get latest academic year
            sorted_years = sorted(courses_data.keys(), reverse=True)
            latest_year = sorted_years[0]
            
            # Get latest semester
            latest_semester = get_latest_semester(courses_data, latest_year)

            # Process all courses for display
            for academic_year in sorted_years:
                year_display = academic_year.replace('-', '/')
                courses[academic_year] = {'display': year_display, 'semesters': {}}
                
                for semester_index, semester_data in enumerate(courses_data[academic_year]):
                    if isinstance(semester_data, dict):
                        semester_courses = []
                        for code, course_info in semester_data.items():
                            unique_course_key = f"{code}_{academic_year}_{semester_index}"
                            lecturers = course_info.get('lecturers', {})
                            lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                            venue_time = course_info.get('venue and time', {})
                            venue_time = [vt for vt in venue_time if vt is not None]
                            lecturer_count = len(lecturers)
                            semester_courses.append({
                                'course_code': code,
                                'course_name': course_info.get('course_name', ''),
                                'lecturers': lecturers,
                                'lecturer_count': lecturer_count,
                                'venue_time': venue_time,
                                'student_count': course_student_counts.get(unique_course_key, 0)  # Use the semester-specific count
                            })
                            
                        if semester_courses:
                            courses[academic_year]['semesters'][str(semester_index)] = semester_courses

            # Get latest courses for dropdown
            if latest_semester is not None:
                latest_semester_courses = courses_data[latest_year][latest_semester]
                if isinstance(latest_semester_courses, dict):
                    for code, course_info in latest_semester_courses.items():
                        latest_courses.append({
                            'course_code': code,
                            'course_name': course_info.get('course_name', '')
                        })
            
            # Get student's courses if user is a student
            if request.session.get('user_role') == 'student':
                user_email = get_current_user(request)
                encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
                user_courses = database.child("users").child(encoded_email).child("courses").get().val()
                student_courses = []
                if user_courses and isinstance(user_courses, dict):
                    for course in user_courses.values():
                        student_courses.append({
                            'course_code': course.get('course_code', ''),
                            'academic_year': course.get('academic_year', ''),
                            'semester': course.get('semester', '')  # Add semester to the data structure
                        })
                    # Sort by academic year to get the earliest year first
                    student_courses.sort(key=lambda x: x['academic_year'])

    except Exception as e:
        print(f"Error fetching courses: {e}")
        print(f"Latest year: {latest_year}")
        print(f"Latest semester: {latest_semester}")
   
    context = {
        'courses': courses,
        'latest_courses': latest_courses,
        'student_courses': student_courses,
        'latest_year': latest_year,
        'latest_semester': latest_semester
    }

    print("this is student courses", student_courses)

    return render(request, 'analytics.html', context)

def users_management_view(request):
    return render(request, 'users-management.html')

@login_required
def profile_view(request):
    try:
        user_email = get_current_user(request)
        encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
        
        if request.method == 'POST':
            try:
                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    profile_pic = request.FILES['profile_picture']
                    import base64
                    profile_pic_base64 = base64.b64encode(profile_pic.read()).decode('utf-8')
                    database.child("users").child(encoded_email).update({
                        "profile_picture": profile_pic_base64
                    })
                
                # Handle other profile updates
                name = request.POST.get('name')
                gender = request.POST.get('gender')
                birthday = request.POST.get('birthday')
                major = request.POST.get('major')
                matrix = request.POST.get('matrix')
                identity = request.POST.get('identity')

                user_data = {
                    'name': name,
                    'gender': gender,
                    'birthday': birthday,
                    'major': major,
                    'matrix': matrix,
                    'identity': identity
                }
                database.child("users").child(encoded_email).update(user_data)
                
                # Check if it's an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Profile updated successfully!'
                    })
                else:
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('profile')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    })
                else:
                    messages.error(request, str(e))
                    return redirect('profile')

        # Get user data
        user_data = database.child("users").child(encoded_email).get().val()
         # Transform gender and major values if user_data exists
        if user_data:
            # Transform gender
            if 'gender' in user_data:
                if user_data['gender'] == 'M':
                    user_data['gender'] = 'Male'
                elif user_data['gender'] == 'F':
                    user_data['gender'] = 'Female'
            
        if not user_data:
            messages.error(request, 'User data not found')
            return redirect('login')

        return render(request, 'profile.html', {
            'user': user_data,
            'default_image': 'image/user.png'
        })

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('dashboard')

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

def createpost_view(request):
    if request.method == 'POST':
        print(request.POST)
        try:
            # Get form data
            subject = request.POST.get('subject')
            title = request.POST.get('title')
            content = request.POST.get('content')
            tags = json.loads(request.POST.get('tags', '[]'))
            author_email = get_current_user(request)
            
            # Get current timestamp
            current_timestamp =int(datetime.datetime.now(pytz.UTC).timestamp() * 1000)
            formatted_date = datetime.datetime.fromtimestamp(current_timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S')
            print("Current Timestamp:", current_timestamp)

            # Retrieve all posts
            all_posts = database.child("forum").get()
            
            # Find the maximum PostID
            max_post_id = 0
            if all_posts.val() and 'posts' in all_posts.val():
                posts = all_posts.val()['posts']
                max_post_id = max(
                    post.get('PostID', 0) for post in posts.values()
                )
            
            # Increment to get next PostID
            next_post_id = max_post_id + 1
     
            # Create post data
            post_data = {
                "PostID": next_post_id,
                "subject": subject,
                "title": title,
                "content": content,
                "tags": tags,
                "author": author_email,
                "timestamp": formatted_date,
            }
            
            # Save to Firebase
            database.child("forum").child("posts").push(post_data)
            
            # Set success message
            success_message = "Post created successfully!"
            return render(request, 'Tools/Forum/createPost.html', {'success_message': success_message})
        except Exception as e:
            print(f"Error creating post: {e}")
            return render(request, 'Tools/Forum/createPost.html', {'error': str(e)})
            
    return render(request, 'Tools/Forum/createPost.html')

def getPosts():
    posts = database.child("forum").child("posts").get()
    #check if post exist
    if posts.val():
        post_list = []
        for post in posts.each():
            post_data = post.val()
            # Count replies if 'replies' key exists
            replies = post_data.get("replies", {})
            reply_count = len(replies) if isinstance(replies, dict) else 0
            # Add reply count to the post data
            post_data['reply_count'] = reply_count
            post_list.append(post_data)
            print(post_list)
    else:
        post_list=[]  
    return post_list  

def viewPost(request, post_id):
    try:
        posts = database.child("forum").child("posts").get()
        if posts.val():
            # Convert posts to a list of dictionaries
            post_list = [post.val() for post in posts.each()]
            # Find the post with the matching PostID
            post = next((p for p in post_list if p.get("PostID") == post_id), None)
            if post:
                return render(request, 'Tools/Forum/viewPost.html', {'post': post})
        return render(request, 'Tools/Forum/viewPost.html', {'error': 'Post not found'})
    except Exception as e:
        print(f"Error fetching post: {e}")
        return render(request, 'Tools/Forum/viewPost.html', {'error': 'An error occurred'})

def submit_comment(request, post_id):
    if request.method == 'POST':
        try:
            # Get the comment content from the request
            content = request.POST.get('content')  # Get the comment content
            user_email = get_current_user(request)
            # Get current timestamp
            current_timestamp = int(datetime.datetime.now(pytz.UTC).timestamp() * 1000)
            formatted_date = datetime.datetime.fromtimestamp(current_timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S')

            # Reference to the specific post in Firebase using post_id
            post_data = database.child("forum").child("posts").order_by_child("PostID").equal_to(post_id).get().val()
            if post_data:
                post_key = list(post_data.keys())[0] 
                # Push the reply to the post's replies
                reply_data = {
                    "content": content,
                    "author": user_email,
                    "timestamp": formatted_date
                }

                database.child("forum").child("posts").child(post_key).child("replies").push(reply_data)

                # Update the comments count if needed
                current_count = post_data.get("comments_count", 0)
                new_count = current_count + 1
                post_data.update({"comments_count": new_count})

                  # Add a success message
                print("Adding success message") 
                messages.success(request, "Comment added successfully!")
                
                # Redirect to the forum page
                return redirect('forum')  
            else:
                return render({'status': 'error', 'message': 'Post not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def timetable_view(request):
    # Fetch course data from the database
    courses_data = database.child("course").get().val()
    subject_codes = []

    # Find the latest academic year and semester
    if courses_data:
        # Sort academic years in descending order
        sorted_years = sorted(courses_data.keys(), reverse=True)
        latest_year = sorted_years[0] if sorted_years else None

        if latest_year:
            semesters = courses_data[latest_year]
            # Find the highest semester number
            latest_semester = max(range(len(semesters)), key=lambda x: x if isinstance(semesters[x], dict) else -1)

            # Process only the latest year and semester
            courses_in_semester = semesters[latest_semester]
            if isinstance(courses_in_semester, dict):
                for code, course_info in courses_in_semester.items():
                    lecturers = course_info.get('lecturers', [])
                    lecturers = [lecturer for lecturer in lecturers if lecturer]
                    venue_time = course_info.get('venue and time', [])
                    
                    if isinstance(venue_time, dict):
                        venue_time = [vt for vt in venue_time.values() if vt]
                    else:
                        venue_time = [vt for vt in venue_time if vt]

                    lecturer_count = len(lecturers)
                    subject_codes.append({
                        'course_code': code,
                        'course_name': course_info.get('course_name', ''),
                        'lecturers': lecturers,
                        'lecturer_count': lecturer_count,
                        'venue_time': venue_time
                    })

    # Handle timetable generation
    timetable_html = None
    if request.method == 'POST':
        selected_courses = request.POST.getlist('course')
        if selected_courses:
            #call function  generate_timetable
            timetable_html = generate_timetable(selected_courses, subject_codes, request)
            return render(request, 'Tools/Timetable/index.html', {
                'courses': subject_codes,
                'timetable': timetable_html,
                'selected_courses': selected_courses
            })

    return render(request, 'Tools/Timetable/index.html', {
        'courses': subject_codes,
        'timetable': None
    })

def generate_timetable(selected_courses, subject_codes, request):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    def generate_pastel_color():
        hue = random.random()
        saturation = 0.3 + random.random() * 0.2
        value = 0.9 + random.random() * 0.1
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    
    course_colors = {course: generate_pastel_color() for course in selected_courses}
    #create empty set(timeslots)
    time_slots = set() 

    # Create time slots from selected courses
    for course_code in selected_courses:
        #for loop course in subject_codes if the course_code(subject code ) same as the request course code
        course_info = next((course for course in subject_codes if course['course_code'] == course_code), None)
        if course_info:
            for vt in course_info.get('venue_time'):
                #if both start &end time exist add to the timeslot
                if 'class_start_time' in vt and 'class_end_time' in vt:
                    time_slots.add(f"{vt['class_start_time']} - {vt['class_end_time']}")
    
    #sort in ascending order
    time_slots = sorted(list(time_slots))

    print(time_slots)
    
    #defines a dictionary for loop the days and slot 
    timetable = {day: {slot: [] for slot in time_slots} for day in days}

    for course_code in selected_courses:
        course_info = next((course for course in subject_codes if course['course_code'] == course_code), None)
        if course_info:
            for vt in course_info['venue_time']:
                day = vt.get('class_day')
                time_slot = f"{vt['class_start_time']} - {vt['class_end_time']}"
                venue = vt.get('class_venue', '')

                if day in timetable and time_slot in timetable[day]:
                    timetable[day][time_slot].append({
                        'code': course_info['course_code'],
                        'venue': venue,
                        'color': course_colors[course_code]
                    })

    # Generate HTML for the timetable
    table_html = '<table class="timetable-colored">'
    table_html += '<tr><th class="time-column">Time</th>'
    for day in days:
        table_html += f'<th class="day-column">{day}</th>'
    table_html += '</tr>'

    for time in time_slots:
        table_html += '<tr>'
        table_html += f'<td class="time-column">{time}</td>'
        for day in days:
            cell_content = timetable[day][time]
            if cell_content:
                td_content = '<td class="course-column">'
                for course in cell_content:
                    td_content += f'''
                        <div style="background-color: {course["color"]}; padding: 5px; margin: 2px; border-radius: 4px;">
                            <div class="course-code">{course["code"]}</div>
                            <div class="venue-text">({course["venue"]})</div>
                        </div>'''
                td_content += '</td>'
                table_html += td_content
            else:
                table_html += '<td class="course-column"></td>'
        table_html += '</tr>'
    table_html += '</table>'

    table_html = f'''
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
            .course-column {{ width: 13%; }}
            .time-column {{ width: 9%; }}
            .course-code {{ font-weight: bold; }}
            .venue-text {{ font-size: 0.9em; }}
        </style>
    </head>
    <body>
        {table_html}
    </body>
    </html>
    '''
    request.session['timetable_html'] = table_html
    
    return table_html

def download_timetable(request):
    if request.method == 'POST':
        # Get the HTML content from session
        html_content = request.session.get('timetable_html')
        
        if html_content:
            # Create PDF
            buffer = BytesIO()
            pisa.CreatePDF(html_content, dest=buffer)
            pdf = buffer.getvalue()
            buffer.close()
            
            # Create response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="timetable.pdf"'
            response.write(pdf)
            
            return response

    return HttpResponse('No timetable data found', status=400)

def cgpa_view(request):
    grading = [
        ("A", 4.00),
        ("A-", 3.67),
        ("B+", 3.33),
        ("B", 3.00),
        ("B-", 2.67),
        ("C+", 2.33),
        ("C", 2.00),
        ("C-", 1.67),
        ("D+", 1.33),
        ("D", 1.00),
        ("D-", 0.67),
        ("F", 0.00)
    ]
    return render(request, 'Tools/CGPA/index.html', {
        'grading': grading,
    })

def is_valid_usm_email(email):
    """Validate that email is from USM domain"""
    valid_domains = ['@student.usm.my', '@usm.my']
    email = email.lower()
    return any(email.endswith(domain) for domain in valid_domains)

def test_database_connection(request):
    try:
        # Test Pyrebase connection
        test_data = database.child("test").get()
        logger.info("Pyrebase connection successful")
        
        # Test Firebase Admin SDK connection
        ref = admin_db.reference('/test')
        ref.get()
        logger.info("Firebase Admin SDK connection successful")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Database connection successful'
        })
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def delete_profile(request):
    if request.method == 'POST':
        try:
            user_email = get_current_user(request)
            encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
            
            # Delete from Realtime Database
            database.child("users").child(encoded_email).remove()
            
            # Delete from Authentication
            user = auth.get_user_by_email(user_email)
            auth.delete_user(user.uid)
            
            # Clear session
            request.session.flush()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Account deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

def check_course(request):
    try:
        code = request.GET.get('code')
        semester = request.GET.get('semester')
        year = request.GET.get('year').replace('/', '-')
        
        # Check if course exists in database
        course_ref = database.child("course").child(year).child(semester).child(code).get()
        
        return JsonResponse({
            'exists': bool(course_ref.val())
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def check_student_course(request):
    try:
        code = request.GET.get('code')
        semester = request.GET.get('semester')
        year = request.GET.get('year')
        
        user_email = get_current_user(request)
        encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
        
        # Get user's courses
        user_courses = database.child("users").child(encoded_email).child("courses").get().val()
        
        # Check if course exists in user's courses for the specific semester and year
        exists = False
        if user_courses:
            for course in user_courses.values():
                if (course.get('course_code') == code and 
                    course.get('semester') == semester and 
                    course.get('academic_year') == year):
                    exists = True
                    break
                    
        return JsonResponse({
            'exists': exists
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def update_marks(request, semester_year, course_code, student_email):
    if request.method == 'POST':
        try:
            # Debug prints
            print("POST data:", request.POST)
            
            # Parse academic year and semester
            academic_year = semester_year[semester_year.index("year") + 4:]
            semester = semester_year[semester_year.index("sem") + 3:semester_year.index("year")]
            
            # Get student reference
            encoded_email = student_email.replace('.', '-dot-').replace('@', '-at-')
            
            # Get course data to get coursework types
            course_data = database.child("course").child(academic_year).child(semester).child(course_code).get().val()
            print("Course data:", course_data)
            
            if not course_data or 'courseworks' not in course_data:
                raise ValueError("Course or coursework data not found")
            
            # Get all student courses
            student_courses = database.child("users").child(encoded_email).child("courses").get().val()
            
            # Find the target course
            target_course_key = None
            for key, course in student_courses.items():
                if (course.get('course_code') == course_code and 
                    course.get('academic_year') == academic_year and 
                    course.get('semester') == semester):
                    target_course_key = key
                    break
            
            # Get the marks from POST data using the actual coursework types
            marks = {}
            print("Processing courseworks:", course_data['courseworks'])
            
            for coursework in course_data['courseworks'].values():
                coursework_type = coursework['type']
                # Change underscore to hyphen in the mark_key
                mark_key = f"mark_{coursework_type.lower().replace(' ', '-')}"
                print(f"Looking for mark_key: {mark_key}")
                print(f"Available POST keys: {request.POST.keys()}")
                
                if mark_key in request.POST and request.POST[mark_key].strip():
                    try:
                        mark_value = float(request.POST[mark_key])
                        print(f"Found value for {coursework_type}: {mark_value}")
                        if 0 <= mark_value <= float(coursework['total_mark']):
                            marks[coursework_type] = mark_value
                        else:
                            messages.error(request, f'Mark for {coursework_type} must be between 0 and {coursework["total_mark"]}')
                            return redirect('course-detail', semester_year=semester_year, course_code=course_code)
                    except ValueError:
                        messages.error(request, f'Invalid mark value for {coursework_type}')
                        return redirect('course-detail', semester_year=semester_year, course_code=course_code)
            
            print("Final marks dict:", marks)
            
            # Update the marks in database
            if marks:
                database.child("users").child(encoded_email).child("courses").child(target_course_key).child("coursework").update(marks)
                messages.success(request, 'Marks updated successfully')
            else:
                messages.warning(request, 'No marks to update')
            
        except Exception as e:
            print(f"Error updating marks: {str(e)}")
            messages.error(request, f'Error updating marks: {str(e)}')
            
        return redirect('course-detail', semester_year=semester_year, course_code=course_code)
    
    return redirect('course-detail', semester_year=semester_year, course_code=course_code)

@require_POST
def unenroll_student(request):
    try:
        data = json.loads(request.body)
        student_email = data.get('student_email')
        course_code = data.get('course_code')
        academic_year = data.get('academic_year')
        semester = data.get('semester')

        # Encode the email address to match Firebase structure
        encoded_email = student_email.replace('.', '-dot-').replace('@', '-at-')

        # Get the user's courses
        user_courses = database.child("users").child(encoded_email).child("courses").get().val()
        
        if user_courses:
            # Find and delete the specific course
            for course_key, course_info in user_courses.items():
                # Print debug information
                print(f"Checking course: {course_info}")
                print(f"Looking for: code={course_code}, year={academic_year}, sem={semester}")
                
                # Match exact values from the database structure
                if (course_info.get('course_code') == course_code and 
                    course_info.get('academic_year') == academic_year.replace('/', '-') and  # Convert 2025/2026 to 2025-2026
                    str(course_info.get('semester')) == str(semester)):  # Ensure both are strings
                    
                    # Delete this specific course
                    database.child("users").child(encoded_email).child("courses").child(course_key).remove()
                    return JsonResponse({'status': 'success', 'message': 'Student unenrolled successfully'})
        
        return JsonResponse({'status': 'error', 'message': 'Course not found'})

    except Exception as e:
        print(f"Error in unenroll_student: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def upload_marks(request, semester_year, course_code):
    try:
        if 'csvFile' not in request.FILES:
            return JsonResponse({'status': 'error', 'message': 'No file uploaded'})

        csv_file = TextIOWrapper(request.FILES['csvFile'].file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        
        # Parse semester_year format
        try:
            semester = semester_year[3:4]
            academic_year = semester_year[8:]
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Invalid semester_year format: {semester_year}. Expected format: sem[1-2]year[YYYY-YYYY]'
            })
        
        # Get course data
        course = database.child("course").child(academic_year).child(semester).child(course_code).get().val()
        if not course:
            return JsonResponse({'status': 'error', 'message': f'Course not found: {semester}, {academic_year}, {course_code}'})

        # Get coursework types and clean them
        courseworks = {}
        if 'courseworks' in course:
            for cw_key, cw_data in course['courseworks'].items():
                if isinstance(cw_data, dict) and 'type' in cw_data and 'total_mark' in cw_data:
                    # Store the coursework type and its total mark
                    coursework_type = cw_data['type'].strip()
                    courseworks[coursework_type] = float(cw_data['total_mark'])

        if not courseworks:
            return JsonResponse({'status': 'error', 'message': 'No coursework types found in course configuration'})

        # Clean CSV headers by removing percentages and match with course courseworks
        cleaned_headers = {}
        for header in reader.fieldnames:
            if header == 'Matrix Number':
                cleaned_headers[header] = header
                continue

            # Remove percentage and clean the header
            clean_header = header.split('(')[0].strip() if '(' in header else header.strip()
            
            # Check if this header matches any coursework type (case-insensitive)
            for coursework_type in courseworks.keys():
                if clean_header.lower() == coursework_type.lower():
                    cleaned_headers[header] = coursework_type
                    break

        if len(cleaned_headers) <= 1:  # Only Matrix Number found
            return JsonResponse({
                'status': 'error',
                'message': 'No valid coursework columns found in CSV. Headers should match coursework types in course configuration.'
            })

        success_count = 0
        errors = []

        for row in reader:
            try:
                matrix = row['Matrix Number'].strip()
                
                # Find student by matrix number
                student_ref = None
                students = database.child("users").get().val()
                for email, data in students.items():
                    if 'matrix' in data and data['matrix'] == matrix:
                        student_ref = email
                        break

                if not student_ref:
                    errors.append(f"Student with matrix {matrix} not found")
                    continue

                # Update marks
                marks = {}
                for original_header, coursework_type in cleaned_headers.items():
                    if coursework_type != 'Matrix Number' and original_header in row:
                        try:
                            mark = float(row[original_header])
                            max_mark = courseworks[coursework_type]
                            if 0 <= mark <= max_mark:
                                marks[coursework_type] = mark
                            else:
                                errors.append(f"Invalid mark for {matrix}: {coursework_type} mark must be between 0 and {max_mark}")
                                continue
                        except ValueError:
                            errors.append(f"Invalid mark format for {matrix}: {coursework_type}")
                            continue

                # Find the course key in student's courses
                student_courses = database.child("users").child(student_ref).child("courses").get().val()
                course_key = None
                if student_courses:
                    for key, course_data in student_courses.items():
                        if (course_data.get('course_code') == course_code and 
                            course_data.get('academic_year') == academic_year and 
                            str(course_data.get('semester')) == semester):
                            course_key = key
                            break

                if course_key:
                    # Update marks in database
                    database.child("users").child(student_ref).child("courses").child(course_key).child("coursework").update(marks)
                    success_count += 1
                else:
                    errors.append(f"Student {matrix} is not enrolled in this course")

            except Exception as e:
                errors.append(f"Error processing student {matrix}: {str(e)}")

        # Prepare response message
        message = f"Successfully updated marks for {success_count} students."
        if errors:
            message += f"\nErrors encountered:\n" + "\n".join(errors)

        return JsonResponse({
            'status': 'success' if success_count > 0 else 'error',
            'message': message
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_latest_semester(courses_data, latest_year):
    """
    Retrieve the latest semester index from the courses data for the given year.

    Args:
        courses_data (dict): The data structure containing course information.
        latest_year (int): The year for which to find the latest semester.

    Returns:
        int or None: The index of the latest semester, or None if not found.
    """
    latest_semester = None
    if latest_year in courses_data:
        for i in range(len(courses_data[latest_year])):
            if isinstance(courses_data[latest_year][i], dict):
                latest_semester = i
    return latest_semester

@require_POST
def add_achievement(request):
    try:
        # Get the current user's email
        user_email = get_current_user(request)
        if not user_email:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'})

        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        proof_file = request.FILES.get('proof')

        if not title or not description:
            return JsonResponse({'status': 'error', 'message': 'Title and description are required'})

        try:
            # Convert email to database format
            encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
            
            # Handle file upload
            proof_url = None
            if proof_file:
                file_content = proof_file.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
                proof_url = file_base64

            # Get current timestamp for sorting
            current_time = datetime.datetime.now()
            timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Create achievement data
            achievement_data = {
                'title': title,
                'description': description,
                'proof': proof_url,
                'date_added': timestamp
            }

            # Generate timestamp-based ID for natural descending order
            # Using inverse timestamp (max timestamp - current timestamp)
            max_timestamp = "9999-12-31 23:59:59"
            inverse_timestamp = datetime.datetime.strptime(max_timestamp, '%Y-%m-%d %H:%M:%S') - current_time
            
            # Convert to total seconds and format as hex for compact storage
            seconds = int(inverse_timestamp.total_seconds())
            timestamp_hex = f"{seconds:08x}"  # 8 characters of hex
            
            # Add random suffix for uniqueness
            random_suffix = uuid.uuid4().hex[:12]  # 12 characters of random hex
            
            # Combine to create the achievement ID
            achievement_id = f"-{timestamp_hex}{random_suffix}"

            # Update directly under the user's node with the unique ID
            database.child("users").child(encoded_email).child("achievements").child(achievement_id).set(achievement_data)
            
            print(f"Achievement added for user: {encoded_email} with ID: {achievement_id}")  # Debug print
            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug print
            return JsonResponse({'status': 'error', 'message': f'Database error: {str(e)}'})

    except Exception as e:
        print(f"General error: {str(e)}")  # Debug print
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def delete_achievement(request, achievement_key):
    try:
        # Get the current user's email
        user_email = request.session.get('user_email')
        if not user_email:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'})

        # Convert email to database format
        encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')

        # Delete the achievement
        database.child("users").child(encoded_email).child("achievements").child(achievement_key).remove()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_GET
def view_certificate(request, achievement_key):
    try:
        # Get current user's email
        user_email = request.session.get('user_email')
        if not user_email:
            return HttpResponse('User not authenticated', status=401)

        # Convert email to database format
        encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')

        # Get the achievement data
        achievement = database.child("users").child(encoded_email).child("achievements").child(achievement_key).get().val()
        
        if not achievement or 'proof' not in achievement:
            return HttpResponse('Certificate not found', status=404)

        # Decode the base64 data
        try:
            file_data = base64.b64decode(achievement['proof'])
            
            # Improved file type detection
            if file_data[0:2] == b'\xff\xd8':  # JPEG signature (more general check)
                content_type = 'image/jpeg'
                ext = 'jpg'
                disposition = 'inline'
            elif file_data[0:8] == b'\x89PNG\r\n\x1a\n':  # PNG signature
                content_type = 'image/png'
                ext = 'png'
                disposition = 'inline'
            elif file_data[0:4] == b'%PDF':  # PDF signature
                content_type = 'application/pdf'
                ext = 'pdf'
                disposition = 'inline'
            else:
                # Additional check for JPEG files
                try:
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(file_data))
                    if img.format == 'JPEG':
                        content_type = 'image/jpeg'
                        ext = 'jpg'
                        disposition = 'inline'
                    else:
                        content_type = 'application/octet-stream'
                        ext = 'file'
                        disposition = 'attachment'
                except:
                    content_type = 'application/octet-stream'
                    ext = 'file'
                    disposition = 'attachment'
            
            # Create response
            response = HttpResponse(file_data, content_type=content_type)
            
            # Set filename and disposition based on file type
            filename = f"certificate_{achievement_key}.{ext}"
            response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
            
            # Add cache control headers to help with browser viewing
            response['Cache-Control'] = 'public, max-age=0'
            response['Pragma'] = 'public'
            
            return response

        except Exception as e:
            print(f"Error decoding certificate: {str(e)}")  # Debug print
            return HttpResponse(f'Error decoding certificate: {str(e)}', status=500)

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        return HttpResponse(f'Error: {str(e)}', status=500)

DEVIL_AI_API_KEY = '693550-4bddea-2efd1e-e5badd'
DEVIL_AI_BASE_URL = 'https://api.devil.ai/v1'

@require_POST
def start_mbti_test(request):
    try:
        # Generate new test link from Devil.ai
        response = requests.get(
            f'{DEVIL_AI_BASE_URL}/new_test',
            params={
                'api_key': DEVIL_AI_API_KEY,
                'notify_url': request.build_absolute_uri('/test-complete/'),
                'return_url': request.build_absolute_uri('/profile/'),
            }
        )

        if not response.ok:
            raise Exception('Failed to generate test')

        data = response.json()
        if data['meta']['success']:
            return JsonResponse({
                'status': 'success',
                'test_url': data['data']['test_url'],
                'test_id': data['data']['test_id']
            })
        else:
            raise Exception('API returned error')

    except Exception as e:
        print(f"Error starting test: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@require_POST
def check_test_result(request):
    try:
        data = json.loads(request.body)
        test_id = data.get('test_id')
        if not test_id:
            return JsonResponse({'status': 'error', 'message': 'No test ID provided'})

        # Check test result from Devil.ai
        response = requests.get(
            f'{DEVIL_AI_BASE_URL}/check_test',
            params={
                'api_key': DEVIL_AI_API_KEY,
                'test_id': test_id
            }
        )

        if not response.ok:
            raise Exception('Failed to check test result')

        result_data = response.json()
        if result_data['meta']['success']:
            # Get current time in the required format
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Extract and format personality data
            personality_data = {
                'type': result_data['data']['prediction'],
                'predictions': result_data['data']['predictions'],
                'conscious_traits': result_data['data']['trait_order_conscious'],
                'shadow_traits': result_data['data']['trait_order_shadow'],
                'matches': result_data['data']['matches'],
                'result_date': current_time,  # Use current time instead of API response
                'results_page': result_data['data']['results_page']
            }

            # Save to Firebase
            try:
                encoded_email = get_current_user(request).replace('.', '-dot-').replace('@', '-at-')
                database.child("users").child(encoded_email).update({
                    'personality': personality_data
                })
                print(f"Saved personality data for user {encoded_email}: {personality_data}")  # Debug log

                return JsonResponse({
                    'status': 'success',
                    'message': 'Personality test results saved successfully'
                })
            except Exception as e:
                print(f"Firebase error: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to save results to database'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'API returned unsuccessful response'
            })

    except Exception as e:
        print(f"Error checking test result: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@require_POST
def get_mbti_questions(request):
    try:
        # Fetch questions from Devil.ai API
        response = requests.get(
            f'{DEVIL_AI_BASE_URL}/questions',
            headers={'Authorization': f'Bearer {DEVIL_AI_API_KEY}'}
        )

        if not response.ok:
            raise Exception('Failed to fetch MBTI questions')

        questions = response.json()
        return JsonResponse({
            'status': 'success',
            'questions': questions
        })

    except Exception as e:
        print(f"Error fetching questions: {str(e)}")  # Debug print
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


@login_required
def update_announcement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            announcement_id = data.get('announcement_id')
            course_code = data.get('course_code')
            title = data.get('title')
            content = data.get('content')
            year = data.get('year').replace('/', '-')  # Convert 2025/2026 to 2025-2026
            semester = data.get('semester')
            current_user = request.session.get('user_name')
            
            print(f"Updating announcement:")
            print(f"ID: {announcement_id}")
            print(f"Course: {course_code}")
            print(f"Year: {year}")
            print(f"Semester: {semester}")
            
            # Update the announcement
            database.child("course")\
                   .child(year)\
                   .child(semester)\
                   .child(course_code)\
                   .child('announcements')\
                   .child(announcement_id)\
                   .update({
                        'title': title,
                        'content': content,
                        'last_modified': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                   })
            
            return JsonResponse({
                'status': 'success',
                'message': 'Announcement updated successfully'
            })
            
        except Exception as e:
            print(f"Error updating announcement: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@login_required
def delete_announcement(request):
    if request.method == 'POST':
        try:
            # First parse the JSON data
            data = json.loads(request.body)
            
            # Then get the values from the parsed data
            announcement_id = data.get('announcement_id')
            course_code = data.get('course_code')
            year = data.get('year')
            semester = data.get('semester')
            
            # Delete the announcement
            database.child("course")\
                   .child(year)\
                   .child(semester)\
                   .child(course_code)\
                   .child('announcements')\
                   .child(announcement_id)\
                   .remove()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Announcement deleted successfully'
            })
                
        except Exception as e:
            print(f"Error in delete_announcement: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

#resume
def resume_view(request):
    user_email = get_current_user(request)
    encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')
    print("resume view")
    print(request.POST)
    user_data = database.child("users").child(encoded_email).get().val()
    resume_data = database.child("resume").child(encoded_email).get().val()
    if resume_data is None:
        resume_data = {}  # Initialize as an empty dictionary if no data is found
    if request.method == 'POST':
        print("resume view post")
        resume_data = extract_data(request, user_email, user_data,resume_data)
        print(resume_data)
        database.child("resume").child(encoded_email).set(resume_data)
        return redirect('/resume_generated', resume_data=resume_data)
        
    if resume_data.get("current_user") == user_email:
        print("User email matches.")
        return render(request, 'Tools/Resume/index.html', {'resume_data': resume_data})
    else:
        print("User email does not match.")
    return render(request, 'Tools/Resume/index.html', {'user_data': user_data})

def extract_data(request, user_email, user_data, resume_data):
    print("extract data")
    if request.method == 'POST':
        data = request.POST
        print(data)

        # Extracting personal information
        name = data['name']
        email = data['email']
        phone = data['phone']
        about = data['about']
        address = data['address']
        
          # Extracting company details
        companies = []
        company_names = data.getlist('company[]')
        posts = data.getlist('post[]')
        durations = data.getlist('duration[]')
        descriptions = data.getlist('description[]')

        for i in range(len(company_names)):
            company = {
                'name': company_names[i],
                'post': posts[i] if i < len(posts) else '',
                'duration': durations[i] if i < len(durations) else '',
                'description': descriptions[i] if i < len(descriptions) else '',
            }
            companies.append(company)

        # Extracting languages, technical skills, soft skills, and achievements
        languages = data.getlist('lang[]')
        technical_skills = data.getlist('tech[]')
        soft_skills = data.getlist('soft[]')
        achievements = data.getlist('achievements[]')

        # Extracting education details
        schools = []
        school_names = data.getlist('schools[]')
        programs = data.getlist('programs[]')
        start_years = data.getlist('start_years[]')
        graduation_years = data.getlist('graduation_years[]')
        cgpas = data.getlist('cgpa[]')

        for j in range(len(school_names)):
            school = {
                'name': school_names[j],
                'program': programs[j] if j < len(programs) else '',
                'start_year': start_years[j] if j < len(start_years) else '',
                'graduation_year': graduation_years[j] if j < len(graduation_years) else '',
                'cgpa': cgpas[j] if j < len(cgpas) else '',
            }
            schools.append(school)
        # Handling profile picture
        profile_pic_base64 = None
        if 'profile_picture' in request.FILES:
            profile_pic = request.FILES['profile_picture']
            import base64
            profile_pic_base64 = base64.b64encode(profile_pic.read()).decode('utf-8')
        elif resume_data.get("profile_picture"):
            profile_pic_base64 = resume_data.get("profile_picture")
        else:
            profile_pic_base64 = user_data.get("profile_picture")

        # Create post data
        resume_data = {
            "current_user": user_email,
            "profile_picture": profile_pic_base64,
            "name": name,
            "email": email,
            "phone": phone,
            "about": about,
            "address": address,
            "companies": companies,
            "languages": languages,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "schools": schools,
            "achievements": achievements,
        }

        print("Extracted Companies:", companies)
        print("Extracted Schools:", schools)

        return resume_data

def resume_generated(request):
    user_email = get_current_user(request)
    
    # Encode email for Firebase path (replace @ and . with safe characters)
    encoded_email = user_email.replace('.', '-dot-').replace('@', '-at-')

    # Check if the user exists in the database
    #user for take profile picture
    user_data = database.child("users").child(encoded_email).get().val()
    resume_data=database.child("resume").child(encoded_email).get().val()


    return render(request, 'Tools/Resume/generate.html', {'resume_data': resume_data})


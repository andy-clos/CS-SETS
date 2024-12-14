from django.shortcuts import render, redirect
from django.http import JsonResponse
from firebase_admin import auth
import json
import pyrebase
from datetime import datetime
import pytz

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

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

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
    if request.method == 'POST':
        try:
            academic_year = request.POST.get('academic_year').replace('/', '-')
            semester = request.POST.get('semester')
            course_code = request.POST.get('course_code').upper()
            course_name = request.POST.get('course_name').title()

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

            venue_time = {}
            venue_time_index = 1
            while True:
                class_venue = request.POST.get(f'class_venue{venue_time_index}')
                class_day = request.POST.get(f'class_day{venue_time_index}')
                class_start_time = request.POST.get(f'class_start_time{venue_time_index}')
                class_end_time = request.POST.get(f'class_end_time{venue_time_index}')
                if not class_venue or not class_day or not class_start_time or not class_end_time:
                    break
                venue_time[venue_time_index] = {
                    "class_venue": class_venue.upper(),
                    "class_day": class_day.title(),
                    "class_start_time": class_start_time,
                    "class_end_time": class_end_time
                }
                venue_time_index += 1

            course_data = {
                "course_name": course_name,
                "lecturers": lecturers,
                "venue and time": venue_time
            }

            database.child("course").child(academic_year).child(semester).child(course_code).set(course_data)

            success_message = "Course added successfully!"
            return redirect('academic')
        except Exception as e:
            print(f"Error adding course: {e}")
            return render(request, 'academic.html', {'error': str(e)})

    courses = []
    try:
        courses_data = database.child("course").get().val()

        for academic_year, semesters in courses_data.items():
            for semester_index, courses_in_semester in enumerate(semesters):
                semester = str(semester_index)
                if isinstance(courses_in_semester, dict):
                    for course_code, course_info in courses_in_semester.items():
                        lecturers = course_info.get('lecturers', {})
                        lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                        venue_time = course_info.get('venue and time', {})
                        venue_time = [vt for vt in venue_time if vt is not None]
                        lecturer_count = len(lecturers)
                        courses.append({
                            'academic_year': academic_year,
                            'semester': semester,
                            'course_code': course_code,
                            'course_name': course_info.get('course_name', ''),
                            'lecturers': lecturers,
                            'lecturer_count': lecturer_count,
                            'venue and time': venue_time
                        })

    except Exception as e:
        print(f"Error fetching courses: {e}")

    return render(request, 'academic.html', {'courses': courses})

def course_detail_view(request, semester_year, course_code):
    if request.method == 'POST':
        try:
            academic_year = request.POST.get('academic_year').replace('/', '-')
            semester = request.POST.get('semester')
            course_code = request.POST.get('course_code').upper()
            course_name = request.POST.get('course_name').title()

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

            venue_time = {}
            venue_time_index = 1
            while True:
                class_venue = request.POST.get(f'class_venue{venue_time_index}')
                class_day = request.POST.get(f'class_day{venue_time_index}')
                class_start_time = request.POST.get(f'class_start_time{venue_time_index}')
                class_end_time = request.POST.get(f'class_end_time{venue_time_index}')
                if not class_venue or not class_day or not class_start_time or not class_end_time:
                    break
                venue_time[venue_time_index] = {
                    "class_venue": class_venue.upper(),
                    "class_day": class_day.title(),
                    "class_start_time": class_start_time,
                    "class_end_time": class_end_time
                }
                venue_time_index += 1

            course_data = {
                "course_name": course_name,
                "lecturers": lecturers,
                "venue and time": venue_time
            }

            database.child("course").child(academic_year).child(semester).child(course_code).update(course_data)

            success_message = "Course updated successfully!"

            return redirect('course-detail', semester_year=semester_year, course_code=course_code)
        except Exception as e:
            print(f"Error updating course: {e}")
            return render(request, 'course-detail.html', {'error': str(e)})

    try:
        academic_year, semester = semester_year.split('sem')
        semester = semester[0] 
        academic_year = semester_year[semester_year.index("year") + 4:]

        courses_data = database.child("course").get().val()
        courses = []
        
        for year, semesters in courses_data.items():
            if year == academic_year:
                for semester_index, courses_in_semester in enumerate(semesters):
                    if str(semester_index) == semester:
                        if isinstance(courses_in_semester, dict):
                            for code, course_info in courses_in_semester.items():
                                if code == course_code: 
                                    lecturers = course_info.get('lecturers', {})
                                    lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                                    venue_time = course_info.get('venue and time', {})
                                    venue_time = [vt for vt in venue_time if vt is not None]
                                    lecturer_count = len(lecturers)
                                    print("this is count" ,lecturer_count)
                                    courses.append({
                                        'semester_year': semester_year,
                                        'academic_year': year.replace('-', '/'),
                                        'semester': str(semester_index),
                                        'course_code': code,
                                        'course_name': course_info.get('course_name', ''),
                                        'lecturers': lecturers,
                                        'lecturer_count': lecturer_count,
                                        'venue_time': venue_time
                                    })
        print(courses)
        if not courses:
            return render(request, 'course-detail.html', {'error': 'Course not found'})
        
        return render(request, 'course-detail.html', {'courses': courses, 'course_code': course_code, 'academic_year': academic_year, 'semester': semester})
    except Exception as e:
        print(f"Error fetching course details: {e}")
        return render(request, 'course-detail.html', {'error': 'An error occurred while fetching course details'})

def analytics_detail_view(request, semester_year, course_code):
    if request.method == 'POST':
        try:
            academic_year = request.POST.get('academic_year').replace('/', '-')
            semester = request.POST.get('semester')
            course_code = request.POST.get('course_code').upper()
            course_name = request.POST.get('course_name').title()

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

            venue_time = {}
            venue_time_index = 1
            while True:
                class_venue = request.POST.get(f'class_venue{venue_time_index}')
                class_day = request.POST.get(f'class_day{venue_time_index}')
                class_start_time = request.POST.get(f'class_start_time{venue_time_index}')
                class_end_time = request.POST.get(f'class_end_time{venue_time_index}')
                if not class_venue or not class_day or not class_start_time or not class_end_time:
                    break
                venue_time[venue_time_index] = {
                    "class_venue": class_venue.upper(),
                    "class_day": class_day.title(),
                    "class_start_time": class_start_time,
                    "class_end_time": class_end_time
                }
                venue_time_index += 1

            course_data = {
                "course_name": course_name,
                "lecturers": lecturers,
                "venue and time": venue_time
            }

            database.child("course").child(academic_year).child(semester).child(course_code).update(course_data)

            success_message = "Course updated successfully!"

            return redirect('analytics-detail', semester_year=semester_year, course_code=course_code)
        except Exception as e:
            print(f"Error updating course: {e}")
            return render(request, 'analytics-detail.html', {'error': str(e)})

    try:
        academic_year, semester = semester_year.split('sem')
        semester = semester[0] 
        academic_year = semester_year[semester_year.index("year") + 4:]

        courses_data = database.child("course").get().val()
        courses = []
        
        for year, semesters in courses_data.items():
            if year == academic_year:
                for semester_index, courses_in_semester in enumerate(semesters):
                    if str(semester_index) == semester:
                        if isinstance(courses_in_semester, dict):
                            for code, course_info in courses_in_semester.items():
                                if code == course_code: 
                                    lecturers = course_info.get('lecturers', {})
                                    lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                                    venue_time = course_info.get('venue and time', {})
                                    venue_time = [vt for vt in venue_time if vt is not None]
                                    lecturer_count = len(lecturers)
                                    print("this is count" ,lecturer_count)
                                    courses.append({
                                        'semester_year': semester_year,
                                        'academic_year': year.replace('-', '/'),
                                        'semester': str(semester_index),
                                        'course_code': code,
                                        'course_name': course_info.get('course_name', ''),
                                        'lecturers': lecturers,
                                        'lecturer_count': lecturer_count,
                                        'venue_time': venue_time
                                    })
        print(courses)
        if not courses:
            return render(request, 'analytics-detail.html', {'error': 'Course not found'})
        
        return render(request, 'analytics-detail.html', {'courses': courses, 'course_code': course_code, 'academic_year': academic_year, 'semester': semester})
    except Exception as e:
        print(f"Error fetching course details: {e}")
        return render(request, 'analytics-detail.html', {'error': 'An error occurred while fetching course details'})

def delete_course_view(request, semester_year, course_code):
    try:
        print(f"Deleting course: semester_year={semester_year}, course_code={course_code}")
        academic_year, semester = semester_year.split('sem')
        semester = semester[0]  # Extract the semester number
        academic_year = semester_year[semester_year.index("year") + 4:]
        print("this is year:", academic_year)
        # Delete the course from the database
        database.child("course").child(academic_year).child(semester).child(course_code).remove()

        return redirect('academic')
    except Exception as e:
        print(f"Error deleting course: {e}")
        return render(request, 'course-detail.html', {'error': str(e)})
    
def tools_view(request):
    return render(request, 'Tools/tools.html')

def appointments_view(request):
    return render(request, 'appointments.html')

def forum_view(request):
    # Get user email from session storage
    user_email = request.GET.get('email')   
    # Retrieve posts from Firebase
    posts = getPosts()  # Call the getPosts function to retrieve posts 
    return render(request, "Tools/Forum/forum.html", {"user_email": user_email, "posts": posts})

def analytics_view(request):
    courses = []
    try:
        courses_data = database.child("course").get().val()

        for academic_year, semesters in courses_data.items():
            for semester_index, courses_in_semester in enumerate(semesters):
                semester = str(semester_index)
                if isinstance(courses_in_semester, dict):
                    for course_code, course_info in courses_in_semester.items():
                        lecturers = course_info.get('lecturers', {})
                        lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                        venue_time = course_info.get('venue and time', {})
                        venue_time = [vt for vt in venue_time if vt is not None]
                        lecturer_count = len(lecturers)
                        courses.append({
                            'academic_year': academic_year,
                            'semester': semester,
                            'course_code': course_code,
                            'course_name': course_info.get('course_name', ''),
                            'lecturers': lecturers,
                            'lecturer_count': lecturer_count,
                            'venue and time': venue_time
                        })

    except Exception as e:
        print(f"Error fetching courses: {e}")

    return render(request, 'analytics.html', {'courses': courses})

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

def createpost_view(request):
    if request.method == 'POST':
        try:
            # Get form data
            subject = request.POST.get('subject')
            title = request.POST.get('title')
            content = request.POST.get('content')
            tags = json.loads(request.POST.get('tags', '[]'))
            author_email = request.POST.get('author_email')
            
            # Get current timestamp
            current_timestamp = int(datetime.now(pytz.UTC).timestamp() * 1000)
            formatted_date = datetime.fromtimestamp(current_timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S')
            
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
        post_list = [post.val() for post in posts.each()] 
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
               user_email = request.session.get('user_email')

               # Get current timestamp
               current_timestamp = int(datetime.now(pytz.UTC).timestamp() * 1000)
               formatted_date = datetime.fromtimestamp(current_timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S')

               # Reference to the specific post in Firebase
               post_ref = database.child("forum").child("posts").child(f"PostID{post_id}")
               print(f"Post ID: {post_id}")  # Debugging output

               # Check if the post exists
               post_data = post_ref.get().val()
               print(f"Post Data: {post_data}")  # Debugging output

               if post_data:
                   # Push the reply to the post's replies
                   reply_data = {
                       "content": content,
                       "author": user_email,
                       "timestamp": formatted_date
                   }
                   post_ref.child("replies").push(reply_data)

                   # Update the comments count if needed
                   current_count = post_data.get("comments_count", 0)
                   new_count = current_count + 1
                   post_ref.update({"comments_count": new_count})

                   return JsonResponse({'status': 'success', 'message': 'Reply added successfully.'})
               else:
                   return JsonResponse({'status': 'error', 'message': 'Post not found.'}, status=404)

           except Exception as e:
               return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

       return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

#Push Data
# data = {
#     "subject": "552",
#     "title": "Question 1",
#     "content": "What is the capital of France?",
#     "tags": ["France", "Paris", "Capital"]
# }
# # database.push(data)

# #create data
# database.child("forum").child("posts").set(data)
#retrieve data
# info=authe.current_user()
# print(info.val())
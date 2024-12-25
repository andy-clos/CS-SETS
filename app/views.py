import joblib
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from firebase_admin import auth
import json
import pyrebase
from datetime import datetime
import pytz
from django.contrib import messages
import random
import colorsys
from io import BytesIO
import xhtml2pdf.pisa as pisa



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

    courses = {}
    try:
        courses_data = database.child("course").get().val()
        sorted_courses_data = dict(sorted(courses_data.items(), key=lambda item: item[0], reverse=True))
        for academic_year, semesters in sorted_courses_data.items():
            academic_year_slash = academic_year.replace('-', '/')  # Replace dash with slash for display
            if academic_year not in courses:
                courses[academic_year] = {'display': academic_year_slash, 'semesters': {}}
            for semester_index, courses_in_semester in enumerate(semesters):
                semester = str(semester_index)
                if isinstance(courses_in_semester, dict):
                    semester_courses = []
                    for course_code, course_info in courses_in_semester.items():
                        lecturers = course_info.get('lecturers', {})
                        lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                        venue_time = course_info.get('venue and time', {})
                        venue_time = [vt for vt in venue_time if vt is not None]
                        lecturer_count = len(lecturers)
                        semester_courses.append({
                            'course_code': course_code,
                            'course_name': course_info.get('course_name', ''),
                            'lecturers': lecturers,
                            'lecturer_count': lecturer_count,
                            'venue and time': venue_time
                        })
                    if semester_courses:
                        courses[academic_year]['semesters'][semester] = semester_courses

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

        if not courses:
            return render(request, 'analytics-detail.html', {'error': 'Course not found'})
        
        return render(request, 'analytics-detail.html', {'courses': courses, 'course_code': course_code, 'academic_year': academic_year, 'semester': semester, 'predictions': predictions})
    except Exception as e:
        print(f"Error fetching course details: {e}")
        return render(request, 'analytics-detail.html', {'error': 'An error occurred while fetching course details'})

def delete_course_view(request, semester_year, course_code):
    try:
        print(f"Deleting course: semester_year={semester_year}, course_code={course_code}")
        academic_year, semester = semester_year.split('sem')
        semester = semester[0]
        academic_year = semester_year[semester_year.index("year") + 4:]

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
    user_email = request.GET.get('email')
    search_query = request.GET.get('search', '')  # Get the search query from the URL
    posts = getPosts()  # Call the getPosts function to retrieve posts

    # Filter posts based on the search query in title or subject
    if search_query:
        posts = [post for post in posts if search_query.lower() in post['title'].lower() or search_query.lower() in post['subject'].lower()]

    return render(request, "Tools/Forum/forum.html", {"user_email": user_email, "posts": posts, "search_query": search_query})

def getSubject():
    subject = database.child("forum").child("posts").get()

def analytics_view(request):
    courses = {}
    try:
        courses_data = database.child("course").get().val()
        sorted_courses_data = dict(sorted(courses_data.items(), key=lambda item: item[0], reverse=True))
        for academic_year, semesters in sorted_courses_data.items():
            academic_year_slash = academic_year.replace('-', '/')  # Replace dash with slash for display
            if academic_year not in courses:
                courses[academic_year] = {'display': academic_year_slash, 'semesters': {}}
            for semester_index, courses_in_semester in enumerate(semesters):
                semester = str(semester_index)
                if isinstance(courses_in_semester, dict):
                    semester_courses = []
                    for course_code, course_info in courses_in_semester.items():
                        lecturers = course_info.get('lecturers', {})
                        lecturers = [lecturer for lecturer in lecturers if lecturer is not None]
                        venue_time = course_info.get('venue and time', {})
                        venue_time = [vt for vt in venue_time if vt is not None]
                        lecturer_count = len(lecturers)
                        semester_courses.append({
                            'course_code': course_code,
                            'course_name': course_info.get('course_name', ''),
                            'lecturers': lecturers,
                            'lecturer_count': lecturer_count,
                            'venue and time': venue_time
                        })
                    if semester_courses:
                        courses[academic_year]['semesters'][semester] = semester_courses

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
            user_email = request.POST.get('author_email')
            # Get current timestamp
            current_timestamp = int(datetime.now(pytz.UTC).timestamp() * 1000)
            formatted_date = datetime.fromtimestamp(current_timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S')

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
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday","Sunday"]
    
    # Function to generate random pastel color
    def generate_pastel_color():
        hue = random.random()
        saturation = 0.3 + random.random() * 0.2
        value = 0.9 + random.random() * 0.1
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
    
    course_colors = {course: generate_pastel_color() for course in selected_courses}
    time_slots = set()
    
    for course in subject_codes:
        for vt in course.get('venue_time', []):
            if 'class_start_time' in vt and 'class_end_time' in vt:
                time_slots.add(f"{vt['class_start_time']} - {vt['class_end_time']}")
    time_slots = sorted(list(time_slots))

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
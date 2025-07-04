from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt

from .models import User, Note


def index(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = User.objects.get(id=user_id)
    notes = note_query(user.username)
    return render(request, 'index.html', {'user': user, 'notes': notes})

def note_query(username):
    with connection.cursor() as cursor:

        # FLAW 1: A1:2017 – Injection
        cursor.execute(f"SELECT * FROM app_note WHERE owner_id IN (SELECT id FROM app_user WHERE username = '{username}')")

        # FIX:
        # cursor.execute("SELECT * FROM app_note WHERE owner_id IN (SELECT id FROM app_user WHERE username = %s)",[username])

        return cursor.fetchall()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():

            # FLAW 2: A2:2017 – Broken Authentication
            User.objects.create(username=username, password=password)

            # FIX:
            # User.objects.create(username=username, password=make_password(password))
            return redirect('login')
        else:
            return HttpResponse("Username already exists")
    return render(request, 'register.html')

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:

            # Continuation of FLAW 2: A2:2017 – Broken Authentication
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect('index')
        
            # Continuation of FLAW 2 FIX: A2:2017 – Broken Authentication
            #user = User.objects.get(username=username)
            #if check_password(password, user.password):
                #request.session['user_id'] = user.id
                #return redirect('index')
            #else:
                #error = "Invalid username or password."

        except:
            error = "Invalid username or password."
    return render(request, 'login.html', {'error': error})
        
def logout_view(request):
    del request.session['user_id']
    return redirect('login')

def view_note(request, note_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:

        # FLAW 3: A5:2017 – Broken Access Control
        note = Note.objects.get(id=note_id)

        # FIX:
        # note = Note.objects.get(id=note_id, owner_id=user_id)

    except Note.DoesNotExist:
        return HttpResponse("Invalid note.")

    return render(request, 'view_note.html', {'note': note})

# FLAW 4: CSRF
@csrf_exempt
# FIX:
# remove @csrf_exempt
def add_note(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        Note.objects.create(owner=user, title=title, content=content)
        return redirect('index')
    return render(request, 'add_note.html')
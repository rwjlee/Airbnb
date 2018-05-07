import bcrypt, json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from pprint import pprint
from apps.airbnbclone.models import User

def index(request):
    return render(request, 'airbnbclone/index.html')

# def logout(request):
#     request.session.clear()
#     return redirect('airbnbclone:index')

# def login(request):
#     if 'user_id' in request.session:
#         return redirect('airbnbclone:index')
#     return render(request, 'airbnbclone/login.html')

# def register(request):
#     if 'user_id' in request.session:
#         return redirect('airbnbclone:index')
#     return render(request, 'airbnbclone/register.html')

# def authenticate(request, auth_for):
#     if (request.method == 'POST'):
#         success = False
#         user = None

#         if (auth_for == 'register'):
#             success, user = register_user(request)

#         if auth_for == 'login':
#             success, user = login_user(request)

#         if (success):
#             start_session(request, user)
#             return JsonResponse({ "url": redirect('airbnbclone:index').url })

#         errors = []
#         for message in messages.get_messages(request):
#             errors.append(str(message))

#         return JsonResponse({ 'errors': errors }, status=400)

#     return JsonResponse({ 'message': 'method not allowed' })

# def login_user(request):
#     email = request.POST['html_email']
#     password = request.POST['html_password']
#     is_valid = check_length(request, email, 'Email')
#     is_valid = check_length(request, password, 'Password')

#     if is_valid:
#         try:
#             user = User.objects.get(email=email)
#             if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
#                 return True, user
#             else:
#                 messages.error(request, 'Invalid email or password')
#         except:
#             messages.error(request, 'Email not found. Please register.')

#     return False, None

# def register_user(request):
#     username = request.POST['html_username']
#     email = request.POST['html_email']
#     password = request.POST['html_password']
#     confirm = request.POST['html_confirm']

#     is_valid = check_length(request, username, 'Full name')
#     is_valid = check_length(request, email, 'Email')
#     is_valid = check_length(request, password, 'Password')
#     is_valid = check_length(request, confirm, 'Confirm password')

#     if password != confirm:
#         messages.error(request, 'Passwords do not match')
#         is_valid = False

#     if is_valid:
#         try:
#             user = User.objects.create(username=username, email=email, password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
#             return True, user
#         except:
#             messages.error(request, 'That email address is already in use.  Please use a different email address.')

#     return False, None

def start_session(request, user):
    request.session['user_id'] = user.id
    request.session['username'] = user.username

def check_length(request, data, name):
    if len(data) == 0:
        messages.error(request, name + ' cannot be left blank')
        return False
    return True


def edit_profile(request):
    if 'user_id' in request.session:
        return redirect('airbnbclone:index')
    if request.method == 'POST':
        if len(request.POST['html_email']) > 0 and request.POST['html_password'] == request.POST['html_confirm']:
            try:
                user = User.objects.create(
                    username = request.POST['html_username'],
                    email = request.POST['html_email'], 
                    password = request.POST['html_password'],
                    birthday = request.POST['html_birthday'])
                request.session['username'] = user.username
                request.session['user_id'] = user.id
                request.session['email'] = user.email
                request.session['birthday'] = user.birthday
            except:
                raise
                messages.error(request,'Account already in use')
                return redirect('airbnbclone:edit_profile')

        return redirect('airbnbclone:index')
    return render(request, 'airbnbclone/edit_profile.html')

def register(request):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    if request.method == 'POST':
        if len(request.POST['html_email']) > 0 and request.POST['html_password'] == request.POST['html_confirm']:
            try:
                user = User.objects.create(
                    username = request.POST['html_username'],
                    email = request.POST['html_email'], 
                    password = request.POST['html_password'],
                    birthday = request.POST['html_birthday'])
                request.session['username'] = user.username
                request.session['user_id'] = user.id
                request.session['email'] = user.email
                request.session['birthday'] = user.birthday
            except:
                raise
                messages.error(request,'Account already in use')
                return redirect('airbnbclone:register')

        return redirect('airbnbclone:index')
    return render(request, 'airbnbclone/register.html')

def login(request):
    if 'user_id' in request.session:
        return redirect('airbnbclone:index')
    if request.method == 'POST':
        try:
            user = User.objects.get(email = request.POST['html_email'])
            if request.POST['html_password'] == user.password:
                request.session['username'] = user.username
                request.session['user_id'] = user.id
                request.session['email'] = user.email
                return redirect('airbnbclone:index')
            else:
                messages.error(request, 'Invalid login')
                return redirect('airbnbclone:login')
        except:
            messages.error(request, 'Invalid login')    
            return redirect('airbnbclone:login')

    return render(request, 'airbnbclone/login.html')

    
def logout(request):
    request.session.clear()
    return redirect('airbnbclone:index')



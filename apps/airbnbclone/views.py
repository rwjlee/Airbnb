import bcrypt, json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from pprint import pprint
from apps.airbnbclone.models import User
import googlemaps
from datetime import datetime
from apps.airbnbclone.constants import MAP_API_KEY
from apps.airbnbclone.models import User

def index(request):
    return render(request, 'airbnbclone/index.html')

def start_session(request, user):
    request.session['user_id'] = user.id
    request.session['username'] = user.username

def check_length(request, data, name):
    if len(data) == 0:
        messages.error(request, name + ' cannot be left blank')
        return False
    return True


def edit_profile(request):
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
                return redirect('airbnbclone:edit_profile')

        return redirect('airbnbclone:index')
    return render(request, 'airbnbclone/edit_profile.html')

def register(request):
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


def listing(request):
    query = request.GET["html_term".replace(" ", "+")]

    context = {
        'api_key' : MAP_API_KEY,
        'query' : query
    }
    return render(request, 'airbnbclone/listing.html', context)

<<<<<<< HEAD
def become_a_host(request):

    return render(request, 'airbnbclone/create_listing.html')

def create_listing(request):

    # if 'user_id' in request.session:
    #     return redirect('airbnbclone:index')

    if request.method == 'POST':
        try:
            # host = request.session['user_id']
            listing_type = request.POST['html_listing_type']
            privacy_type = request.POST['html_privacy_type']
            bedroom = request.POST['html_bedroom']
            bath = request.POST['html_bath']
            bed = request.POST['html_bed']
            num_guests= request.POST['html_num_guests']
            country = request.POST['html_country']
            address = request.POST['html_address']
            name = request.POST['html_name']
            desc = request.POST['html_desc']
            listing = m.Listing.objects.create(
                listing_type = listing_type,
                privacy_type = privacy_type,
                bedroom = bedroom,
                bath = bath,
                bed = bed,
                num_guests= num_guests,
                country = country,
                address = address,
                name = name,
                desc = desc,    
            )
        except:
            raise
            print('This is wrong')
            return redirect('airbnbclone:index')

        return redirect('airbnbclone:index')

    return render(request, 'airbnbclone/create_listing.html')
=======

>>>>>>> edcd3eefb8e1d53023cabebd928207b137f00668

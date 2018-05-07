from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from pprint import pprint
import apps.airbnbclone.models as m
import googlemaps
from datetime import datetime
from apps.airbnbclone.constants import MAP_API_KEY
from django.db.models import Q
import json, requests

# Create your views here.
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
        try:
            user = m.User.objects.get(id = request.session['user_id'])
            user.username = request.POST['html_username']
            user.password = request.POST['html_password']
            user.birthday = request.POST['html_birthday']
            print(request.POST['html_birthday'])
            user.gender = request.POST['html_gender']
            user.description = request.POST['html_description']
            user.save()
            request.session['username'] = user.username

        except:
            raise
            messages.error(request,'Account already in use')
            return redirect('airbnbclone:edit_profile')

        return redirect('airbnbclone:index')

    user = m.User.objects.get(id = request.session['user_id'])
    print("*****")
    print(str(user.birthday))
    print("*****")
    context = {
        "user": user,
        "birthday": str(user.birthday),
        "gender_options": ["Male", "Female", "Other"]
    }
    return render(request, 'airbnbclone/edit_profile.html', context)

def register(request):
    if 'user_id' in request.session:
        return redirect('airbnbclone:index')
    if request.method == 'POST':
        if len(request.POST['html_email']) > 0 and request.POST['html_password'] == request.POST['html_confirm']:
            try:
                user = m.User.objects.create(
                    username = request.POST['html_username'],
                    email = request.POST['html_email'], 
                    password = request.POST['html_password'],
                    birthday = request.POST['html_birthday']
                )
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
            user = m.User.objects.get(email = request.POST['html_email'])
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


def view_profile(request, user_id):
    try:
        profile = m.User.objects.get(id = user_id)
    except:
        profile = None
        return redirect('airbnbclone:index')

    context = {
        'profile': profile
    }

    return render(request, 'airbnbclone/view_profile.html', context)


def listing(request, listing_id):

    try:
        room = m.Listing.objects.get(id = listing_id)
    except:
        room = None
        return redirect('airbnbclone:index')

    context = {
        'api_key' : MAP_API_KEY,
        'room': room,
    }
    print("listing got okay")
    print(room.address)
    return render(request, 'airbnbclone/listing.html', context)

def filters(request):
    return render(request, 'airbnbclone/filters.html')

def results(request):
    query = request.GET['html_term']
    context = {
        'listings' : m.Listing.objects.filter(Q(address__icontains=query) | Q(country__icontains=query) | Q(name__icontains=query))
    }
    listings = m.Listing.objects.filter()

    return render(request, 'airbnbclone/results.html', context)

def become_a_host(request):

    if 'user_id' not in request.session:
        return redirect('airbnbclone:register')
    return render(request, 'airbnbclone/create_listing.html')

def get_url(address, city, country):
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={},+{},+{}&key={}".format(address, city, country, MAP_API_KEY)
    return url

def get_json(url):
    resp = requests.get(url)
    return json.loads(resp.text)

def create_listing(request):

    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    if request.method == 'POST':
        try:
            host = request.session['user_id']
            listing_type = request.POST['html_listing_type']
            privacy_type = request.POST['html_privacy_type']
            bedroom = request.POST['html_bedroom']
            bath = request.POST['html_bath']
            bed = request.POST['html_bed']
            num_guests= request.POST['html_num_guests']

            country = request.POST['html_country']
            city = request.POST['html_city']
            address = request.POST['html_address']

            price = request.POST['html_price']
            
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
                city = city,
                address = address,
                name = name,
                desc = desc,
                price = price,
            )

        except:
            raise
            print('This is wrong')
            return redirect('airbnbclone:index')

        return redirect('airbnbclone:index')

    return render(request, 'airbnbclone/create_listing.html')

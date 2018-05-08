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
        listings = m.Listing.objects.all()
    except:
        profile = None
        return redirect('airbnbclone:index')
    context = {
        'profile': profile,
        'listings': listings
    }
    return render(request, 'airbnbclone/view_profile.html', context)

def my_bookings(request):
    user_id = request.session['user_id']
    bookings = m.Booking.objects.filter(guest_id = user_id)

    context = {
        'user_id': user_id,
        'bookings': bookings
    }
    return render(request, 'airbnbclone/my_bookings.html', context)

def authenticate_booking(request):
    if request.method== "POST":
        booking = create_booking(request)

        if booking:
            return JsonResponse({"url": redirect('airbnbclone:index').url})

        errors = []
        for message in messages.get_messages(request):
            errors.append(str(message))

        return JsonResponse({'errors': errors}, status=400)
        
    return JsonResponse({'message': 'method not allowed'})

def test_booking(request):

    return render(request, 'airbnbclone/booking.html')

def create_booking(request):
    listing_id = request.POST["html_listing_id"]
    user_id = request.POST["html_user_id"]
    checkin = request.POST["html_checkin"]
    checkout = request.POST["html_checkout"]
    guests = request.POST["html_guests"]
    charge = float(request.POST["html_charge"]) * 5

    if not check_dates(checkin, checkout, listing_id):
        return None

    try:
        booking = m.Booking.objects.create(
            guest_id = user_id, 
            home_listing_id = listing_id, 
            from_date = checkin,
            to_date = checkout,
            guests = guests,
            charge_amount = charge,
        )
        
    except:
        raise
    
    print("==========finish book=======")

    return booking

def check_dates(start_date, end_date, listing_id):
    print("in check date")
    try:
        listing = m.Listing.objects.get(id=listing_id)
    except:
        raise
        return False

    return True

def listing(request, listing_id):
    print("1111111 {}".format(request.method))
    
    try:
        room = m.Listing.objects.get(id = listing_id)
        if not room.active:
            return redirect('airbnbclone:index')
    except:
        room = None
        return redirect('airbnbclone:index')

    context = {
        'api_key' : MAP_API_KEY,
        'room': room,
    }
    print("listing got okay")
    print(room.address)
    # geo_address = get_json(get_url(room.address, room.city, room.country))
    # pprint(geo_address)
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

def edit_listing(request, listing_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    
    listing = Listing.objects.get(id = listing_id)
    if listing and listing.host_id == request.session['user_id']:
        print("do edit")

    return redirect('airbnbclone:index') 

def get_amenities(amen):
    a = None

    try:
        a = m.Amenity.objects.get(name = amen)
    except:
        print("amenity does not exist")
        a = m.Amenity.objects.create(name = amen)
    
    return a

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

            amen = get_amenities("dryer")
            
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
                host_id = host,
            )

            listing.active = True
            listing.amenities.add(amen)
            listing.save()

        except:
            raise
            print('This is wrong')
            return redirect('airbnbclone:index')

        return redirect('airbnbclone:listing', listing.id)

    return render(request, 'airbnbclone/create_listing.html')

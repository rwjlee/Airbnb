from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from pprint import pprint
import apps.airbnbclone.models as m
import googlemaps
import datetime
from apps.airbnbclone.constants import MAP_API_KEY
from django.db.models import Q
import json, requests
import pandas as pd

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

def cancel_booking(request, booking_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    try:
        booking = m.Booking.objects.get(id = booking_id)
        user_id = request.session['user_id']

        if booking.guest_id == user_id or booking.home_listing.host_id == user_id:
            booking.is_cancelled = 1
            update_avail(booking.from_date, booking.to_date, booking.home_listing_id, 1)
            booking.save()
    except:
        return redirect('airbnbclone:index')

    return redirect('airbnbclone:my_bookings')
    
def my_bookings(request):
    user_id = request.session['user_id']
    today = datetime.date.today()
    current_bookings = m.Booking.objects.filter(Q(to_date__gte = today) & Q(guest_id = user_id) & Q(is_cancelled = 0)).all()
    past_bookings = m.Booking.objects.filter(Q(to_date__lt = today) & Q(guest_id = user_id) & Q(is_cancelled = 0)).all()

    context = {
        'user_id': user_id,
        'current_bookings': current_bookings,
        'past_bookings': past_bookings
    }
    return render(request, 'airbnbclone/my_bookings.html', context)

def all_messages(request):
    messages = m.Message.objects.all()

    context = {
        'messages': messages,
    }
    return render(request, 'airbnbclone/all_messages.html', context)

def convo(request, listing_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    listing = m.Listing.objects.get(id = listing_id)
    messages = m.Message.objects.filter((Q(recipient_id = listing.host.id) & Q(listing_id = listing.id)) | (Q(recipient_id = request.session['user_id']) & Q(listing_id = listing.id))).order_by('-created_at')

    context = {
        'listing': listing,
        'messages': messages,
    }
    return render(request, 'airbnbclone/convo.html', context)

def send_message(request, listing_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    if request.method == 'POST':
        if len(request.POST['html_contents']) > 0:
            try:
                message = m.Message.objects.create(
                    contents = request.POST['html_contents'],
                    sender_id = request.session['user_id'],
                    recipient_id = 
                )

    return render(request, 'airbnbclone/convo.html')

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
    user_id = request.POST["html_user_id"]
    checkin = request.POST["html_checkin"]
    checkout = request.POST["html_checkout"]
    guests = request.POST["html_guests"]
    charge = float(request.POST["html_charge"]) * 5
    listing_id = request.POST["html_listing_id"]

    avail_list = check_dates(checkin, checkout, listing_id)
    date_list, open_list = zip(*avail_list)

    if False in open_list:
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
        update_avail(booking.from_date, booking.to_date, listing_id, 0)
        
    except:
        raise
    
    print("==========finish book=======")

    return booking

def update_avail_one(add_date, listing_id, available):
    try:
        avail = m.Availability.objects.filter(Q(listing_id = listing_id) & Q(one_day = add_date)).first()
        if avail:
            avail.available = available
            avail.save()
            print("=======available========")
        else:
            avail = m.Availability.objects.create(listing_id = listing_id, available=available, one_day = add_date)
            print(avail.listing.host.username)
            print("========not available=======")
    except:
        raise
        print("cannot update")
        return None

    return avail

def update_avail(start_date, end_date, listing_id, available):

    if start_date >= end_date:
        return None

    mydates = pd.date_range(start_date, end_date).tolist()
    d_range = [d.date() for d in mydates[:-1]]
    avail_list = [update_avail_one(day, listing_id, available) for day in d_range]

    return avail_list

def find_avail(one_date, listing_id):
    try:
        avail = m.Availability.objects.filter(Q(listing_id = listing_id) & Q(one_day = one_date)).first()
        if avail.available == 1:
            return (one_date, True)
        else:
            return (one_date, False)
    except:
        return (one_date, False)


def check_dates(start_date, end_date, listing_id):
    if (end_date <= start_date):
        return None

    mydates = pd.date_range(start_date, end_date).tolist()
    d_range = [d.date() for d in mydates[:-1]]
    avail_list = [find_avail(day, listing_id) for day in d_range]

    return avail_list

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

def get_price_range(request, input):
    if input == 1:
        request.session['price'] = [0, 50]
    elif input == 2:
        request.session['price'] = [50, 100]
    elif input == 3:
        request.session['price'] = [100, 150]
    elif input == 4:
        request.session['price'] = [150, 200]
    elif input == 5:
        request.session['price'] = [200, 250]
    elif input == 6:
        request.session['price'] = [250, 300]
    elif input == 7:
        request.session['price'] = [300, 400]
    elif input == 8:
        request.session['price'] = [400, 500]
    elif input == 9:
        request.session['price'] = 500
    else:
        request.session['price'] = [0, 1000]

def filters(request):
    request.session['from_date'] = request.POST["fromDate"]
    request.session['to_date'] = request.POST["toDate"]

    if request.POST['guests'] != "Guests":
        request.session['guests'] = request.POST["guests"]
        print(request.session['guests'] )
    if request.POST['homeType'] != "Home Type":
        request.session['home_type'] = request.POST["homeType"]
        print(request.session['home_type'])
    if request.POST['price'] != 'Price':
        get_price_range(request, int(request.POST["price"]))
    
    return JsonResponse({})
        
def results(request):
    query = request.GET['html_term']
    results = []
    for listing in m.Listing.objects.filter(Q(address__icontains=query) | Q(country__icontains=query) | Q(name__icontains=query)):
        results.append(listing)

    print(results)

    if 'guests' in request.session:
        for listing in m.Listing.objects.filter(num_guests=request.session['guests']):
            if listing not in results:
                results.append(listing)
            for result in results:
                if request.session['guests'] != result.num_guests:
                    results.remove(result)

    print(results)
            
    if 'home_type' in request.session:
        for listing in m.Listing.objects.filter(privacy_type=request.session['home_type']):
            if listing not in results:
                results.append(listing)
            for result in results:
                if request.session['home_type'] != result.privacy_type:
                    results.remove(result)

    print(results)

    if 'price' in request.session:
        for listing in m.Listing.objects.filter(price=request.session['price']):
            if listing not in results:
                results.append(listing)
            for result in results:
                if request.session['price'] != result.price:
                    results.remove(result)
    
    print(results)

    context = {
        'listings' : results
    }
    if 'guests' in request.session:
        del request.session['guests']

    if 'home_type' in request.session:
        del request.session['home_type']
    
    if 'price' in request.session:
        del request.session['price']

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

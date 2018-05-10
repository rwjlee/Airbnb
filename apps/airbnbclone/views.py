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
import math as math
from django.core.files.storage import FileSystemStorage
from operator import itemgetter


from django.core import serializers

# Create your views here.
def index(request):
    context = {
        "api_key": MAP_API_KEY,
    }
    return render(request, 'airbnbclone/index.html', context)

def start_session(request, user):
    request.session['user_id'] = user.id
    request.session['username'] = user.username

def check_length(request, data, name):
    if len(data) == 0:
        messages.error(request, name + ' cannot be left blank')
        return False
    return True

#### LOGIN AND REGISTRATION

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
                request.session['has_listings'] = len(user.has_listings.all())

                # try:
                #     print(user.has_listings)
                #     has_listings = len(user.has_listings)
                # except:
                #     raise
                #     has_listings = 0

                # print(has_listings)

                # request.session['has_listings'] = has_listings

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

#### MESSAGES AND CONVERSATIONS

def all_messages(request):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    user_id = request.session['user_id']

    conversations = m.Conversation.objects.filter(Q(host_id = user_id) | Q(guest_id = user_id)).order_by('-created_at')

    context = {
        'conversations': conversations,
    }
    return render(request, 'airbnbclone/all_messages.html', context)

def convo(request, conversation_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    conversation = m.Conversation.objects.get(id = conversation_id)
    messages = m.Message.objects.filter(conversation_id = conversation_id).order_by('-created_at')

    context = {
        'conversation': conversation,
        'messages': messages,
    }
    return render(request, 'airbnbclone/convo.html', context)

def send_message(request, conversation_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    if request.method == 'POST':
        conversation = m.Conversation.objects.get(id=conversation_id)

        if len(request.POST['html_contents']) > 0:
            try:
                message = m.Message.objects.create(
                    conversation_id = conversation.id,
                    contents = request.POST['html_contents'],
                    from_user_id = request.session['user_id'],
                )
            except:
                pass

    return redirect('airbnbclone:convo', conversation_id=conversation_id)

def start_convo(request, listing_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    
    listing = m.Listing.objects.get(id = listing_id)

    conversation = m.Conversation.objects.create(
        listing_id = listing.id,
        host_id = listing.host_id,
        guest_id = request.session['user_id'],
    )

    return redirect('airbnbclone:display_convo', conversation_id=conversation.id)

def display_convo(request, conversation_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    conversation = m.Conversation.objects.get(id = conversation_id)

    context = {
        'conversation': conversation,
    } 

    return render(request, 'airbnbclone/convo.html', context)

#### BOOKINGS

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

def authenticate_booking(request):
    if request.method== "POST":
        booking = create_booking(request)
        print("==========={}=======".format(booking))

        if booking:
            return JsonResponse({"url": redirect('airbnbclone:index').url})

        errors = []
        for message in messages.get_messages(request):
            errors.append(str(message))
        
        print(errors)

        return JsonResponse({'errors': errors}, status=400)
        
    return JsonResponse({'message': 'method not allowed'})

def test_booking(request):
    avail = m.Availability.objects.filter(Q(listing_id=6) & Q(available=1)).all()
    room = [a.one_day.strftime('%m-%d-%Y') for a in avail]
    # room = {"2018-12-11": 1, "2018-06-07": 0}
    
    print("----------test_booking---------")
    print(room)
    context = {
        'room': room,
    }

    return render(request, 'airbnbclone/booking.html', context)

def create_booking(request):
    user_id = request.POST["html_user_id"]
    checkin = request.POST["html_checkin"]
    checkout = request.POST["html_checkout"]
    guests = request.POST["html_guests"]
    charge = float(request.POST["html_charge"]) * 5
    listing_id = request.POST["html_listing_id"]

    avail_list = check_dates(checkin, checkout, listing_id)
    if avail_list is None:
        messages.error(request, "Incorrect dates")
        return None

    if len(avail_list) == 0:
        messages.error(request, "No Available Dates")
        return None

    date_list, open_list = zip(*avail_list)

    if False in open_list:
        print("++++++++++++++")
        print(avail_list)
        messages.error(request, "The date range entered are not available")
        return None

    try:
        booking = m.Booking.objects.create(
            guest_id = user_id, 
            home_listing_id = listing_id, 
            from_date = checkin,
            to_date = checkout,
            num_guests = guests,
            charge_amount = charge,
        )
        print("-------{}---------".format(booking.id))
        update_avail(booking.from_date, booking.to_date, listing_id, 0)
        
    except:
        messages.error(request, "Booking cannot be completed")
        raise
    
    return booking

#### REVIEWS

def write_review(request, booking_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    booking = m.Booking.objects.get(id = booking_id)
    context = {
        'booking': booking,
    } 
    return render(request, 'airbnbclone/write_review.html', context)

def submit_review(request, booking_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    booking = m.Booking.objects.get(id = booking_id)

    review = m.Review.objects.create(
        booking_id = booking_id,
        description = request.POST["html_description"],
        star_rating = request.POST["html_star_rating"],
    )

    listing = m.Listing.objects.get(id = booking.home_listing_id)


    listing.number_reviews += 1
    listing.save()

    ratings = m.Review.objects.filter(booking__home_listing__id = booking.home_listing_id).all()

    rating_list = [rating.star_rating for rating in ratings]
    avg_rating = sum(rating_list) / float(len(rating_list))
    listing.average_rating = avg_rating
    listing.save()

    context = {
        'booking': booking,
        'review': review,
        'listing': listing,
    } 
    return render(request, 'airbnbclone/my_bookings.html', context)


#### AVAILABILITIES

def update_avail_one(add_date, listing_id, available):
    try:
        avail = m.Availability.objects.filter(Q(listing_id = listing_id) & Q(one_day = add_date)).first()
        print("=================avail")
        if avail:
            avail.available = available
            avail.save()
            print("=======available========")
        else:
            print("========not available=======")
            avail = m.Availability.objects.create(listing_id = listing_id, available=available, one_day = add_date)
            print(avail.listing.address)
    except:
        raise
        print("cannot update")
        return None

    return avail

def update_avail(start_date, end_date, listing_id, available):

    if start_date >= end_date:
        messages.error(request, "checkin date cannot be less than checkout date")
        return None

    mydates = pd.date_range(start_date, end_date).tolist()
    d_range = [d.date() for d in mydates[:-1]]
    avail_list = [update_avail_one(day, listing_id, available) for day in d_range]

    return avail_list
    
## add avail from html page using ajax
def add_avail(request):

    return render(request, 'airbnbclone/add_avail.html')


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
        
    today = datetime.date.today().strftime("%Y-%m-%d")
    if start_date < today:
        return None

    mydates = pd.date_range(start_date, end_date).tolist()
    d_range = [d.date() for d in mydates[:-1]]
    avail_list = [find_avail(day, listing_id) for day in d_range]

    return avail_list

#### LISTINGS

def listing(request, listing_id):
    try:
        room = m.Listing.objects.get(id = listing_id)
        if not room.active:
            return redirect('airbnbclone:index')
        reviews = m.Review.objects.filter(booking__home_listing_id=listing_id).order_by('-created_at')
        primary_photo = m.Photo.objects.get(listing_id = room.id, is_primary = True)
        photos = m.Photo.objects.filter(listing_id = room.id)

        if 'user_id' in request.session:
            user_id = request.session['user_id']
            fav_list = m.Favorite.objects.filter(Q(home_listing_id = room.id) & Q(guest_id = user_id))
            fav = len(fav_list)
            print("============fav")
        else:
            fav = 0

        print("========{}fav".format(fav))
        
    except:
        raise
        room = None
        return redirect('airbnbclone:index')

    context = {
        'api_key' : MAP_API_KEY,
        'room': room,
        'reviews': reviews,
        'primary' : primary_photo,
        'photos' : photos,
        'fav_status': fav,
    }
    print("listing got okay")
    print(room.address)
    return render(request, 'airbnbclone/listing.html', context)

def my_listings(request):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    
    user_id = request.session['user_id']
    my_listings = m.Listing.objects.filter(host_id = user_id)

    context = {
        'user_id': user_id,
        'my_listings': my_listings,
    }
    return render(request, 'airbnbclone/my_listings.html', context)

def my_favorites(request):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')
    
    user_id = request.session['user_id']
    my_favorites = m.Listing.objects.filter(saved_by = user_id)
    print(len(my_favorites))

    context = {
        'user_id': user_id,
        'my_favorites': my_favorites,
    }
    return render(request, 'airbnbclone/my_favorites.html', context)

def get_price_range(input):
    # if input == 1:
    #     request.session['price'] = [0.0, 50.0]
    # elif input == 2:
    #     request.session['price'] = [50.0, 100.0]
    # elif input == 3:
    #     request.session['price'] = [100.0, 150.0]
    # elif input == 4:
    #     request.session['price'] = [150.0, 200.0]
    # elif input == 5:
    #     request.session['price'] = [200.0, 250.0]
    # elif input == 6:
    #     request.session['price'] = [250.0, 300.0]
    # elif input == 7:
    #     request.session['price'] = [300.0, 400.0]
    # elif input == 8:
    #     request.session['price'] = [400.0, 500.0]
    # elif input == 9:
    #     request.session['price'] = 500.0
    # else:
    #     request.session['price'] = [0.0, 1000.0]

    if input == 1:
        return [0.0, 50.0]
    if input == 2:
        return [50.0, 100.0]
    if input == 3:
        return [100.0, 150.0]
    if input == 4:
        return [150.0, 200.0]
    if input == 5:
        return [200.0, 250.0]
    if input == 6:
        return [250.0, 300.0]
    if input == 7:
        return [300.0, 400.0]
    if input == 8:
        return [400.0, 500.0]
    if input == 9:
        return [500.0]
    else:
        return [0.0]

def filters(request):
    
#     request.session['from_date'] = request.POST["fromDate"]
#     request.session['to_date'] = request.POST["toDate"]

#     if request.POST['guests'] != "Guests":
#         request.session['guests'] = int(request.POST["guests"])
#     if request.POST['homeType'] != "Home Type":
#         request.session['home_type'] = request.POST["homeType"]
#     if request.POST['price'] != 'Price':
#         get_price_range(request, int(request.POST["price"]))
    
    return JsonResponse({})
        
def results(request):
    results = []
    if len(request.GET['html_term']) != 0:
        query = request.GET['html_term']
        for listing in m.Listing.objects.filter(active=1).filter(Q(address__icontains=query) | Q(country__icontains=query) | Q(name__icontains=query)):
            results.append(listing)
    
    print(results)
    
    if 'from_date' in request.session and 'to_date' in request.session:
        print("==========From Date: {}".format(request.session['from_date']))
        print("==========To Date: {}".format(request.session['to_date']))
    
    if 'guests' in request.session:
        for listing in m.Listing.objects.filter(max_guests__gte=request.session['guests']).filter(active=1):
            if listing not in results:
                results.append(listing)
        for result in results:
            if request.session['guests'] > result.max_guests:
                results.remove(result)
    
    if 'home_type' in request.session:
        for listing in m.Listing.objects.filter(privacy_type=request.session['home_type']).filter(active=1):
            if listing not in results:
                results.append(listing)
        for result in results:
            if request.session['home_type'] != result.privacy_type:
                results.remove(result)

    if 'price' in request.session:
        lower = request.session['price'][0]
        higher = request.session['price'][1]
        print(request.session['price'])
        for listing in m.Listing.objects.filter(price__gte=lower).filter(price__lte=higher).filter(active=1):
            if listing not in results:
                results.append(listing)

        appender = []
        for result in results:
            if not(lower < result.price < higher):
                appender.append(result)

        for append in appender:
            if append in results:
                results.remove(append)

    # gmaps = googlemaps.Client(key = MAP_API_KEY)
    # print(gmaps)
    
    # geocode_result = gmaps.geocode('query')

    # pprint(geocode_result[0][0])
    # latitude = (geocode_result[2]['geometry']['location']['lat'])
    # longitude = (geocode_result[2]['geometry']['location']['lng'])

    context = {
        'listings' : results,
        'api_key' : MAP_API_KEY,
        # 'longitude' : longitude,
        # 'latitude' : latitude,
        
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
            max_guests= request.POST['html_max_guests']

            country = request.POST['html_country'].upper()
            city = request.POST['html_city'].upper()
            address = request.POST['html_address'].upper()

            price = request.POST['html_price']
            
            name = request.POST['html_name']
            desc = request.POST['html_desc']

            amen = get_amenities("dryer")

            try:
                geo_address = get_json(get_url(address, city, country))['results'][0]
                addr_lat = geo_address['geometry']['location']['lat']
                addr_lon = geo_address['geometry']['location']['lng']
            except:
                pass

            
            listing_obj = m.Listing.objects.create(
                listing_type = listing_type,
                privacy_type = privacy_type,
                bedroom = bedroom,
                bath = bath,
                bed = bed,
                max_guests= max_guests,
                country = country,
                city = city,
                address = address,
                name = name,
                desc = desc,
                price = price,
                host_id = host,
                addr_lat = addr_lat,
                addr_lon = addr_lon,
            )

            listing_obj.active = True
            listing_obj.amenities.add(amen)
            listing_obj.save()

            if 'html_photo' in request.FILES:
                html_photo = request.FILES.getlist('html_photo')
                print(html_photo)
                fs = FileSystemStorage()
                for file in html_photo:
                    filename = fs.save(file.name, file)
                    photo = m.Photo.objects.create(listing_id = listing_obj.id, url = fs.url(filename), is_primary = False)
                    print(photo.url)
                    print(html_photo[0].name) 
                    print(photo.is_primary)
                    if "/media/{}".format(html_photo[0].name) == photo.url:
                        photo.is_primary = True
                        photo.save()



        except:
            raise
            print('This is wrong')
            return redirect('airbnbclone:index')

        return redirect('airbnbclone:listing', listing_obj.id)

    return render(request, 'airbnbclone/create_listing.html')

def save_favorite(request):

    if "user_id" not in request.session:
        return JsonResponse({'errors': "Login First", "url": redirect('airbnbclone:login').url}, status=400)
    
    if request.method == "POST":
        listing_id = request.POST["html_listing"]
        user_id = request.session['user_id']

        try:
            fav = m.Favorite.objects.get(Q(home_listing_id=listing_id) & Q(guest_id = user_id))
            fav.delete()
            fav_status = 0
        except:
            fav = m.Favorite.objects.create(home_listing_id=listing_id, guest_id=user_id)
            fav_status = 1

        context = {
            "fav": fav_status,
        }
        return JsonResponse(context)
    
    return JsonResponse({'errors': "Not Allowed", "url": redirect('airbnbclone:index').url}, status=400)
    

def distance_to_center(addr_lat, addr_lon, center_lat, center_lon):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = math.radians(addr_lat)
    lon1 = math.radians(addr_lon)
    lat2 = math.radians(center_lat)
    lon2 = math.radians(center_lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance

def filter_by(request):
    
    all_listings = m.Listing.objects.filter(active=1)

    if len(all_listings)==0:
        return JsonResponse({'errors': "No Result"}, status=400)
    
    fromDate = request.POST['html_fromDate']
    toDate = request.POST['html_toDate']
    guests = request.POST['html_guests']
    homeType = request.POST['html_homeType']
    price = request.POST['html_price']

    if guests!="Guests":
        all_listings = all_listings.filter(max_guests__gte=guests)
        if len(all_listings)==0:
            return JsonResponse({'errors': "No Result"}, status=400)
        
    if homeType!="Home Type":
        all_listings = all_listings.filter(privacy_type=homeType)
        if len(all_listings)==0:
            return JsonResponse({'errors': "No Result"}, status=400)
        
    
    if price!="Price":
        price_list = get_price_range(int(price))
        if len(price_list) == 1:
            all_listings = all_listings.filter(price__gte=price_list[0]).filter(price__lte=higher)
        elif len(price_list) == 2:
            all_listings = all_listings.filter(price__gte=price_list[0]).filter(price__lte=price_list[1])

        if len(all_listings)==0:
            return JsonResponse({'errors': "No Result"}, status=400)

    if fromDate and toDate:
        final_list = []
        for listing in all_listings:
            date_avail = check_dates(fromDate, toDate, listing.id)
            
            date_list, open_list = zip(*date_avail)

            print(date_avail)

            if 0 not in open_list:
                final_list.append(listing)

        all_listings = final_list


    if len(all_listings)==0:
        return JsonResponse({'errors': "No Result"}, status=400)
    
    address = request.POST['html_loc']
    
    if address=="":
        center_lat = 40.7178871	
        center_lon = -73.9856753
    else:
        geo_address = get_json(get_url(address, '', ''))['results'][0]
        center_lat = geo_address['geometry']['location']['lat']
        center_lon = geo_address['geometry']['location']['lng']

    results_tuple = [(distance_to_center(listing.addr_lat, listing.addr_lon, center_lat, center_lon), listing) for listing in all_listings]

    results_tuple.sort(key=itemgetter(0))

    distance, final_results = zip(*results_tuple)

    center_lat = final_results[0].addr_lat
    center_lon = final_results[0].addr_lon

    context = {
        'center_lat': center_lat,
        'center_lon': center_lon,
        'results' : json.loads(serializers.serialize("json", final_results))
    }
    return JsonResponse(context)


def search_by_map(request):
    address = request.POST['html_loc']
    geo_address = get_json(get_url(address, '', ''))['results'][0]
    center_lat = geo_address['geometry']['location']['lat']
    center_lon = geo_address['geometry']['location']['lng']

    all_listings = m.Listing.objects.all()
    results_tuple = [(distance_to_center(listing.addr_lat, listing.addr_lon, center_lat, center_lon), listing) for listing in all_listings]

    results_tuple.sort(key=itemgetter(0))

    distance, final_results = zip(*results_tuple)

    center_lat = final_results[0].addr_lat
    center_lon = final_results[0].addr_lon

    context = {
        'center_lat': center_lat,
        'center_lon': center_lon,
        'results' : json.loads(serializers.serialize("json", final_results))
    }
    return JsonResponse(context)

def results_edit(request):
    print(request.GET)
    context = {
        'listings': m.Listing.objects.all(),
        'api_key': MAP_API_KEY,
    }

    return render(request, 'airbnbclone/results_edit.html', context)


def view_maps(request):
    context = {
        'api_key': MAP_API_KEY,
    }

    return render(request, 'airbnbclone/view_maps.html', context)

def photos(request, listing_id):
    photos = m.Photo.objects.filter(listing_id = listing_id)
    context = {
        'photos' : photos,
    }
    return render(request, 'airbnbclone/photos.html', context)


    
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

gmaps = googlemaps.Client(key = MAP_API_KEY)

# Create your views here.
def index(request):
    listings_rated = []
    listings_all = []
    listings = m.Listing.objects.all()
    i = 8 
    while i < 16:
        listings_rated.append(listings[i])
        i += 1
    z = 16
    while z < 25:
        listings_all.append(listings[z])
        if z == 19:
            z += 2
        else:
            z += 1
    context = {
        "api_key": MAP_API_KEY,
        "listings_rated" : listings_rated,
        "listings_all" : listings_all,
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

    conversations = m.Conversation.objects.filter(Q(host_id = user_id) | Q(guest_id = user_id)).order_by('-updated_at')

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
                conversation.updated_at = message.created_at
                conversation.save()

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
    current_bookings = m.Booking.objects.filter(Q(to_date__gte = today) & Q(guest_id = user_id) & Q(is_cancelled = 0)).all().order_by('to_date')
    past_bookings = m.Booking.objects.filter(Q(to_date__lt = today) & Q(guest_id = user_id) & Q(is_cancelled = 0)).all().order_by('-to_date')

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
            return JsonResponse({"url": redirect('airbnbclone:my_bookings').url})

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
    charge = float(request.POST["html_charge"])
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

    else:
        charge=charge*len(open_list)

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
    # return render(request, 'airbnbclone/my_bookings.html', context)
    return redirect('airbnbclone:my_bookings')


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
    my_favorites = m.Listing.objects.filter(saved_by__guest_id = user_id)

    fav_photos = []

    for my_favorite in my_favorites:
        photo = m.Photo.objects.get(listing_id = my_favorite.id, is_primary = 1)
        fav_photos.append(photo)

    print(fav_photos)

    context = {
        'user_id': user_id,
        'my_favorites': my_favorites,
        'fav_photos': fav_photos,
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
    return render(request, 'airbnbclone/awesomeforms.html')

def get_url(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(address, MAP_API_KEY)
    return url

def get_json(url):
    resp = requests.get(url)
    return json.loads(resp.text)

def edit_listing(request, listing_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:index')

    try:
        listing = m.Listing.objects.get(id = listing_id)
    except:
        return redirect('airbnbclone:index')
    
    try:
        primary_photo = m.Photo.objects.get(listing_id = listing.id, is_primary=1)
    except:
        primary_photo = None
        
    if listing and listing.host_id == request.session['user_id']:
        context = {
            "room": listing,
            "primary": primary_photo
        }
        return render(request, 'airbnbclone/edit_listing.html', context)

    return redirect('airbnbclone:index')

def create_steps(request):
    amen_list = m.Amenity.objects.all()
    print(amen_list)
    context = {
        'hide_search': True, 
        'api_key': MAP_API_KEY,
        'amen_list': amen_list,
    }
    return render(request, 'airbnbclone/create_steps.html', context)

def find_address(request):

    if request.method == "POST":

        try:
            city = None
            country = None
            address = request.POST['address']
            geo_address = get_json(get_url(address))['results'][0]
            long_address = geo_address['formatted_address']
            for addr in geo_address['address_components']:
                if 'administrative_area_level_1' in addr['types'] or 'postal_town' in addr['types'] or 'locality' in addr['types']:
                    if not city:
                        city = addr['long_name']
                elif 'country' in addr['types']:
                    country = addr['long_name']
            
            addr_lat = geo_address['geometry']['location']['lat']
            addr_lon = geo_address['geometry']['location']['lng']

            context = {
                'long_address': long_address,
                'city': city,
                'country': country,
                'geo_address': geo_address,
                'addr_lat': addr_lat,
                'addr_lon': addr_lon,
            }

            return JsonResponse(context)

        except:
            context = {
                "errors": "Address Error",
                "url": redirect('airbnbclone:login').url
            }
            return JsonResponse(context, status=401)


def create_listing(request):

    if 'user_id' not in request.session:
        context = {
            "errors": "Login First",
            "url": redirect('airbnbclone:login').url
        }
        
        return JsonResponse(context, status=400)

    if request.method == 'POST':
        print(request.POST)
        errors = {}
        check_list = ['html_listing_type', 'html_privacy_type', 'html_bedroom', 'html_bath',
            'html_bed', 'html_max_guests', 'html_address', 'html_price', 'html_name', 'html_desc',
            'html_start_date', 'html_end_date']

        for check in check_list:
            if check in request.POST:
                if request.POST[check]=='':
                    errors[check]="Cannot be blank"
                else:
                    pass
            else:
                errors[check]="Need to be filled"

        if len(errors)>0:
            print(errors)
            context = {
                "errors": errors
            }
            return JsonResponse(context, status=400)

        try:
            host = request.session['user_id']

            listing_type = request.POST['html_listing_type']
            privacy_type = request.POST['html_privacy_type']
            bedroom = request.POST['html_bedroom']
            bath = request.POST['html_bath']
            bed = request.POST['html_bed']
            max_guests= request.POST['html_max_guests']

            address = request.POST['html_address']

            price = request.POST['html_price']
            
            name = request.POST['html_name']
            desc = request.POST['html_desc']

            country = request.POST['html_country']
            city = request.POST['html_city']

            addr_lat = request.POST['html_lat']
            addr_lon = request.POST['html_lon']

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

            return JsonResponse({"listing_id": listing_obj.id})

        except:
            raise
            
    context = {
        "errors": "Listing cannot be created. Try Again."
    }

    return JsonResponse(context, status=401)


def add_amenity(request):
    
    # amen_list = m.Amenity.objects.all()
    # for amen in amen_list:
    #     if amen.font_class in request.POST:
    #         listing_obj.amenities.add(amen)

    pass
            
def add_dates(request):
    if request.method == "POST":
        print(request.POST)
        try:
            listing_id=request.POST['html_listing_id']
            from_date = request.POST['html_start_date']
            to_date = request.POST['html_end_date']
            price = request.POST['html_price']
            listing = m.Listing.objects.get(id = listing_id)
            listing.price = price
            listing.save()

            update_avail(from_date, to_date, listing_id, 1)
        except:
            raise
            return JsonResponse({"errors": "Incorrect Date Entered"}, status=401)
        
        context = {
            "message": "Date and Price Updated",
            "price": price
        }
        return JsonResponse(context)

    return JsonResponse({"Errors": "Bad Path"}, status=400)

def add_photo(request):

    if request.method == "POST":

        listing_id = request.POST['html_listing_id']
        print("in add_photo")

        try:
            if 'html_photo' in request.FILES:
                html_photo = request.FILES.getlist('html_photo')
                print("get_photo")
                fs = FileSystemStorage()
                photo = None
                for file in html_photo:
                    filename = fs.save(file.name, file)
                    photo = m.Photo.objects.create(listing_id = listing_id, url = fs.url(filename), is_primary = False)

                for old_photo in m.Photo.objects.filter(listing_id = listing_id):
                    old_photo.is_primary= 0
                    old_photo.save()
                
                photo.is_primary = True
                photo.save()
                context = {
                    "room": m.Listing.objects.get(id = listing_id),
                    "primary": photo,
                }

                return render(request, 'airbnbclone/edit_listing.html', context)
        except:
            pass

    return redirect('airbnbclone:index')

def add_listing(request):

    if 'user_id' not in request.session:
        context = {
            "errors": "Login First",
            "url": redirect('airbnbclone:login').url
        }
        
        return JsonResponse(context, status=400)

    if request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        try:
            host = request.session['user_id']
            listing_type = request.POST['html_listing_type']
            privacy_type = request.POST['html_privacy_type']
            bedroom = request.POST['html_bedroom']
            bath = request.POST['html_bath']
            bed = request.POST['html_bed']
            max_guests= request.POST['html_max_guests']

            address = request.POST['html_address'].upper()

            price = request.POST['html_price']
            
            name = request.POST['html_name']
            desc = request.POST['html_desc']

            country = request.POST['html_country'].upper()
            city = request.POST['html_city'].upper()

            try:
                geo_address = get_json(get_url(address))['results'][0]

                for addr in geo_address['address_components']:
                    if 'locality' in addr['types']:
                        city = addr['long_name']
                    elif 'country' in addr['types']:
                        country = addr['long_name']

                print("========={}".format(city))
                print("=========={}".format(country))
                
                addr_lat = geo_address['geometry']['location']['lat']
                addr_lon = geo_address['geometry']['location']['lng']
            except:
                context = {
                    "errors": "Address Error",
                    "url": redirect('airbnbclone:login').url
                }
                return JsonResponse(context, status=401)
            
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

            # amen_list = m.Amenity.objects.all()

            # for amen in amen_list:
            #     if amen.font_class in request.POST:
            #         listing_obj.amenities.add(amen)
            
            from_date = request.POST['html_start_date']
            to_date = request.POST['html_end_date']
            
            try:
                update_avail(from_date, to_date, listing_obj.id, 1)
            except:
                return JsonResponse({"errors": "Incorrect Dates"})
            
            listing_obj.save()

            if 'html_photo' in request.FILES:
                html_photo = request.FILES.getlist('html_photo')
                fs = FileSystemStorage()
                photo = None
                for file in html_photo:
                    filename = fs.save(file.name, file)
                    photo = m.Photo.objects.create(listing_id = listing_obj.id, url = fs.url(filename), is_primary = False)
                
                photo.is_primary = True
                photo.save()

        except:
            return JsonResponse({"errors": "Incorrect Dates"}, status=400)
            
        
        context = {
            "success": "good job",
            "url": "/listing/"+listing_obj.id
        }

        return JsonResponse(context)

    return render(request, 'airbnbclone/create_listing.html', {'hide_search': True, 'api_key': MAP_API_KEY})

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
    
def un_favorite(request, listing_id):
    if 'user_id' not in request.session:
        return redirect('airbnbclone:login')
    
    user_id = request.session['user_id']
    try:
        fav = m.Favorite.objects.get(Q(home_listing_id = listing_id) & Q(guest_id = user_id))
        fav.delete()
    except:
        pass

    return redirect('airbnbclone:my_favorites')
    

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
        geo_address = get_json(get_url(address))['results'][0]
        center_lat = geo_address['geometry']['location']['lat']
        center_lon = geo_address['geometry']['location']['lng']

    results_tuple = [(distance_to_center(listing.addr_lat, listing.addr_lon, center_lat, center_lon), listing) for listing in all_listings]

    results_tuple.sort(key=itemgetter(0))

    distance, final_results = zip(*results_tuple)

    center_lat = final_results[0].addr_lat
    center_lon = final_results[0].addr_lon

    photo_array = [m.Photo.objects.get(listing_id = listing.id) for listing in final_results]

    print("photoarrya okay")

    context = {
        'center_lat': center_lat,
        'center_lon': center_lon,
        'results' : json.loads(serializers.serialize("json", final_results)),
        'images' : json.loads(serializers.serialize("json", photo_array)),
    }
    return JsonResponse(context)

    
def search_by_map(request):
    print("here")
    address = request.POST['html_loc']
    print(address)
    geo_address = get_json(get_url(address))['results'][0]
    center_lat = geo_address['geometry']['location']['lat']
    center_lon = geo_address['geometry']['location']['lng']

    all_listings = m.Listing.objects.filter(active=1).order_by("id").all()[:38]

    if len(all_listings)==0:
        return JsonResponse({'errors': "No Result"}, status=400)

    # results_tuple = []

    # for listing in all_listings:
    #     dist = distance_to_center(listing.addr_lat, listing.addr_lon, center_lat, center_lon)
    #     if dist < 100:
    #         results_tuple.append((dist, listing))

    results_tuple = [(distance_to_center(listing.addr_lat, listing.addr_lon, center_lat, center_lon), listing) for listing in all_listings]

    results_tuple.sort(key=itemgetter(0))

    distance, final_results = zip(*results_tuple)

    center_lat = final_results[0].addr_lat
    center_lon = final_results[0].addr_lon

    photo_array = [m.Photo.objects.get(listing_id = listing.id) for listing in final_results]

    context = {
        'center_lat': center_lat,
        'center_lon': center_lon,
        'results' : json.loads(serializers.serialize("json", final_results)),
        'images' : json.loads(serializers.serialize("json", photo_array)),
    }
    return JsonResponse(context)

def results_edit(request):
    print(request.GET)
    context = {
        'listings': m.Listing.objects.all(),
        'api_key': MAP_API_KEY,
    }

    return render(request, 'airbnbclone/results_edit.html', context)

def awesomeforms(request):

    amen_list = m.Amenity.objects.all()
    
    context = {
        "amen_list": m.Amenity.objects.all(),
        "api_key": MAP_API_KEY,
    }
    return render(request, 'airbnbclone/awesomeforms.html', context)

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


    
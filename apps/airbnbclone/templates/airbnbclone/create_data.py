import googlemaps
from datetime import datetime

import django

import data_constants as const
import apps.airbnbclone.models as m
import random

from pprint import pprint

django.setup()

gmaps = googlemaps.Client(key='AIzaSyDSLQt7KusqUJAwSxviZ2iBJ371b5mI3EQ')


FIRST_NAMES = ['Ned', 'John', 'Arya', 'Sansa', 'Cersei', 'Rob', 'Jorah', 'Daenerys', 'Joffrey', 'Robert', 'Samwell', 'Catelyn', 'Oberyn', 'Gregor', 'Rhaegar', 'Sandor']
LAST_NAMES = ['Clegane', 'Baratheon', 'Targareyen', 'Stark', 'Lannister', 'Arryn', 'Tully', 'Greyjoy', 'Umber', 'Martel', 'Tarly', 'Mormont', 'Glover']

NAMES = ['Mansion', 'Party House', 'Riverfront', 'Time of your Life', 'FOMO', 'YOLO', 'Boathouse', 'Beach villa', 'Dreams come true', 'Trump Palace', 'Royal Residences', 'Grand Hotel']

STAY_TYPE = ['Entire place','Private room','Shared room']
PROP_TYPE = ['House','Apartment','Bed and breakfast','Boutique hotel','Bungalow', 'Cabin','Chalet','Cottage','Guest suite','Guesthouse','Hostel','Hotel','Loft','Resort','Townhouse', 'Villa']
UNIQ_TYPE = ['Barn','Boat','Camper/RV','Campsite','Casa particular','Castle','Cave','Cycladic house','Dammuso','Dome house','Earth house','Farm stay','Houseboat','Hut','Igloo','Island','Lighthouse','Minsu','Nature lodge','Pension (South Korea)','Plane','Ryokan','Shepherdshut (U.K., France)','Tent','Tiny house','Tipi','Train','Treehouse','Trullo','Windmill','Yurt']
AMENITIES = [{ 'icon': 'fa-cutlery', 'name': 'Kitchen'},
{ 'icon': 'fa-shower', 'name': 'Shower'},
{ 'icon': 'fa-snowflake-o', 'name': 'A/C'},
{ 'icon': 'fa-bathtub', 'name': 'Bathtub'},
{ 'icon': 'fa-wifi', 'name': 'Wifi'},
{ 'icon': 'fa-coffee', 'name': 'Breakfast'},
{ 'icon': 'fa-fire', 'name': 'Fireplace'},
{ 'icon': 'fa-bell', 'name': 'Buzzer/wireless intercom'},
{ 'icon': 'fa-male', 'name': 'Doorman'},
{ 'icon': 'fa-female', 'name': 'Hair dryer'},
{ 'icon': 'fa-desktop', 'name': 'Workspace'},
{ 'icon': 'fa-television', 'name': 'TV'},
{ 'icon': 'fa-child', 'name': 'High chair'},
{ 'icon': 'fa-video-camera', 'name': 'Self check-in'},
{ 'icon': 'fa-fire-extinguisher', 'name': 'Fire extinguisher'},
{ 'icon': 'fa-gamepad', 'name': 'Game console'},]

FACILITIES = ['Free parking','Gym','Hot tub','Pool']
RULES = [('Events allowed','No events allowed'),('Pets allowed','No pets allowed'),('Smoking permitted','Smoking not permitted')]

ADDRESSES = [
    { 'street_addr': '5757 Wilshire Blvd #106'},
    { 'street_addr': '1161 Westwood Blvd'},
    { 'street_addr': '11707 San Vicente Blvd'},
    { 'street_addr': '3242 Cahuenga Blvd W'},
    { 'street_addr': '5453 Hollywood Blvd'},
    { 'street_addr': '138 S Central Ave'},
    { 'street_addr': '3722 Crenshaw Blvd'},
    { 'street_addr': '8817 S Sepulveda Blvd'},
    { 'street_addr': '5855 W Century Blvd'},
    { 'street_addr': '120 S Los Angeles St #110'},
    { 'street_addr': '555 W 5th St'},
    { 'street_addr': '800 W Olympic Blvd #102'},
    { 'street_addr': '1850 W Slauson Ave'},
    { 'street_addr': '5857 S Central Ave'},
    { 'street_addr': '906 Goodrich Blvd'},
    { 'street_addr': '7724 Telegraph Rd'},
    { 'street_addr': '17254 Lakewood Blvd'},
    { 'street_addr': '429 Los Cerritos Center'},
    { 'street_addr': '3575 Katella Ave'},
    { 'street_addr': '1680 W Lomita Blvd'},
    { 'street_addr': '8152 Sunset Blvd'},
    { 'street_addr': '5223 W Century Blvd'},
    { 'street_addr': '4947 Huntington Dr'},
    { 'street_addr': '14742 Oxnard St'},
    { 'street_addr': '5933 York Blvd'},
    { 'street_addr': '2319 N San Fernando Rd'},
    { 'street_addr': '4655 Hollywood Blvd'},
    { 'street_addr': '6250 Hollywood Blvd'},
    { 'street_addr': '400 World Way'},
    { 'street_addr': '11603 Slater St'},
    { 'street_addr': '8581 W Pico Blvd'},
    { 'street_addr': '189 The Grove Dr'},
    { 'street_addr': '901 South La Brea Ave #2'},
    { 'street_addr': '4301 W Pico Blvd'},
    { 'street_addr': '2575 W Pico Blvd'},
    { 'street_addr': '852 S Broadway'},
    { 'street_addr': '5601 Melrose Ave'},
    { 'street_addr': '1528 North Vermont Avenue C'},
    { 'street_addr': '523 N Fairfax Ave'},
    
    { 'street_addr': 'Paseo de la Reforma s/n'},
    { 'street_addr': 'Paseo de la Reforma 476'},
    { 'street_addr': 'Insurgentes Sur 235'},
    { 'street_addr': 'Calle Durango 205 Local 1'},
    { 'street_addr': 'Calle Hamburgo 87'},

    { 'street_addr': '463 Saint-Catherine'},
    { 'street_addr': '2050 Rue de Bleury'},
    { 'street_addr': '150 Saint-Catherine St'},
    { 'street_addr': '245 Sherbrooke St'},
    { 'street_addr': '262 Saint-Catherine St'},
    
]

def make_user():
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return {'email': '{}@{}.com'.format(first_name, last_name).lower(), 'name': '{} {}'.format(first_name, last_name), 'password': '123'}

def create_amenities():
    for am in AMENITIES:
        m.Amenity.objects.create(name=am['name'], font_class=am['icon'])

def create_users():
    for i in range(1, 100):
        try:
            user = make_user()
            m.User.objects.create(email=user['email'], username=user['name'], password=user['password'])
        except:
            pass

def get_component(component):
    def get_filter(city_data):
        for item in city_data:
            if component in item['types']:
                return item['long_name']
    return get_filter


def create_listings():
    for addr in ADDRESSES:
        address = addr['street_addr']
        google_address = gmaps.geocode(address)[0]
        location = google_address['geometry']['location']
        city = get_component('locality')(google_address['address_components'])
        country = get_component('country')(google_address['address_components'])
        addr_lat = float(location['lat'])
        addr_lon = float(location['lng'])

        user_id = random.choice(range(1, 51))
        listing_type = random.choice(PROP_TYPE)
        privacy_type = random.choice(STAY_TYPE)
        bedroom = random.choice(range(1, 50))
        bed = random.choice(range(1, 30))
        bath = random.choice(range(1, 25))
        max_guests = random.choice(range(1, 20))
        
        price = random.choice(range(50, 1000))
        active = True

        name = '{} {}'.format(random.choice(LAST_NAMES), random.choice(NAMES))
        description = ''

        listing = m.Listing.objects.create(host_id=user_id, listing_type=listing_type, privacy_type=privacy_type, bedroom=bedroom, bath=bath, bed=bed , max_guests=max_guests, city=city, country=country, address=address, price=price, active=True, name=name, desc=description, addr_lat=addr_lat, addr_lon=addr_lon) 

        amenities = []
        for i in range(3, len(AMENITIES)):
            name = random.choice(AMENITIES)['name']
            if name not in amenities:
                amenities.append(name)

        for name in amenities:
            listing.amenities.add(m.Amenity.objects.get(name=name))
        listing.save()
        


def create_data():
    create_amenities()
    create_users()
    create_listings()
from shutil import copyfile
import googlemaps
from datetime import datetime

import django

import apps.airbnbclone.models as m
import random
from django.core.files.storage import FileSystemStorage

import os

from pprint import pprint

django.setup()

gmaps = googlemaps.Client(key='AIzaSyDSLQt7KusqUJAwSxviZ2iBJ371b5mI3EQ')


REVIEWS = [
    'Excellent view. Excellent location for relax and getting away from the city. Many great location for taking photos. Excellent housekeepers. Overall, excellent experience stayef at your place. Thank you.',
    'Nika was very helpful, we didnt meet her but her assistant was there to greet us and show us around when we arrived.',
    'Lovely place! Scenic view, great amenities, stylish accommodation!',
    'If you think the pictures are amazing, wait until you see it in person!!! The views are mesmerizing but mornings and evenings will take your breath away! Such a dreamy place with lots of space and privacy.',
    'The place looks even more amazing IRL. We had an amazing time at the house, check-in went fine, food ordering was also simple.',
    'Our stay was truly magical!',
    'Great place for a group of friends. Buy all of your supplies for food and drink before checking in',
    'It was the most special house I stayed. I feel so lucky to live here for one night. But I will advice everyone you should stay here at least two night! I like the style of the house.',
    'A Gem!!!',
    'Unbelievably beautiful house! I recommend you stay here. It is even more beautiful than in the photo. My family enjoyed the house a lot! Only thing I regret is that we just spent only one night there! I recommend you to stay here!',
    'The place is very stylish and has all the things you could ask for. Cleanliness was an issue. There were bugs and ants in parts of the house. I even saw a lizard in the kitchen area. If they work on the cleanliness and bugs issue, the house would be perfect.',
    'It’s a great place,with peaceful,convenient and poetic！thanks!',
    'What. A. View I had a huge smile on my face upon entering the hideaway. The view was just glorious we were so happy to just sit and stare at it all day. ',
    'This place is better than what we could have imagined. We only were able to stay one night, but SO glad we did. The swing is the highlight and so nice to be able to swing whenever on your own terms rather than paying to swing next door.',
    'Best place Ive ever been too Amazing view, fantastic house!!',
    'What an incredible place! The view is breathtaking, I was so overcome when I saw it, I felt like crying! Such a beautiful place and the swing...wow!!',
    'An amazing view and very private space. That was exactly what we were looking for.',
    'Amazing tranquil, relaxing place to find your Zen. View just couldnt get any better. Having own transport would make things a bit easier. Having your own food supplies would also be preferable also.',
    'What a wonderful place. The view is amazing. When you sit on the swing you feel like flying over the valley. The house is beautiful, calming atmosphere, all to maximise the joy you will get from the view and the location. Very nice and helpfull staff, they have thought of everything.',
    'BOOK. THIS. AIRBNB. Thats it. This is an amazing minimalist property. Thats not to say that the amenities are lacking - in fact, they are perfect!',
    'Spectacular territorial views and impressive interior design details with all the key amenities available ( kitchen with gas, refrigerator, filter water; AC bedroom; washer/dryer; good shower and bathroom). This place really is one of a kind.',
    'Perfect location in Paradise! Beautiful for photos and your own hide away spot!',
    'Absolutely stunning home, with magical surroundings. And that swing. Communication was solid - if youre not already on (Hidden by Airbnb) , Id recommend that in case the airbnb app has trouble connecting.',
    'What a truly amazing experience and I would recommend this place to anyone. Next time we are in Bali we want to bring all our friends here. cool vibes, cool swing - amazing experience.',
    'Absolutely amazing stay! Its a Paradies!',
    'Have to live once before you die',
    'I was so excited to get to the Zen Hideaway because of all the amazing reviews and pictures. As soon as I walked in and saw it in person, my jaw literally dropped. ',
    'What an amazing experience - just magic! The swing is everything you could hope for. Its beautifully appointed and has everything you could possibly think to need (the yoga mats were a great touch!) ',
    'Beautiful',
    'Incredible house, swing is so much fun! Definitely recommend ',
    'Photos dont do this place justice! It was absolutely stunning and wish we couldve spent more time there.',
    'It is a good place to relax the mind.',
    'Was in awe when we stepped into the villa. The view was amazing and I never felt so close to nature before. The place was well equipped.',
    'This is a magic inspirational place that we will never forget!',
    'Wow what an amazing house and the view is spectacular. Like in a dream. We would love to come back.',
    'Such an amazing place to stay! The housekeepers were super helpfull and the house was probably the most beautiful i have ever seen. I would love to get back there some day!',
    'Five stars in every way. Incredible home, amazing host and unbelievable experience! Absolutely loved this place! Would recommend to anyone! Best of the best!',
    'Love the location of the house, it allowed us to explore the island to areas we may have not even been aware of. ',
    'Loved This place . So unique . We I’ll never Forget it. We will be Back!',
    'A more beautiful place could not exist. It looks great in photos but it looks EVEN BETTER in person. Easy to get to, daily housekeeping, perfect pool, quiet location. Just paradise with a full moon. Grateful to experience a place such as this. Thank you to all who helped make this place a reality. My birthday was the best yet.',
    'The pictures dont do justice to the magic of this place. We live 10 mins away from this place so, youd expect us to know the neighborhood. Well, no... it felt like we were teleported to another dimension. Right in the middle of the city is this wonderland. Absolutely amazingly built. This is a perfect getaway. I would suggest to loose all your electronics and digital gadgets in the car and enjoy the nature for the duration you are here.',
    'Had a great time With Irene and her sweet parents. The place is stunning and you get to be part of a Real Italian family. The wifi wasnt so strong, so instead you Can relax and Enjoy the wonderful view!',
    'Staying here is a truly incredible experience. The breakfast we were given each morning was home cooked, seasoned with herbs from the garden and unbelievable! The surrounding area is beautiful and the home is well located.',
    'We had a wonderful stay, thank you Anna for being so welcoming and helpful. Hope to be back again.',
    'Staying at House on the lake was absolutely wonderful. Irenes parents - Anna and Cezare were our hosts during our staying, available in every time for everything. Wonderful, smart and experienced people, living the inspiring life, worth of admiration',
    'The most incredible Airbnb experience I have ever had. Anna & her husband are two of the most lovely hosts you could imagine coming by. If there was such a thing as a Super Duper host these guys would have it! ',
    'The best breakfast we had in years!!! The breakfast itself is worth the price!! We had a really relaxed time at Irenes place, the sight on the lake is beautiful and exactly as seen in the pictures!',



]

def create_reviews():
    for review in REVIEWS:
        booking_id = random.choice(range(1, 36))
        rating = random.choice(range(3, 6))
        review_objs = m.Review.objects.create(booking_id = booking_id, description = review, star_rating = rating)



def create_bookings():
    for i in m.Listing.objects.all():
        user_id = random.choice(range(1, 51))
        listing_id = random.choice(range(1, 36))
        charge_amt = random.choice(range(10, 1000))
        guests = random.choice(range(0, 100))
        to_date = "2018-0{}-{}".format(random.choice(range(3, 10)), random.choice(range(14, 30)))
        from_date = "2018-03-13"
        


        m.Booking.objects.create(guest_id = user_id, home_listing_id = listing_id, charge_amount = charge_amt, num_guests = guests, from_date = from_date, to_date = to_date)



MEDIA_DIR = '/media/'
IMAGE_ROOT = '/Users/CryptoWork/Downloads/images/'
file_names = []
def create_images():
    for image in (os.listdir(IMAGE_ROOT)):
        file_names.append(image)    
    for name in file_names:
        print(IMAGE_ROOT+name)
        copyfile(IMAGE_ROOT+name, './'+MEDIA_DIR+name)
    for listing in m.Listing.objects.all():
        m.Photo.objects.create(listing=listing, url = MEDIA_DIR + file_names[listing.id], is_primary = True)


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
    create_images()
    create_bookings()
    create_reviews()

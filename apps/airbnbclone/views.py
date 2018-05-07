from django.shortcuts import render, redirect
import googlemaps
from datetime import datetime
from pprint import pprint
from apps.airbnbclone.constants import MAP_API_KEY
import apps.airbnbclone.models as m

# Create your views here.
def index(request):
    return render(request, 'airbnbclone/index.html')

def map(request):
    query = request.GET["html_term".replace(" ", "+")]
    
    context = {
        'api_key' : MAP_API_KEY,
        'query' : query
    }
    return render(request, 'airbnbclone/map.html', context)

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
    

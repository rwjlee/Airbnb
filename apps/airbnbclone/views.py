from django.shortcuts import render, redirect
import googlemaps
from datetime import datetime
from pprint import pprint
from apps.airbnbclone.constants import MAP_API_KEY

# Create your views here.
def index(request):
    return render(request, 'airbnbclone/index.html')

def listing(request):
    query = request.GET["html_term".replace(" ", "+")]

    context = {
        'api_key' : MAP_API_KEY,
        'query' : query
    }
    return render(request, 'airbnbclone/listing.html', context)


    

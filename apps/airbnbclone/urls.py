from django.urls import path
from . import views

app_name = 'airbnbclone'

urlpatterns = [
    path('', views.index, name='index'),

    path('create_listing', views.create_listing, name='create_listing'),
    path('become_a_host', views.become_a_host, name='become_a_host'),

    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('view_profile/<int:user_id>', views.view_profile, name='view_profile'),
    path('listing/<int:listing_id>', views.listing, name='listing'),
    path('results', views.results, name='results'),
    path('filters', views.filters, name='filters'),
    path('authenticate_booking', views.authenticate_booking, name='authenticate_booking'),
    
    path('test_booking', views.test_booking, name='test_booking'),
    path('my_bookings', views.my_bookings, name='my_bookings'),
    path('cancel_booking/<int:booking_id>', views.cancel_booking, name='cancel_booking'),
]
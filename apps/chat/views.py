from django.shortcuts import render, redirect


def index(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    if 'user_id' in request.session:
        context = {
            'room_name': room_name
        }
        return render(request, 'chat/room.html', context)
        
    return redirect('airbnbclone:index')


def create_room(request):
    if request.method == 'POST':
        return redirect('chat:room', room_name=request.POST['room_name'].replace(' ', '-'))
    
    return redirect('airbnbclone:index')
from django.shortcuts import render

# Create your views here.

def addfriend(request):
  pass


def myfriends(request):
  return render(request, 'friends/myfriends.html')

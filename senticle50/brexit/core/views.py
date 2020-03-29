from django.shortcuts import render
from scraper.views import get_most_recent_tweets


# Create your views here.
def index(request):
    return render(request, 'core/index.html', {})


def home(request):
    return render(request, 'core/home.html', {"nav_page": "home", "tweets": get_most_recent_tweets(request)})


def about(request):
    return render(request, 'core/about.html', {"nav_page": "about"})


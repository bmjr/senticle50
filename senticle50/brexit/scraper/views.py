from django.db import connections
from django.db.models import Count
from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render

from .models import Tweet


def tweet_count_by_month(request):
    data = Tweet.objects.all() \
        .extra(select={
        'month': connections[Tweet.objects.db].ops.date_trunc_sql('month',
                                                                  'date')
    }
    ) \
        .values('month') \
        .annotate(count_items=Count('id')) \
        .order_by('month')

    return JsonResponse(list(data), safe=False)


def get_most_recent_tweets(request):
    return list(Tweet.objects.exclude(text__contains='\n').exclude(text=None)
                .order_by('-date').values_list('text', flat=True)[:50])


def data(request):
    items_per_page = 100
    current_page = request.GET.get('page_number')

    try:
        current_page_int = int(current_page)
    except Exception:
        current_page_int = 1

    if current_page_int < 1:
        raise Http404

    offset = (current_page_int - 1) * items_per_page

    link_prefix = str(
        request.build_absolute_uri('/')[
        :-1]) + '/data/' + '?page_number='

    tweets = Tweet.objects.filter(~Q(text=None)) \
                 .order_by('-date')[offset:offset + items_per_page + 1]

    next_page = ""
    prev_page = ""

    items_retrieved = tweets.count()

    if items_retrieved == 0:
        raise Http404

    if items_retrieved > items_per_page:
        next_page = link_prefix + str(current_page_int + 1)

    if current_page_int > 1:
        prev_page = link_prefix + str(current_page_int - 1)

    return render(request, 'core/data.html',
                  {"nav_page": 'data',
                   "tweets": tweets[:items_per_page],
                   "next_page_link": next_page,
                   "prev_page_link": prev_page})

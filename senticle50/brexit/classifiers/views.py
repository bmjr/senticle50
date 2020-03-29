import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q, F
from django.db.models import Sum
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render

from classifiers.models import ClassifiedDay, ClassificationType, ClassifiedTweet
from scraper.models import Day
from .entities.Classification import Classification
from .serializers.ClassifiedDaySerializer import ClassifiedDaySerializer


def classified_tweet_count_by_day(request):
    data = ClassifiedDay.objects \
        .filter(
        Q(classification_type=ClassificationType.leave_eu) | Q(
            classification_type=ClassificationType.remain_eu)) \
        .order_by('date')

    classified_days = dict()

    for day in data:
        if day.classification_type.id == ClassificationType.leave_eu:
            day.classification_name = "leave"
        else:
            day.classification_name = "remain"

        existing_day = classified_days.get(day.date)
        if existing_day is not None:
            classification_name = day.classification_name
            new_classification = Classification(classification_name,
                                                day.classification_value)
            classification_list = existing_day.classifications
            classification_list.insert(len(classification_list),
                                       new_classification)
            existing_day.classifications = classification_list
        else:
            new_day = ClassifiedDay(day.date, None)
            classification_name = day.classification_name
            new_classification = Classification(classification_name,
                                                day.classification_value)
            classification_list = new_day.classifications
            classification_list.insert(len(classification_list),
                                       new_classification)
            new_day.classifications = classification_list
            classified_days.update({day.date: new_day})

    serializer = ClassifiedDaySerializer(classified_days.values(), many=True)

    return JsonResponse(serializer.data, safe=False)


def preview_data_year(request, classifier):
    rows = []
    row = []
    selected = 'year'
    next_granularity = 'month'

    classification_type = get_classifier(classifier)
    title = classification_type.display_title

    year = request.GET.get('time_period')
    date_time = get_date('01/01/' + year, '%d/%m/%Y', selected)
    original_date_time = date_time

    time_title = year

    total_tweets = Day.objects \
        .filter(Q(date__year=year)) \
        .extra({'time_unit': "Extract(month from date)"}) \
        .values('time_unit') \
        .annotate(value=Sum('tweet_number')) \
        .order_by('time_unit')

    tweet_tuples = []
    for entry in total_tweets:
        tweet_tuples.append((date_time.replace(month=int(entry['time_unit']), day=1), entry['value']))

    tweet_timestamps = get_tweet_timestamps(tweet_tuples)

    classified_months = ClassifiedDay.objects \
        .filter(Q(classification_type=classification_type) &
                Q(date__year=year) &
                Q(classification_type__label__classification_value=F('classification_value'))) \
        .extra({'time_unit': "Extract(month from date)"}) \
        .values('time_unit', 'classification_value', 'classification_type__label__name', 'classification_type__label__color') \
        .annotate(value=Sum('amount_classified'))

    link_prefix = str(
        request.build_absolute_uri('/')[:-1]) + '/analysis/' \
                  + classifier + '/' + next_granularity + '?time_period='

    classifier_summary_classifications = {}
    classified_counts = {}
    classification_colors = {}
    classifications_exist = False
    for month in range(1, 13):
        month_classifications = get_classifications_by_unit_of_time(
            month, classified_months)
        classifications = []
        for classification in month_classifications:
            classifications_exist = True
            if classification['classification_type__label__name'] in classifier_summary_classifications:
                classifier_summary_classifications[
                    classification['classification_type__label__name']] += classification[
                    'value']
                classified_counts[classification['classification_type__label__name']].append((date_time.replace(month=month, day=1), classification['value']))
            else:
                classifier_summary_classifications[
                    classification['classification_type__label__name']] = classification[
                    'value']
                classified_counts[
                    classification['classification_type__label__name']] = [
                    (date_time.replace(month=month, day=1), classification['value'])]
                classification_colors[
                    classification['classification_type__label__name']] = \
                classification['classification_type__label__color']

            classifications.append(
                {'label': classification['classification_type__label__name'],
                 'value': int(classification['value'])})

        if month % 4 == 0:
            month = {
                'text': date_time.replace(month=month, day=1).strftime("%b"),
                'classifications': classifications,
                'link': link_prefix + date_time.strftime("%m/%Y")
            }
            row.append(month)
            rows.append(row)
            row = []
        else:
            month = {
                'text': date_time.replace(month=month, day=1).strftime("%b"),
                'classifications': classifications,
                'link': link_prefix + date_time.replace(month=month, day=1).strftime("%m/%Y")
            }
            row.append(month)

    for entry in classified_counts:
        classified_counts[entry] = get_tweet_timestamps(classified_counts[entry])

    return render(request, 'core/classifier-analysis.html', {"nav_page": 'analysis',
                                                  "title": title,
                                                  "selected": selected,
                                                  "classifications_exist": classifications_exist,
                                                  "classification_counts": classified_counts,
                                                  "classification_colors": classification_colors,
                                                  "total_tweets": tweet_timestamps,
                                                  "item_rows": rows,
                                                  "classifier_summary": get_classifier_summary(
                                                      classifier_summary_classifications,
                                                      next_granularity, '"%m"'),
                                                  "top_tweet_parameters": get_top_tweet_parameters(int(classification_type.id), date_time, datetime.strptime('31/12/' + year, '%d/%m/%Y')),
                                                  "time_switcher": get_time_switcher_links(request, time_title, classifier, original_date_time, selected)
                                                  })


def preview_data_month(request, classifier):
    rows = []
    row = []
    selected = 'month'
    next_granularity = 'week'

    classification_type = get_classifier(classifier)
    title = classification_type.display_title

    time_period = request.GET.get('time_period')
    month, year = time_period.split('/')
    date_string = '01/' + month + '/' + year
    date_time = get_date(date_string, '%d/%m/%Y', selected)
    original_date_time = date_time
    time_title = date_time.strftime('%b') + ' ' + date_time.strftime("%Y")

    start_of_first_week = date_time + relativedelta(days=-date_time.weekday())
    last_day_of_month = date_time + relativedelta(months=1) + relativedelta(days=-1)
    end_of_last_week = last_day_of_month + relativedelta(days=6 - last_day_of_month.weekday())



    total_tweets = Day.objects \
        .filter(Q(date__gte=start_of_first_week) & Q(date__lt=end_of_last_week)) \
        .extra({'time_unit': "Extract(week from date)"}) \
        .values('time_unit') \
        .annotate(value=Sum('tweet_number'))

    tweet_tuples = []
    for entry in total_tweets:
        timestamp_year = int(year)
        timestamp_week = int(entry['time_unit'])
        if timestamp_week == 52 and int(month) == 1:
            timestamp_year -= 1
        tweet_tuples.append((datetime.strptime(str(timestamp_year) + '-W' + str(timestamp_week) + '-0', "%Y-W%W-%w"), entry['value']))

    tweet_tuples = sorted(tweet_tuples, key=lambda x: x[0])
    if tweet_tuples:
        date_time = tweet_tuples[0][0] + relativedelta(days=-6)
    tweet_timestamps = get_tweet_timestamps(tweet_tuples)

    ##Classifications

    classified_weeks = ClassifiedDay.objects \
        .filter(Q(classification_type=classification_type) & Q(date__gte=date_time) & Q(date__lte=tweet_tuples[len(tweet_tuples) - 1][0])
                & Q(classification_type__label__classification_value=F('classification_value'))) \
        .extra({'time_unit': "Extract(week from date)"}) \
        .values('time_unit', 'classification_value', 'classification_type__label__name', 'classification_type__label__color') \
        .annotate(value=Sum('amount_classified'))

    link_prefix = str(
        request.build_absolute_uri('/')[:-1]) + '/analysis/' \
                  + classifier + '/' + next_granularity + '?time_period='

    classifier_summary_classifications = {}
    classified_counts = {}
    classification_colors = {}
    classifications_exist = False
    while date_time <= end_of_last_week:
        week_classifications = get_classifications_by_unit_of_time(
            date_time.isocalendar()[1], classified_weeks)
        classifications = []
        for classification in week_classifications:
            classifications_exist = True
            if classification['classification_type__label__name'] in classifier_summary_classifications:
                classifier_summary_classifications[
                    classification['classification_type__label__name']] += classification[
                    'value']
                classified_counts[classification['classification_type__label__name']].append((date_time + relativedelta(days=6), classification['value']))
            else:
                classifier_summary_classifications[
                    classification['classification_type__label__name']] = classification[
                    'value']
                classified_counts[
                    classification['classification_type__label__name']] = [
                    (date_time + relativedelta(days=6),
                     classification['value'])]
                classification_colors[
                    classification['classification_type__label__name']] = \
                    classification['classification_type__label__color']

            classifications.append(
                {'label': classification['classification_type__label__name'],
                 'value': int(classification['value'])})

        new_week_string = date_time.strftime('%d/%m/%Y') \
                          + ' - ' + (date_time + relativedelta(days=6))\
                              .strftime('%d/%m/%Y')
        week = {
            'text': new_week_string,
            'classifications': classifications,
            'link': link_prefix + new_week_string.replace(" ", "")
        }
        row.append(week)
        date_time += relativedelta(days=7)
    rows.append(row)

    for entry in classified_counts:
        classified_counts[entry] = get_tweet_timestamps(classified_counts[entry])

    return render(request, 'core/classifier-analysis.html', {"nav_page": 'analysis',
                                                  "title": title,
                                                  "selected": selected,
                                                  "classifications_exist": classifications_exist,
                                                  "classification_counts": classified_counts,
                                                  "classification_colors": classification_colors,
                                                  "total_tweets": tweet_timestamps,
                                                  "classified_weeks": classified_weeks,
                                                  "item_rows": rows,
                                                  "classifier_summary": get_classifier_summary(
                                                      classifier_summary_classifications,
                                                      next_granularity, '"%d"'),
                                                  "top_tweet_parameters": get_top_tweet_parameters(int(classification_type.id), start_of_first_week, end_of_last_week),
                                                  "time_switcher": get_time_switcher_links(
                                                      request, time_title, classifier, original_date_time, selected)
                                                  })


def preview_data_day(request, classifier):
    selected = 'day'

    classification_type = get_classifier(classifier)
    title = classification_type.display_title

    day_string = request.GET.get('time_period')
    time_title = day_string
    date_time = get_date(day_string, '%d/%m/%Y', selected)

    total_tweets = \
        int(Day.objects.filter(
            date__exact=date_time.strftime('%Y-%m-%d')).values_list(
            'tweet_number', flat=True).count())

    classifications = ClassifiedDay.objects \
        .filter(Q(classification_type=classification_type) & Q(date__exact=date_time.strftime('%Y-%m-%d'))
                & Q(classification_type__label__classification_value=F('classification_value'))) \
        .extra(select={'time_unit': 'date'}) \
        .values('time_unit', 'classification_value', 'classification_type__label__name', 'classification_type__label__color') \
        .annotate(value=Sum('amount_classified'))

    classifier_summary_classifications = {}
    classification_colors = {}
    classifications_exist = False
    for classification in classifications:
        classifications_exist = True
        if classification['classification_type__label__name'] in classifier_summary_classifications:
            classifier_summary_classifications[
                classification['classification_type__label__name']] += classification[
                'value']
        else:
            classifier_summary_classifications[
                classification['classification_type__label__name']] = classification[
                'value']
            classification_colors[
                classification['classification_type__label__name']] = \
                classification['classification_type__label__color']

    return render(request, 'core/classifier-analysis.html', {"nav_page": 'analysis',
                                                  "title": title,
                                                  "selected": selected,
                                                  "classifications_exist": classifications_exist,
                                                  "classification_colors": classification_colors,
                                                  "classifier_summary": get_classifier_summary(
                                                      classifier_summary_classifications,
                                                      None, None),
                                                  "top_tweet_parameters": get_top_tweet_parameters(int(classification_type.id), date_time, (date_time + relativedelta(days=1))),
                                                  "total_tweets_text": total_tweets,
                                                  "item_rows": [],
                                                  "time_switcher": get_time_switcher_links(
                                                      request, time_title,
                                                      classifier, date_time,
                                                      selected)
                                                  })


def preview_data_week(request, classifier):
    rows = []
    row = []
    selected = 'week'
    next_granularity = 'day'

    classification_type = get_classifier(classifier)
    title = classification_type.display_title

    time_period = request.GET.get('time_period')
    time_title = time_period
    start_date_string, end_date_string = time_period.split('-')
    start_time = get_date(start_date_string, '%d/%m/%Y', 'day')
    end_time = get_date(end_date_string, '%d/%m/%Y', selected)

    if end_time != start_time + relativedelta(days=6):
        raise Http404

    total_tweets = Day.objects \
        .filter(Q(date__gte=start_time.strftime('%Y-%m-%d')) & Q(
        date__lte=end_time.strftime('%Y-%m-%d'))) \
        .values_list('date', 'tweet_number') \
        .order_by('date')

    tweet_timestamps = get_tweet_timestamps(total_tweets)

    ##Classifications

    classified_days = ClassifiedDay.objects \
        .filter(Q(classification_type=classification_type) &
                Q(date__gte=start_time.strftime('%Y-%m-%d')) &
                Q(date__lte=end_time.strftime('%Y-%m-%d')) &
                Q(classification_type__label__classification_value=F('classification_value'))) \
        .extra({'time_unit': "Extract(day from date)"}, ) \
        .values('time_unit', 'classification_value', 'classification_type__label__name', 'classification_type__label__color') \
        .annotate(value=Sum('amount_classified'))

    link_prefix = str(
        request.build_absolute_uri('/')[:-1]) + '/analysis/' \
                  + classifier + '/' + next_granularity + '?time_period='

    current = start_time
    classifier_summary_classifications = {}
    classified_counts = {}
    classification_colors = {}
    classifications_exist = False
    for i in range(0, 7):
        day_classifications = get_classifications_by_unit_of_time(
            current.day, classified_days)
        classifications = []
        for classification in day_classifications:
            classifications_exist = True
            if classification['classification_type__label__name'] in classifier_summary_classifications:
                classifier_summary_classifications[
                    classification['classification_type__label__name']] += classification[
                    'value']
                classified_counts[classification['classification_type__label__name']].append((current, classification['value']))

            else:
                classifier_summary_classifications[
                    classification['classification_type__label__name']] = classification[
                    'value']
                classified_counts[
                    classification['classification_type__label__name']] = [
                    (current, classification['value'])]
                classification_colors[classification['classification_type__label__name']] = classification['classification_type__label__color']

            classifications.append(
                {'label': classification['classification_type__label__name'],
                 'value': int(classification['value'])})

        new_day_string = current.strftime('%d/%m/%Y')
        day = {
            'text': new_day_string,
            'classifications': classifications,
            'link': link_prefix + new_day_string
        }
        row.append(day)
        current += relativedelta(days=1)
    rows.append(row)

    for entry in classified_counts:
        classified_counts[entry] = get_tweet_timestamps(classified_counts[entry])

    return render(request, 'core/classifier-analysis.html', {"nav_page": 'analysis',
                                                  "title": title,
                                                  "selected": selected,
                                                  "classifications_exist": classifications_exist,
                                                  "classification_counts": classified_counts,
                                                  "classification_colors": classification_colors,
                                                  "item_rows": rows,
                                                  "total_tweets": tweet_timestamps,
                                                  "classifier_summary":get_classifier_summary(classifier_summary_classifications, next_granularity, '"%d"'),
                                                  "top_tweet_parameters": get_top_tweet_parameters(int(classification_type.id), start_time, end_time),
                                                  "classified_days": classified_days,
                                                  "time_switcher": get_time_switcher_links(
                                                      request, time_title, classifier, start_time, selected)
                                                  })


def validate_date(date_time, time_unit_type):
    if ((time_unit_type == 'day' and (date_time >= datetime.today()
                                    or date_time <= date_time.strptime(
                '22/06/2016', '%d/%m/%Y')))
            | (time_unit_type == 'week' and (
                    date_time >= datetime.today() + relativedelta(days=6)
                    or date_time < date_time.strptime('23/06/2016',
                                                       '%d/%m/%Y')))
            | (time_unit_type == 'month' and (date_time >= datetime.today()
                                           or date_time < date_time.strptime(
                        '01/06/2016', '%d/%m/%Y')))
            | (time_unit_type == 'year' and (date_time >= datetime.today()
                                          or date_time <  date_time.strptime(
                        '01/01/2016', '%d/%m/%Y')))):
        raise Http404


def get_date(time_period, format, time_unit_type):
    try:
        date_time = datetime.strptime(time_period, format)
        validate_date(date_time, time_unit_type)
    except Exception:
        raise Http404

    return date_time


def get_classifier(classifier):
    try:
        classifier = ClassificationType.objects.get(name__exact=classifier)
    except Exception:
        raise Http404

    return classifier


def get_tweet_timestamps(total_tweets):
    tweet_timestamps = []
    for (date, tweet_number) in total_tweets:
        timestamp = {}
        timestamp['date'] = date.strftime('%d/%m/%Y')
        timestamp['tweet_number'] = int(tweet_number)
        tweet_timestamps.append(timestamp)
    tweet_timestamps = json.dumps(tweet_timestamps)
    return tweet_timestamps


def get_time_switcher_links(request, title, classifier, selected_time_unit, selected_time_unit_type):
    current_date = datetime.today()

    week_start = current_date + relativedelta(days=-current_date.weekday())
    week_end = week_start + relativedelta(days=6)

    next_time_period, prev_time_period = get_time_switcher_buttons(
        selected_time_unit, selected_time_unit_type, current_date)


    link_prefix = str(
        request.build_absolute_uri('/')[:-1]) + '/analysis/' + classifier

    return {
        "title": title,
        "day": link_prefix + '/day?time_period='
               + current_date.strftime("%d/%m/%Y"),
        "week": link_prefix + '/week?time_period='
                + week_start.strftime("%d/%m/%Y") + '-'
                + week_end.strftime("%d/%m/%Y"),
        "month": link_prefix + '/month?time_period='
                 + current_date.strftime("%m/%Y"),
        "year": link_prefix + '/year?time_period='
                + current_date.strftime("%Y"),
        "next_time_period": next_time_period,
        "prev_time_period": prev_time_period,
    }


def get_time_switcher_buttons(selected_time_unit, selected_time_unit_type,
                              current_date):
    if selected_time_unit_type == 'year':
        prev_date_time = selected_time_unit + relativedelta(years=-1)
        prev_time_period = prev_date_time.strftime("%Y")

        next_date_time = selected_time_unit + relativedelta(years=1)
        next_time_period = next_date_time.strftime("%Y")
    elif selected_time_unit_type == 'month':
        prev_date_time = selected_time_unit + relativedelta(months=-1)
        prev_time_period = prev_date_time.strftime("%m/%Y")

        next_date_time = selected_time_unit + relativedelta(months=1)
        next_time_period = next_date_time.strftime("%m/%Y")
    elif selected_time_unit_type == 'week':
        prev_date_time = selected_time_unit + relativedelta(weeks=-1)
        prev_time_period = prev_date_time.strftime("%d/%m/%Y") + '-' \
                           + (prev_date_time + relativedelta(days=6)).strftime(
            "%d/%m/%Y")

        next_date_time = selected_time_unit + relativedelta(weeks=1)
        next_time_period = next_date_time.strftime("%d/%m/%Y") + '-' \
                           + (next_date_time + relativedelta(days=6)).strftime(
            "%d/%m/%Y")
    else:
        prev_date_time = selected_time_unit + relativedelta(days=-1)
        prev_time_period = prev_date_time.strftime("%d/%m/%Y")

        next_date_time = selected_time_unit + relativedelta(days=1)
        next_time_period = next_date_time.strftime("%d/%m/%Y")

    if (((selected_time_unit_type == 'day') & (selected_time_unit.strftime(
            '%d/%m/%Y') == current_date.strftime('%d/%m/%Y'))) |
            ((selected_time_unit_type == 'week') & (
                    (selected_time_unit.isocalendar()[1] ==
                     current_date.isocalendar()[1]) & (
                            selected_time_unit.year == current_date.year))) |
            ((selected_time_unit_type == 'month') & (
                    selected_time_unit.strftime(
                        '%m/%Y') == current_date.strftime('%m/%Y'))) |
            ((selected_time_unit_type == 'year') & (
                    selected_time_unit.year == current_date.year))):
        next_time_period = None

    if (((selected_time_unit_type == 'day') & (selected_time_unit.strftime(
            '%d/%m/%Y') == '23/06/2016')) |
            ((selected_time_unit_type == 'week') & (
                    selected_time_unit.strftime(
                        '%d/%m/%Y') == '22/06/2016')) |
            ((selected_time_unit_type == 'month') & (
                    selected_time_unit.strftime(
                        '%m/%Y') == '06/2016')) |
            ((selected_time_unit_type == 'year') &
             (selected_time_unit.year == 2016))):
        prev_time_period = None

    return next_time_period, prev_time_period


def get_classifier_summary(classifier_summary_classifications,
                           summary_granularity, tick_granularity):
    classifications = []

    for summary_classification in classifier_summary_classifications:
        classification = {
            "label": summary_classification, "value": int(
                classifier_summary_classifications[summary_classification])
        }
        classifications.append(classification)

    classifier_summary = {
        "granularity": summary_granularity,
        "tick_granularity": tick_granularity,
        "table_labels": ["classification", "amount"],
        "classifications": classifications
    }

    return classifier_summary


def analysis(request):
    rows = []
    row = []

    classifiers = ClassificationType.objects.all().order_by('display_title')

    current_date = datetime.today().now().strftime('%d/%m/%Y')

    for classifier in classifiers:
        classifier_display = {
            "name": classifier.name,
            "title": classifier.display_title,
            "text": classifier.display_text
        }
        row.append(classifier_display)
        if len(row) == 2:
            rows.append(row)
            row = []

    if len(row) > 0:
        rows.append(row)


    return render(request, 'core/analysis.html', {"nav_page": "analysis",
                                                  "current_date": current_date,
                                                  "rows": rows})


def get_classifications_by_unit_of_time(time_unit, classification_list):
    classifications = []
    for classification in classification_list:
        if classification['time_unit'] == time_unit:
            classifications.append(classification)
    return classifications

def get_top_classified_tweets_table(classification_type_id, start_date, end_date):
    classifier_classification_values = \
        ClassificationType.objects.filter(id=classification_type_id).values_list('label__classification_value', flat=True)

    top_tweets = []
    for classification_value in classifier_classification_values:
        top_tweets.extend(ClassifiedTweet.objects
                          .filter(Q(classification_type_id=classification_type_id)
                                  & Q(classification_value=int(classification_value))
                                  & Q(tweet_id__date__gte=start_date)
                                  & Q(tweet_id__date__lte=end_date))
                          .values('tweet_id__text', 'classification_type__label__name')
                          .order_by('classification_probability')[:5])
    return top_tweets


def get_top_tweet_parameters(classification_type_id, start_date, end_date):

    return {
        'classification_type_id': classification_type_id,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }


def top_tweets(request):
    start_date = request.GET["start_date"]
    end_date = request.GET["end_date"]
    classification_type_id = int(request.GET["classification_type_id"])

    classifier_classification_values = \
        ClassificationType.objects.filter(
            id=classification_type_id).values_list(
            'label__classification_value', flat=True)

    top_tweets = []
    for classification_value in classifier_classification_values:
        tweets = ClassifiedTweet.objects.filter(
            Q(classification_probability__gte=0.99)
            & Q(classification_type_id=classification_type_id)
            & Q(classification_value=int(classification_value))
            & Q(tweet_id__date__gte=start_date)
            & Q(tweet_id__date__lte=end_date)
            & Q(classification_type__label__classification_value=int(classification_value))).values('tweet_id__text',
                                  'classification_type__label__name')[:5]
        top_tweets.extend(tweets)
    return JsonResponse(top_tweets, safe=False)




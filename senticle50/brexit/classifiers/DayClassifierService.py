from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.models.query import Q

from classifiers.ClassifiedDayTransformer import ClassifiedDayTransformer
from classifiers.models import ClassifiedTweet
from concurrency.SynchronizedList import SynchronizedList
from concurrency.ThreadPool import ThreadPool
from concurrency.Utils import Utils
from utils.DatabaseManager import DatabaseManager


class DayClassifierService:

    @staticmethod
    def process_day_classification(classified_days_list,
                                   day_classification,
                                   worker_loop):

        classified_day = ClassifiedDayTransformer.get_classified_day(
            day_classification['date'],
            day_classification['classification_type_id'],
            day_classification['classification_value'],
            day_classification['amount_classified']
        )

        if classified_day:
            classified_days_list.add(classified_day)

            classified_days_list.get_lock()
            if classified_days_list.get_size_thread_unsafe() >= 1000:
                print('Saving Classified Day...')
                worker_loop.call_soon_threadsafe(
                    DatabaseManager.update_items,
                    classified_days_list.get_list())
                # Clear list now it has been saved
                classified_days_list.clear()
            classified_days_list.release_lock()

    def classify_days(self, since, until):
        day_classifications = list(ClassifiedTweet.objects.filter(
            Q(tweet_id__date__gte=since) & Q(
                tweet_id__date__lte=until)).values('classification_type_id',
                                                   'classification_value').annotate(
            amount_classified=Count('classification_type_id')).annotate(
            date=TruncDate('tweet_id__date')))

        print('Got Tweets')

        worker_loop = Utils.get_worker_loop()
        pool = ThreadPool(3)
        day_classification_list = SynchronizedList()

        for day_classification in day_classifications:
            pool.add_task(self.process_day_classification,
                          day_classification_list, day_classification,
                          worker_loop)

        pool.wait_completion()

        # Save any unsaved tokenized tweets
        DatabaseManager.update_items(
            day_classification_list.get_list())

        # Exit program
        worker_loop.call_soon_threadsafe(worker_loop.stop)

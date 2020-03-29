from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.models.query import Q

from concurrency.SynchronizedList import SynchronizedList
from concurrency.ThreadPool import ThreadPool
from concurrency.Utils import Utils
from scraper.DayTransformer import DayTransformer
from scraper.models import Tweet
from utils.DatabaseManager import DatabaseManager


class EndOfDayService:

    @staticmethod
    def process_day(day_list,
                    days,
                    index,
                    worker_loop):

        day = DayTransformer.get_new_day(
            days[index]['day_date'],
            days[index]['tweet_number']
        )

        if day:
            day_list.add(day)

            day_list.get_lock()
            if day_list.get_size_thread_unsafe() >= 1000:
                print('Saving Classified Day...')
                worker_loop.call_soon_threadsafe(
                    DatabaseManager.update_items,
                    day_list.get_list())
                # Clear list now it has been saved
                day_list.clear()
            day_list.release_lock()

    def generate_days(self, since, until):
        end_of_day_values = \
            Tweet.objects.filter(Q(date__gte=since) & Q(date__lte=until)) \
                .annotate(day_date=TruncDate('date')).values('day_date') \
                .annotate(tweet_number=Count(TruncDate('date')))

        print(end_of_day_values)

        worker_loop = Utils.get_worker_loop()
        pool = ThreadPool(3)
        days = SynchronizedList()

        for i in range(0, end_of_day_values.count()):
            pool.add_task(self.process_day,
                          days, end_of_day_values, i,
                          worker_loop)

        pool.wait_completion()

        # Save any unsaved tokenized tweets
        DatabaseManager.update_items(
            days.get_list())

        # Exit program
        worker_loop.call_soon_threadsafe(worker_loop.stop)

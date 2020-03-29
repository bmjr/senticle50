from scraper.models import Day


class DayTransformer:
    """ A transformer class to transform given tweet parameters into
        a Day model object.
    """

    @staticmethod
    def get_new_day(date, tweet_number):
        """
        A method fetch a Day (model object) from a date and tweet_number

        Args:
            :param date: The date of the Day.
            :param tweet_number: The number of tweets for that Day.

        Returns:
            :return Day: the Day object for that given day.
            :return None: Where an identical Day object in
                    every attribute already exists.
        """

        try:
            day = Day.objects.get(date=date, tweet_number=tweet_number)

            # Check if Update Required
            if day.tweet_number == tweet_number:
                # Return None where identical Day object already exists
                return None
            else:
                day.tweet_number = tweet_number
                return day

        except Day.DoesNotExist:
            # Create Day where one doesn't exist.
            return Day(date=date, tweet_number=tweet_number)

    @staticmethod
    def get_day(date):
        """
        A method fetch a Day (model object) from a date

        Args:
            :param date: The date of the Day.

        Returns:
            :return Day: the Day object for that given day.
        """
        try:
            return Day.objects.get(date=date)
        except Day.DoesNotExist:
            # Create Day where one doesn't exist.
            return Day(date=date, tweet_number=0)

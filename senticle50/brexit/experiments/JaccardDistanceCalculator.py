import numpy
from django.db.models import Q
from scraper.models import Tweet
from scraper.managers.TweetManager import TweetManager

class JacquardsDistanceCalculator:
    @staticmethod
    def get_distance_matrix(seed_hashtags, gathered_hashtags, progress):
        """
        :return: Jacquards Distance Matrix
                 Size: Num[seed hashtags] x Num[gathered hashtags]
        hashtags]
        """

        seed_count = {}
        gathered_count = {}

        for hashtag in seed_hashtags:
            seed_count[hashtag] = \
                TweetManager.get_all_pre_negotiation_tweets().filter(
                text__icontains=hashtag).count()

        for hashtag in gathered_hashtags:
            gathered_count[hashtag] = TweetManager.get_all_pre_negotiation_tweets().filter(
                text__icontains=hashtag).count()

        distance_matrix = numpy.ones(shape=(len(gathered_hashtags),
                                            len(seed_hashtags)))

        for row, source in enumerate(gathered_hashtags):
            for column, destination in enumerate(seed_hashtags):
                intersection = TweetManager.get_all_pre_negotiation_tweets().filter(Q(
                    text__icontains=source) & Q(
                    text__icontains=destination)).count()
                distance_matrix[row][column] = JacquardsDistanceCalculator.get_jacquards_distance(
                    gathered_count[source], seed_count[destination], intersection)
            progress.update(1)

        return distance_matrix

    @staticmethod
    def get_jacquards_distance(a_size, b_size, intersection):
        union = (a_size + b_size) - intersection
        jacquard_coefficient = intersection / union
        jacquard_distance = 1 - jacquard_coefficient

        return jacquard_distance

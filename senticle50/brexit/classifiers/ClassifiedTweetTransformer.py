from classifiers.models import ClassifiedTweet


class ClassifiedTweetTransformer:

    @staticmethod
    def get_or_create_classified_tweet(id, classification_type,
                                       classification, is_training):
        # Get Model
        classification_value, classification_probability = classification
        try:
            existing_classified_tweet = ClassifiedTweet.objects.get(
                tweet_id__id=id, classification_type=classification_type,
                classification_value=classification_value)
            if existing_classified_tweet.classification_value == classification_value:
                return None
            else:
                # Extremely unlikely to happen but:
                #   handle the case of the model predicting a training tweet
                #   a different value than it's existing value
                if existing_classified_tweet.is_training_set and not is_training:
                    return None

                new_classified_tweet = existing_classified_tweet
                new_classified_tweet.classification_value = classification_value
                new_classified_tweet.classification_probability = classification_probability
                return new_classified_tweet
        except ClassifiedTweet.DoesNotExist:
            return ClassifiedTweet(tweet_id_id=id,
                                   classification_type=classification_type,
                                   classification_value=classification_value,
                                   classification_probability=classification_probability,
                                   is_training_set=is_training)

    @staticmethod
    def create_classified_tweet(id, classification_type,
                                classification, is_training):
        # Get Model
        classification_value, classification_probability = classification
        return ClassifiedTweet(tweet_id_id=id,
                               classification_type=classification_type,
                               classification_value=classification_value,
                               classification_probability=classification_probability,
                               is_training_set=is_training)

    @staticmethod
    def get_classified_tweet(id, classification_type,
                             classification, is_training, overwrite_mode):
        if overwrite_mode:
            return ClassifiedTweetTransformer.get_or_create_classified_tweet(
                id, classification_type,
                classification, is_training)

        return ClassifiedTweetTransformer.create_classified_tweet(id,
                                                                  classification_type,
                                                                  classification,
                                                                  is_training)

#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import string

from nltk import tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from django.apps import apps


class TokenizedTweetTransformer:
    """A transformer class used to convert given paramters into TokenizedTweet
       model objects.

       The TokenizedTweetTransformer as part of the system design ignores all
       tweets containing pic.twitter.com as tweets of pictorial type are less
       fruitful in textual content and thus harder to classify correctly.
    """

    @staticmethod
    def get_tokenized_tweet(id, text):
        """
        A method that transforms a given tweet id and text to a TokenizedTweet
        model object

        Args:
        :param id: The id of the tweet
        :param text: The text of the tweet

        Returns:
        :return TokenizedTweet: a TokenizedTweet object.
        :return None: Where the tweet is incompatible for classifying
                      i.e. the tweet contains a picture of a malformed URL

        """

        is_incompatible_img_tweet = re.findall(r"pic.twitter.com", text)
        if is_incompatible_img_tweet:
            return None

        # Make all text lower case
        text = text.lower()

        # Replace Mention @([a-zA-Z0-9_])*
        text = re.sub(r"@([a-zA-Z0-9_])*", " ", text)

        # Replace Hashtags #([a-zA-Z0-9_])*
        text = re.sub(r"#([a-zA-Z0-9_])*", " ", text)

        # Remove Retweet Symbol
        text = re.sub(r"rt", " ", text)

        # Remove extra whitespace
        text = re.sub(' +', ' ', text)

        # Replace URL of type http://example.com ... and http://example.com
        text = re.sub(
            r"(https?://([a-zA-Z0-9:%_+#=~@. /\\])*(( \…( |$))|(\…( |$))|( |$)))",
            " ",
            text)

        # Check if the tweet contains a malformed URL
        is_incompatible_http_tweet = re.findall(r"https?", text)
        if is_incompatible_http_tweet:
            return None

        # Replace speech marks
        text = re.sub(r'"', " ", text)

        # Create tokens from text
        tokens = tokenize.word_tokenize(text)

        # Remove punctuation
        # N.B. this should replace plain text emotions e.g. :)
        tokens = [char for char in tokens if char not in string.punctuation]

        # Remove stop words
        tokens = [word for word in tokens if not word in set(stopwords.words('english'))]

        # Stem words
        tokens = [PorterStemmer().stem(token) for token in tokens]

        # Rejoin tokens into token string
        tokens = " ".join(tokens)

        return apps.get_model('tokenizer','TokenizedTweet')(id, tokens)

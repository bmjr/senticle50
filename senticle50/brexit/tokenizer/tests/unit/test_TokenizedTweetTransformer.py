from django.test import TestCase

from scraper.models import Tweet
from tokenizer.TokenizedTweetTransformer import TokenizedTweetTransformer
from tokenizer.models import TokenizedTweet


class TestTokenizedTweetTransformerMethods(TestCase):
    serialized_rollback = True

    def test_get_tokenized_tweet_returns_none_for_img_tweet(self):
        tweet_containing_image_url = Tweet.objects.create(id=1,
                                                    text='tweet containing '
                                                         'an image '
                                                         'pic.twitter.com/img')

        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_image_url.id, tweet_containing_image_url.text)

        self.assertIsNone(actual_output)

    def test_get_tokenized_tweet_removes_url_for_url_without_expanded_extension(self):
        tweet_containing_url = Tweet.objects.create(id=1,
                                                    text='url '
                                                         'http://example.com')

        expected_output = TokenizedTweet(id=tweet_containing_url,
                                         tokens='url')

        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_url.id, tweet_containing_url.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_url_at_string_end_without_expanded_extension(self):
        tweet_containing_url = Tweet.objects.create(id=1,
                                                    text='url '
                                                         'http://example.com')
        expected_output = TokenizedTweet(id=tweet_containing_url,
                                         tokens='url')

        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_url.id, tweet_containing_url.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_speech_marks(self):
        tweet_containing_speech_marks = Tweet.objects.create(id=1,
                                                    text='"quot"')
        expected_output = TokenizedTweet(id=tweet_containing_speech_marks,
                                         tokens='quot')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_speech_marks.id, tweet_containing_speech_marks.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)


    def test_get_tokenized_tweet_removes_url_with_expanded_extension(self):
        tweet_containing_url = Tweet.objects.create(id=1,
                                                    text='url '
                                                         'http://example.com … ')
        expected_output = TokenizedTweet(id=tweet_containing_url,
                                         tokens='url')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_url.id, tweet_containing_url.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_url_with_expanded_extension_at_string_end(self):
        tweet_containing_url = Tweet.objects.create(id=1,
                                                    text='url '
                                                         'http://example.com …')
        expected_output = TokenizedTweet(id=tweet_containing_url,
                                         tokens='url')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_url.id, tweet_containing_url.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_url_with_expanded_extension_at_string_end_with_space(self):
        tweet_containing_url = Tweet.objects.create(id=1,
                                                    text='url'
                                                         'http://example.com … ')
        expected_output = TokenizedTweet(id=tweet_containing_url,
                                         tokens='url')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_url.id, tweet_containing_url.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_url_with_expanded_extension_no_space(self):
        tweet_containing_url = Tweet.objects.create(id=1,
                                                    text='url'
                                                         'http://example.com… '
                                                         'gone')
        expected_output = TokenizedTweet(id=tweet_containing_url,
                                         tokens='url gone')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_url.id, tweet_containing_url.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_mention(self):
        tweet_containing_mention = Tweet.objects.create(id=2,
                                                        text='mention @Example gone')
        expected_output = TokenizedTweet(id=tweet_containing_mention,
                                         tokens='mention gone')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_mention.id, tweet_containing_mention.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)


    def test_get_tokenized_tweet_removes_retweet(self):
        tweet_containing_mention = Tweet.objects.create(id=2,
                                                        text='RT tweet')
        expected_output = TokenizedTweet(id=tweet_containing_mention,
                                         tokens='tweet')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_mention.id, tweet_containing_mention.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_double_whitespace(self):
        tweet_containing_double_whitespace = Tweet.objects.create(id=2,
                                                                  text='two white space  gone')
        expected_output = TokenizedTweet(id=tweet_containing_double_whitespace,
                                         tokens='two white space gone')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_double_whitespace.id, tweet_containing_double_whitespace.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_removes_extra_whitespace(self):
        tweet_containing_extra_whitespace = Tweet.objects.create(id=2,
                                                                  text='extra white space   gone')
        expected_output = TokenizedTweet(id=tweet_containing_extra_whitespace,
                                         tokens='extra white space gone')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_extra_whitespace.id, tweet_containing_extra_whitespace.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_lowers_all_text(self):
        tweet_containing_all_caps = Tweet.objects.create(id=2,
                                                                  text='TWEET CAP')
        expected_output = TokenizedTweet(id=tweet_containing_all_caps,
                                         tokens='tweet cap')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_all_caps.id, tweet_containing_all_caps.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_lowers_some_text(self):
        tweet_containing_some_caps = Tweet.objects.create(id=2,
                                                                  text='TwEet cap')
        expected_output = TokenizedTweet(id=tweet_containing_some_caps,
                                         tokens='tweet cap')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_some_caps.id, tweet_containing_some_caps.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)


    def test_get_tokenized_tweet_stems_contraction_into_parts(self):
        tweet_containing_contraction = Tweet.objects.create(id=2,
                                                                  text="can't")
        expected_output = TokenizedTweet(id=tweet_containing_contraction,
                                         tokens="ca n't")
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_contraction.id, tweet_containing_contraction.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_stems_single_plural(self):
        tweet_containing_single_plural = Tweet.objects.create(id=2,
                                                                  text='tweet containing one plural')
        expected_output = TokenizedTweet(id=tweet_containing_single_plural,
                                         tokens='tweet contain one plural')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_single_plural.id, tweet_containing_single_plural.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

    def test_get_tokenized_tweet_stems_multiple_plural(self):
        tweet_containing_multiple_plurals = Tweet.objects.create(id=2,
                                                                  text='tweet containing plurals')
        expected_output = TokenizedTweet(id=tweet_containing_multiple_plurals,
                                         tokens='tweet contain plural')
        actual_output = TokenizedTweetTransformer.get_tokenized_tweet(
            tweet_containing_multiple_plurals.id, tweet_containing_multiple_plurals.text)

        self.assertIsNotNone(actual_output)
        self.assertIs(type(actual_output), TokenizedTweet)
        self.assertEqual(actual_output.id, expected_output.id)
        self.assertEqual(actual_output.tokens, expected_output.tokens)

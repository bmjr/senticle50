# Classifier Component Design Rationale

## Classifier Component

The classifier component will be used to classify tweet data against a number of different proposed classifications. The classifier results will then be stored into the database.


## Brexit Stance Classifier Design

### Overview

This classifier will be used to affirm a tweet's stance on Brexit.

Given a tweet categorise it as regarding:

* REMAIN
* LEAVE
* NEITHER

Using a neural network with various layers (to yet be confirmed) a set of training tweets will be given to it for the formation of the model. The tweets will be labelled using a tailored distant supervision technique of automatic labelling. After the model is formed the neural network will be used to classify the remaining tweets.

### Brexit Stance Automatic Labelling

The tweets will be gathered using a set of seed hashtags "#Brexit, #VoteLeave and #StrongerIn" which were three of the main hashtags used during the brexit campaign. The #VoteLeave and #StrongerIn hashtags will be used as the seed hashtags for the leave and remain stances respectively. For both of these hashtags, tweets containing these hashtags will be compared using **_Jaccards Coefficient_** to gather a list of commonly associated hashtags with each stance. After gathering a list of hashtags which co-occur with political stances; any hashtags which co-occur with both stances will be removed and a subset of high co-occuring hashtags will be selected for each of the stances. After gathering a non-bias set of hashtags for each brexit stance they will be used to automatically label tweets on which stance the tweet is most likely discussing (inclusive of some noise).

### Neural Network

****STRUCTURE TBD*** *

## Sentiment Classifier Design

### Overview

This classifier will be used to extract a tweet's sentiment orientation.

Given a tweet extract its sentiment polarity:

* POSITIVE
* NEGATIVE
* NEUTRAL

Using a neural network with various layers (to yet be confirmed) a set of training tweets will be given to it for the formation of the model. The tweets will be labelled using a tailored distant supervision technique of automatic labelling. The tweets will then be passed through Google's **_Word2vec/Doc2vec_** deep learning packages with the intention of converting them to a vector using the power of sentiment specic word embeddings (SSWE) which takes into consideration the context of the whole post by the user and not just the individual words that make up the post. The tweet SSWE vectors and corresponding polarity labels will then be fed into the Neural Network for training. After the model is formed the neural network will be used to classify the remaining tweets.

### Sentiment Polarity Automatic Labelling

Using a pre-established technique of automatic tweet sentiment labelling the classifier intends to use a set of "Positive" and "Negative" text-based emoticons as labels respective of the sentiment of the tweet.

### Neural Network

****STRUCTURE TBD*** *



# Scraper Component Design Rationale

## Scraper Component

The scraper component will be used to source the tweet data (and any other data needed) within the system. The scraper component will utilise API(s) to accomplish the gathering of data. Once gathered, the resulting data will be stored into the system database.


## Scraper Design Decisions

To consider the design of the scraper component we need to evaluate the it's utility in accomplishing System Requirements. It is therefore important to consider the scrapers design on the following requirements:

* The system must be able to access both real time and historical data.
* The system must be able to access large amounts of data
* The system must be able to easily manipulate data

## Tweet Scraping Design Decisions

The system's main data source is tweets of a brexit context and therefore the scraper needs to utilise an API which can retrieve this. As part of the design process for the scraper, numerous API's were evaluated against the aforementioned System Requirements 

### Twitter Search API (_Insufficient_) 

Description: The official twitter search API provides access to a variety of twitter entities. Twitter provides a tiered membership access to this API; standard, premium and enterprise with each  of these tiers gaining more access.

**Benefits**

* Access to a variety of twitter entities including user profiles, tweets etc.
* Access to a variety of metadata on twitter entities i.e. timezone data on a user

**Limitations**

* rate limitations on all endpoints, relatively low rates: ***X requests per 15 minutes***
* Free access is capped to only having access to the past 7 days of tweets
* Free access only gives what twitter coins a "sample" of the tweets this meaning that they do not give access to all tweets but instead "a subsection" which isn't advantageous in extracting overall public consensus
* Paid access gives access to twitter firehose (the full twitter database) however having to pay for access to this API to run the system is incompatible for a non-funded research project.

### Get-Old-Tweets API (_Chosen_)

Description: a simple web-scraper which directly scrapes the HTML of twitter's feed for a given query and parses the response.

**Benefits**

* No rate limiting and is therefore quicker to gather data
* Access to **all** tweets as twitter's feed contains all tweets for a given query
* Utilisation of twitter's feed also allows for usage of url query logic  i.e. limit tweets to English language only.

**Limitations**

* No access to certain metadata on tweets as data is sourced directly from HTML and not from twitter backend
* Could be unreliable as HTML parsing is dependent upon a static DOM, if twitter changes their front-end the API would need to be updated. 
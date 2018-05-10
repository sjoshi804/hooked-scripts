"""
Using Yelp Fuision API to find restaurants to approach (that haven't been approached before)
Save previously approached restaurants in the same directory as a txt file called restaurants
The restaurants to be targeted wil

This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
python hooked-find-restaurants.py
Univeristy: UCLA

if it finds restaurants that do not conflict then it will print out:
'Businesses found and printed to target_restaurants.txt file'
"""
from __future__ import print_function
import argparse
import json
import pprint
import requests
import sys
import urllib

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode



# Private API Key
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= "lCtVCa_2d0_g6gAHXXqHsPf0xpTFn5CKHfW1vXzW_HZ82T-FG1fP6WMuUUGLkom-__Rqi1d5L46QdwOJEFMcYGTx-be9YzNaD99Pio_gqPTgwz28ITNsVwP-bEKeWnYx"


# API constants
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
FACEBOOK_API_BASE_CALL = 'http:// https://graph.facebook.com/'

# Defaults for search
DEFAULT_TERM = 'restaurants'
UNIVERSITY = 'San Francisco, CA'
RADIUS_SIZE = 5000
SEARCH_LIMIT = 100

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location, offset):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'offset': offset,
        'location': location.replace(' ', '+'),
        'radius': RADIUS_SIZE,
        'limit': 50
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def query_api(term, location, RESTRICTED):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(API_KEY, term, location, 0)
    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return
    numFound = 0
    while len(businesses) >= 50 + numFound:
        numFound += 50
        response = search(API_KEY, term, location, numFound)
        more_businesses = response.get('businesses')
        if more_businesses is not None:
            businesses.extend(more_businesses)

    names = []
    contacts = []
    addresses = []
    urls = []
    categories = []
    #Create a list from the names
    #Cross reference with restricted and delete elements that are matching
    for i in range(0, len(businesses)):
        not_matched = True
        for j in range (0, len(RESTRICTED)):
            if(businesses[i]['name'] == RESTRICTED[j].strip('\n')):
                not_matched = False
        if(not_matched):
                names.append(businesses[i]['name'])
                contacts.append(businesses[i]['display_phone'])
                addresses.append(businesses[i]['location']['address1'])
                categories.append(businesses[i]['categories'][0]['title'])
                urls.append(businesses[i]['url'])
    list_restaurants = open('target_restaurants.txt', 'w')
    for x in range(0, len(names)):
        try:
            list_restaurants.write("%s\t" % names[x])
            list_restaurants.write("%s\t" % contacts[x])
            list_restaurants.write("%s\t" % addresses[x])
            list_restaurants.write("%s\t" % categories[x])
            list_restaurants.write("%s\n" % urls[x])

        except UnicodeEncodeError:
            continue

    print("Businesses found and printed to target_restaurants.txt file")

def main():
    # Takes in User Input
    UNIVERSITY = input("University: ")
    #Reads list of restaurants not to be included in target from restaurants.txt into a list restricted_text
    restricted_text = open('restricted.txt', 'r')
    RESTRICTED = restricted_text.readlines()
    restricted_text.close()

    try:
        query_api(DEFAULT_TERM, UNIVERSITY, RESTRICTED)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

    input("Press Enter to continue...")


if __name__ == '__main__':
    main()

import requests

def global_timeline():
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/global_timeline')

    return api_response.text

def latest():
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/latest')

    return api_response.text

def locations():
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/locations?timelines=true&country_code=US')

    return api_response.text

# TODO: Invalid country codes just return empty data structures. Some checking for this should be done somewhere.

def timeline(country_code):
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/timeline/{}'.format(country_code))

    return api_response.text

def total(country_code):
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/total/{}'.format(country_code))

    return api_response.text
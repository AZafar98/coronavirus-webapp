import requests

'https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/total/US'

def global_timeline():
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/global_timeline')

    return api_response.text

def latest():
    api_response = requests.get('https://api.xapix.dev/coronavirus-data/covid-19-api-repository/v2/latest')

    return api_response.text

def locations():
    api_response = requests.get()
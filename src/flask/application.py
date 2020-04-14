from flask import Flask, render_template
from flask_caching import Cache
from src.main.process_corona_data import display_covid_cases, covid_time_series, country_options
from src.main.get_phe_data import get_phe_data_for_flask
import sys
from time import time

# This is purely for PythonAnywhere - not necessary if running locally
project_home = '/home/Azafar98/coronavirus-webapp'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from src.flask.settings import RUNNING_LOCALLY

# Create an 'application' callable
application = Flask(__name__)

if RUNNING_LOCALLY:
    config = {
        "DEBUG": True,
        "CACHE_TYPE": 'filesystem',
        "CACHE_DIR": '../../cache/',
        "CACHE_DEFAULT_TIMEOUT": 300
    }
else:
    config = {
        "DEBUG": False,
        "CACHE_TYPE": 'filesystem',
        "CACHE_DIR": 'coronavirus-webapp/cache',
        "CACHE_DEFAULT_TIMEOUT": 300
    }

application.config.from_mapping(config)
cache = Cache(application)

"""
# NOTE: With the current setup, if PHE data does not exist. It will be downloaded when the page is first loaded.
# So, the first time you try to view the page, it will be notably slower.
# All subsequent refreshes will be fast as it will use the same data which will be saved locally as JSON.
# This *should* only apply when running the app on your local machine
"""

# This lets us call the function through the Jinja2 template engine.
# Thanks to https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2
application.jinja_env.globals.update(displayCovidCases=display_covid_cases)
application.jinja_env.globals.update(getPHEData=get_phe_data_for_flask)
application.jinja_env.globals.update(getCovidTimeSeries=covid_time_series)
application.jinja_env.globals.update(countryOptions=country_options)


@cache.cached(timeout=300)
def index():
    return render_template('index.html')


@cache.cached(timeout=300)
def about():
    return render_template('about.html')


@cache.cached(timeout=300)
def donate():
    return render_template('donate.html')


application.add_url_rule('/', 'index', index)
application.add_url_rule('/about', 'about', about)
application.add_url_rule('/donate', 'donate', donate)

# Run the app. This if block is only entered when running on local machine, so application.debug = True *should* be fine
# to be left here...
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(threaded=True)

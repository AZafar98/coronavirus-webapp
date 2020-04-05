from flask import Flask, render_template
from src.main.process_corona_data import display_covid_cases
from src.main.get_phe_data import get_phe_data_for_flask

# Create an 'application' callable
application = Flask(__name__)

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


def index():
    return render_template('index.html')


def about():
    return render_template('about.html')

def donate():
    return render_template('donate.html')


application.add_url_rule('/', 'index', index)
application.add_url_rule('/about', 'about', about)
application.add_url_rule('/donate', 'donate', donate)

# Run the app. This if block is only entered when running on local machine, so application.debug = True *should* be fine
# to be left here..
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

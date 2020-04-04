from flask import Flask, render_template
from src.main.process_corona_data import display_covid_cases
from src.main.get_phe_data import get_heart_data, get_depression_data, get_domestic_abuse_data

# Create an 'application' callable
application = Flask(__name__)

# NOTE: With the current setup, if PHE data does not exist. It will be downloaded when the page is first loaded.
# So, the first time you try to view the page, it will be notably slower.
# All subsequent refreshes will be fast as it will use the same data which will be saved locally as JSON.
# This *should* only apply when running the app on your local machine


def index():
    # There's probably a better way than passing down a load of similar function calls, but it works for now...
    return render_template('index.html', total_cases=display_covid_cases(cases=True, period='Total'),
                           total_cases_dates=str(display_covid_cases(cases=False, period='Total')),
                           cases_24h=display_covid_cases(cases=True, period='24h'),
                           cases_24h_dates=display_covid_cases(cases=False, period='24h'),
                           cases_7days=display_covid_cases(cases=True, period='7days'),
                           cases_7days_dates=display_covid_cases(cases=False, period='7days'),
                           heart_data=get_heart_data(),
                           depression_data=get_depression_data(),
                           domestic_abuse=get_domestic_abuse_data())


application.add_url_rule('/', 'index', index)

# Run the app. This if block is only entered when running on local machine, so application.debug = True *should* be fine
# to be left here
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

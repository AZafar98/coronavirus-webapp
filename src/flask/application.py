from flask import Flask, render_template
from src.main.process_corona_data import display_covid_cases
from src.main.get_phe_data import get_heart_data

footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default
application = Flask(__name__)

def index():
    # There's probably a better way than passing down a load of similar function calls, but it works for now...
    return render_template('index.html', total_cases = display_covid_cases(cases=True, period='Total'),
                           total_cases_dates = str(display_covid_cases(cases=False, period='Total')),
                           cases_24h = display_covid_cases(cases=True, period='24h'),
                           cases_24h_dates = display_covid_cases(cases=False, period='24h'),
                           cases_7days = display_covid_cases(cases=True, period='7days'),
                           cases_7days_dates = display_covid_cases(cases=False, period='7days'),
                           heart_data = get_heart_data())

application.add_url_rule('/', 'index', index)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
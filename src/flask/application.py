from flask import Flask, render_template
from src.main.process_corona_data import get_cases_from_json
from src.main.get_phe_data import get_heart_data

footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default
application = Flask(__name__)


def index():
    return render_template('index.html', latest_data=get_cases_from_json(),
                           heart_data=get_heart_data())

application.add_url_rule('/', 'index', index)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
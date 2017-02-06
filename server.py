import os
import flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar_lineprofilerpanel.profile import line_profile
import requests


# start flask app
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('secret_key', default='sillysecret')

# config debug tools
app_env = os.getenv('app_env', default='dev')
if 'dev' in app_env:
    app.debug = True
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
    app.config['DEBUG_TB_PANELS'] = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel'
    ]
    toolbar = DebugToolbarExtension(app)
elif 'prod' in app_env:
    app.debug = False
else:
    app.debug = True

API_URL = 'https://api.productvision.io/dev'
LIMIT = 18


@line_profile
def get_filter_prods(latest, category):

    if category != 'all':
        adj_limit = LIMIT * 3
    else:
        adj_limit = LIMIT

    resp = requests.get(headers={'x-api-key': 'demo-jackthreads-82A1'}, url=API_URL +
        '/products?account=demo-jackthreads&created_after={}&limit={}'.format(latest, str(adj_limit)))
    try:
        body_data = resp.json()
    except:
        body_data = {}

    products = body_data.get('products', [])
    next_latest = body_data.get('latest', 0)

    if category != 'all':
        products = [prod for prod in products if prod['meta']['cat_1'] == category]

    return products[0:int(LIMIT)], next_latest


@app.route('/')
@line_profile
def index():
    category = flask.request.args.get('category', 'all')
    flask.session['category'] = category
    products, latest = get_filter_prods(0, category)
    flask.session['latest'] = latest
    return flask.render_template('base.html', products=products)


@app.route('/scroll')
@line_profile
def scroll():
    category = flask.session['category']
    latest = flask.session['latest']
    products, new_latest = get_filter_prods(latest, category)
    flask.session['latest'] = new_latest
    return flask.render_template('partials/prod_card.html', products=products)


@app.route('/debug')
def debug():
    assert app.debug is False


@app.route('/random')
def random():
    import random
    import string
    return ''.join(random.choice(string.lowercase) for i in range(8))


if __name__ == '__main__':
    app.run()

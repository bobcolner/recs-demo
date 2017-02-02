import os
import flask
from flask_debugtoolbar import DebugToolbarExtension
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
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel'
    ]
    toolbar = DebugToolbarExtension(app)
elif 'prod' in app_env:
    app.debug = False
else:
    app.debug = True

api_url = 'https://api.productvision.io/v1'
limit = '24'


@app.route('/')
def index():
    category = flask.request.args.get('category', 'all')  # ['Clothing','Shoes','Accessories']
    flask.session['category'] = category
    resp = requests.get(api_url +
        '/products?account=demo-jackthreads&limit={}'.format(limit))
    products = resp.json()['products']
    if category != 'all':
        products = [prod for prod in products if prod['meta']['cat_1'] == category]
    flask.session['latest'] = resp.json()['latest']
    return flask.render_template('base.html', products=products)


@app.route('/scroll')
def scroll():
    latest = flask.session['latest']
    category = flask.session['category']
    resp = requests.get(api_url +
        '/products?account=demo-jackthreads&created_after={}&limit={}'.format(latest, limit))
    products = products = resp.json()['products']
    if category != 'all':
        products = [prod for prod in products if prod['meta']['cat_1'] == category]
    flask.session['latest'] = resp.json()['latest']
    return flask.render_template('partials/prod_card.html', products=products)


@app.route('/app_env')
def app_env():
    return app_env


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

import os
import simplejson as json
import flask
from flask_debugtoolbar import DebugToolbarExtension
import dynomodb_schema as ddb


# start flask app
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('secret_key', default='sillysecret')

# config debug tools
app_env = os.getenv('app_env', default='else')
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

DATA = []


@app.route('/')
def index(page=1):
    category = flask.request.args.get('category', None)  # 'Clothing'
    global DATA
    DATA = []
    with open('prod_recs.json') as json_data:
        DATA = json.load(json_data)
    if category:
        DATA = [d for d in DATA if d['cat_1'] == category]
    products = get_prods(page)
    return flask.render_template('base.html', products=products, page=page)


@app.route('/infiniscroll')
def infiniscroll(page=2):
    page = int(flask.request.args.get('page', page))
    products = get_prods(page)
    return flask.render_template('partials/prod_card.html', products=products, page=page)


def get_prods(page, size=12):
    first = page * size - size
    last = page * size
    clean_data = []
    for item in DATA[first:last]:
        clean_recs = []
        for rec in item['recs']:
            if rec['cat_2'] == item['cat_2'] and rec['distance'] < 70:
                clean_recs.append(rec)
        item['recs'] = clean_recs
        clean_data.append(item)
    return clean_data


@app.route('/get_recs/<pk>')  # e.g. b020c344c9534f8b557c
def get_recs(pk):
    rec = ddb.engine.get(ddb.ProdRecs, pkeys=[pk])
    return json.dumps(rec[0].ddb_dump_()['recs'])


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

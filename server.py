import os
import simplejson as json
from decimal import Decimal
import flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar_lineprofilerpanel.profile import line_profile
import boto3
from boto3.dynamodb.conditions import Key


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

# connect to dynamodb
# table = 'products-{}'.format('app_env')
TABLE = boto3.resource('dynamodb').Table('products-dev')
LIMIT = 18


@app.route('/')
@app.route('/<account_slug>')  # 'demo-jackthreads-82A1', 'demo-cedarmoss-888888', 'demo-untuckit-888888', 'demo-dwr', 'demo-crateandbarrel', 'demo-needsupplyco'
@line_profile
def index(account_slug='cedarmoss'):

    if account_slug == 'untuckit':
        account = 'demo-untuckit-888888'
        brand = 'UNTUCKit'
        color = 'blue darken-4'
    elif account_slug == 'jackthreads':
        account = 'demo-jackthreads-82A1'
        brand = 'JackThreads'
        color = 'red lighten-1'
    elif account_slug == 'cedarmoss':
        account = 'demo-cedermoss-888888'
        brand = 'Cedar & Moss'
        color = 'teal'
    elif account_slug == 'nsp':
        account = 'demo-needsupplyco'
        brand = 'Need Supply Co.'
        color = 'grey darken-4'
    elif account_slug == 'dwr':
        account = 'demo-dwr'
        brand = 'Design Within Reach'
        color = 'deep-orange darken-2'

    # category = flask.request.args.get('category', 'all')
    # flask.session['category'] = category

    response = TABLE.query(
        IndexName='created_at',
        KeyConditionExpression=Key('created_at').gt(0) & Key('account').eq(account),
        ProjectionExpression='product_id, img_url, created_at, meta, recs',
        Limit=LIMIT
    )

    flask.session['account'] = account
    flask.session['LastEvaluatedKey'] = json.dumps(response['LastEvaluatedKey'])

    products = response['Items']

    # if account == 'demo-dwr':
    #     products = filter_recs(products, key='cat_2')
    # if account == 'demo-untuckit-888888':
    #     products = filter_recs(products, key='category')

    if flask.request.args.get('output', 'html') == 'json':
        return json.dumps(products)
    else:
        return flask.render_template('base.html', brand=brand, color=color, products=products)


def filter_recs(products, key):
    filtered_prods = []
    for prod in products:
        filtered_recs = []
        for rec in prod['recs']:
            if key in rec and rec[key] == prod['meta'][key]:
                filtered_recs.append(rec)
                print(rec[key], prod['meta'][key])
        if len(filtered_recs) > 1:
            prod['recs'] = filtered_recs
            filtered_prods.append(prod)
    return filtered_prods


@app.route('/scroll')
@line_profile
def scroll():
    account = flask.session['account']
    # category = flask.session['category']
    LastEvaluatedKey = json.loads(flask.session['LastEvaluatedKey'])
    if 'created_at' in LastEvaluatedKey:
        LastEvaluatedKey['created_at'] = Decimal(LastEvaluatedKey['created_at'])
    response = TABLE.query(
        IndexName='created_at',
        KeyConditionExpression=Key('created_at').gt(0) & Key('account').eq(account),
        ProjectionExpression='product_id, img_url, created_at, meta, recs',
        Limit=LIMIT,
        ExclusiveStartKey=LastEvaluatedKey
    )
    products = response['Items']
    flask.session['LastEvaluatedKey'] = json.dumps(response['LastEvaluatedKey'])
    return flask.render_template('partials/prod_card.html', products=products)


def filter_prod(products):
    category = flask.session['category']
    if category != 'all':
        products = [prod for prod in products if prod['meta']['category'] == category]


if __name__ == '__main__':
    app.run()

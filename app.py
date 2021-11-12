import concurrent

from flask import Flask, request, render_template, make_response, redirect, url_for, Response
from flask_cors import cross_origin
from md.auction_txt import parse_bidders
from md.lindsay2018 import *
from md.auction_json import *
from md.auction_csv import *
import json
import uuid
from io import StringIO
from flask_executor import Executor

app = Flask(__name__, static_folder='web/static',
            static_url_path='',
            template_folder='web/templates')

app.config['EXECUTOR_MAX_WORKERS'] = 5
executor = Executor(app)

max_perms_to_consider = int(os.environ.get('MAX_PERMS_TO_CONSIDER', '1024'))

@app.route('/')
def index():
    return render_template('index.html')


def my_solve(problem, rule, form):
    auction = Auction()
    solution = auction.winner_determination(problem)
    rule.calc_surplus_shares(solution)
    return solution, form

# Pushes Server-Sent Events (SSE) to the browser about the status of a posted problem.
# Updates are sent every 20 seconds to keep the connection alive.
# 'Done' is sent when the problem has been solved.  See template 'wait.hml' for
# javascript that initiates a connection and processes the events.
@app.route('/listen')
def listen():
    uid = request.args.get("uid")

    def eventStream():
        yield 'data: {}\n\n'.format('Calculating..')
        result = None
        while result is None:
            try:
                result = executor.futures.result(uid, timeout=20)
                yield 'data: {}\n\n'.format('Done')
            except concurrent.futures._base.TimeoutError:
                yield 'data: {}\n\n'.format('Calculating...')

    return Response(eventStream(), mimetype="text/event-stream")


@app.route('/get-result')
def get_result():
    uid = request.args.get("uid")
    output_format = request.args.get("format")

    if not executor.futures._state(uid):
        return "No such element {}".format(uid)
    if not executor.futures.done(uid):
        return render_template('wait.html', uid=uid)
    future = executor.futures.pop(uid)
    solution, form = future.result()

    if output_format == 'txt':
        result = build_result(solution)
        return render_template('market.html', form=form, solution=result)
    elif output_format == 'csv':
        si = StringIO()
        encode_csv_solution(solution, si)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=results.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    elif output_format == 'json':
        json_str = json.dumps(solution, indent=4, cls=ObjectEncoder)
        output = make_response(json_str)
        output.headers["Content-Disposition"] = "attachment; filename=results.json"
        output.headers["Content-type"] = "text/json"
        return output
    else:
        return "Unknown format {}".format(output_format)


@app.route('/txt', methods=['POST', 'GET'])
def txt_bids():
    form = {'error': None,
            'bids': 'Seller: -10 1\nBuyer L: 22 -1\nBuyer H: 26 -1',
            'free_disposal': True,
            'pricing': 'lindsay2018'}
    result = None
    if request.method == 'POST':
        form['bids'] = request.form['bids']
        form['pricing'] = request.form['pricing']
        form['free_disposal'] = request.form.get('free_disposal')

        try:
            bidders = parse_bidders(form['bids'])
            rule = get_rule(form['pricing'], max_perms_to_consider=max_perms_to_consider)
            problem = Problem(bidders=bidders, free_disposal=form['free_disposal'])
            uid = uuid.uuid4().hex
            executor.submit_stored(uid, my_solve, problem, rule, form)
            return redirect(url_for('get_result', uid=uid, format='txt'))

        except ValueError as err:
            form['error'] = err

    return render_template('market.html', form=form, solution=result)


def build_result(solution):
    model = {'bidders': [],
             'surplus': solution.surplus,
             'rule': solution.rule,
             'sum_payments': 0}

    goods = solution.problem.goods
    for bidder in solution.problem.bidders:
        bids = []
        model['sum_payments'] += solution.payments.get(bidder.name, 0)
        for bid in bidder.bids:
            winning = bid.winning > 0
            bid_str = ''
            if bid.winning < 1 and winning:
                # Bid is partially winning.
                bid_str += str(bid.winning)
            bid_str += '['
            bid_str += str(bid.v)
            for good in goods:
                bid_str += ', '
                bid_str += str(bid.q.get(good, 0))
            bid_str += ']'

            bids.append({'quantities': bid_str, 'winning': winning})
            bidder_model = {'name': bidder.name, 'bids': bids}
            if bidder.name in solution.surplus_shares.keys():
                bidder_model['surplus_share'] = solution.surplus_shares[bidder.name]
                bidder_model['payment'] = solution.payments[bidder.name]
        model['bidders'].append(bidder_model)

    return model


@app.route("/solve/<rule_name>", methods=['POST'])
@cross_origin()
def solve_json(rule_name):
    dct = request.json
    problem = decode_problem(dct)
    auction = Auction()
    solution = auction.winner_determination(problem)
    rule = get_rule(rule_name)
    rule.calc_surplus_shares(solution)
    json_str = json.dumps(solution, indent=4, cls=ObjectEncoder)
    return json_str


@app.route('/upload/<file_format>', methods=['POST', 'GET'])
def upload_file(file_format):
    result = None
    form = {'error': None,
            'free_disposal': True,
            'format': file_format,
            'pricing': 'lindsay2018'}
    if request.method == 'POST':
        form['pricing'] = request.form['pricing']
        form['free_disposal'] = request.form.get('free_disposal')
        try:
            rule = get_rule(form['pricing'], max_perms_to_consider=max_perms_to_consider)
            f = request.files['fileupload']
            if file_format == 'csv':
                reader = file2reader(f)
                bidders = decode_csv_bidders(reader)
                problem = Problem(bidders=bidders,free_disposal=form['free_disposal'])
            elif file_format == 'json':
                dct = json.load(f)
                problem = decode_problem(dct)
            else:
                raise ValueError(file_format)

            uid = uuid.uuid4().hex
            executor.submit_stored(uid, my_solve, problem, rule, form)
            return redirect(url_for('get_result', uid=uid, format=file_format))
        except Exception as err:
            print(err)
            form['error'] = err
            result = None
    return render_template('upload.html', form=form, solution=result)

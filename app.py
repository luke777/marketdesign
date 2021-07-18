from flask import Flask, request, render_template, make_response
from flask_cors import cross_origin
from md.auction_txt import parse_bidders
from md.lindsay2018 import *
from md.auction_json import *
from md.auction_csv import *
import json
import csv
from io import StringIO

app = Flask(__name__, static_folder='web/static',
            static_url_path='',
            template_folder='web/templates')


@app.route('/')
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Market solver</title>
</head>
<body>
 <ul>
  <li><a href="txt">Form for .txt bids</a></li>
  <li><a href="upload">Upload .csv bids</a></li>
  <li><a href="jsonapi.html">Form for .json bids</a></li>
  <li><a href="catchment/example1.html">GUI demo</a></li>
</ul>
</body>
</html>"""

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
            rule = get_rule(form['pricing'])
            problem = Problem(bidders=bidders, free_disposal=form['free_disposal'])
            auction = Auction()
            solution = auction.winner_determination(problem)
            rule.calc_surplus_shares(solution)
            result = build_result(solution)
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
            bid_str = '['
            bid_str += str(bid.v)
            for good in goods:
                bid_str += ', '
                bid_str += str(bid.q.get(good, 0))
            bid_str += ']'
            winning = bid.winning > 0
            bids.append({'quantities': bid_str, 'winning': winning})
            print(bid_str)
            bidder_model = {'name': bidder.name, 'bids': bids}
            if bidder.name in solution.surplus_shares.keys():
                bidder_model['surplus_share'] = solution.surplus_shares[bidder.name]
                bidder_model['payment'] = solution.payments[bidder.name]
        model['bidders'].append(bidder_model)

    return model


@app.route("/solve/<rule_name>", methods=['POST'])
@cross_origin()
def solve(rule_name):
    dct = request.json
    problem = decode_problem(dct)
    auction = Auction()
    solution = auction.winner_determination(problem)
    rule = get_rule(rule_name)
    rule.calc_surplus_shares(solution)
    json_str = json.dumps(solution, indent=4, cls=ObjectEncoder)
    return json_str


@app.route('/upload', methods=['POST', 'GET'])
def upload_csv():
    result = None
    form = {'error': None,
            'free_disposal': True,
            'pricing': 'lindsay2018'}
    if request.method == 'POST':
        form['pricing'] = request.form['pricing']
        form['free_disposal'] = request.form.get('free_disposal')
        try:
            rule = get_rule(form['pricing'])
            f = request.files['fileupload']
            reader = file2reader(f)
            bidders = decode_csv_bidders(reader)
            problem = Problem(bidders=bidders)
            auction = Auction()
            solution = auction.winner_determination(problem)
            rule.calc_surplus_shares(solution)

            # return csv..
            si = StringIO()
            encode_csv_solution(solution, si)
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=results.csv"
            output.headers["Content-type"] = "text/csv"
            return output
        except Exception as err:
            print(err)
            form['error'] = err
            result = None
    return render_template('upload.html', form=form, solution=result)

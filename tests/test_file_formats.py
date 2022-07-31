import json
import unittest
from io import StringIO

from md.auction_json import decode_problem, ObjectEncoder
from md.auction_txt import encode_problem, parse_bidders
from md.lindsay2018 import *
from md.auction_csv import *
import pathlib
import csv


def load_all():
    files = list(pathlib.Path('../examples').glob('*.json'))
    problems = []
    for file in files:
        with open(file) as json_file:
            dct = json.load(json_file)
            problems.append(decode_problem(dct))

    return problems


# Read all json examples, the test writing and re-reading them in
# json, csv and txt.
class FormatsTestCase(unittest.TestCase):

    def test_json(self):
        a = Auction()
        problems = load_all()
        for problem in problems:
            expected_sol = a.winner_determination(problem)
            json_str = json.dumps(problem, indent=4, cls=ObjectEncoder)
            dct = json.loads(json_str)
            decoded_problem = decode_problem(dct)
            actual_sol = a.winner_determination(decoded_problem)
            self.assertEqual(expected_sol.surplus, actual_sol.surplus)

    def test_csv(self):
        a = Auction()
        problems = load_all()
        for problem in problems:
            expected_sol = a.winner_determination(problem)
            si = StringIO()
            encode_csv_problem(problem, si)
            reader = string2reader(si.getvalue())
            decoded_problem = decode_csv_problem(reader)
            actual_sol = a.winner_determination(decoded_problem)
            self.assertEqual(expected_sol.surplus, actual_sol.surplus)

    def test_txt(self):
        a = Auction()
        problems = load_all()
        for problem in problems:
            expected_sol = a.winner_determination(problem)
            s = encode_problem(problem)
            bidders = parse_bidders(s)
            decoded_problem = Problem(bidders=bidders)
            actual_sol = a.winner_determination(decoded_problem)
            self.assertEqual(expected_sol.surplus, actual_sol.surplus)

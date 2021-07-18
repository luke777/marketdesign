import unittest
from md.lindsay2018 import *
from md.auction_json import *
import json
import pathlib


def load_example(filename, rule=Lindsay2018()):
    with open(filename) as json_file:
        dct = json.load(json_file)
        problem = decode_problem(dct)
        auction = Auction()
        solution = auction.winner_determination(problem)
        rule.calc_surplus_shares(solution)
        return solution


class MyTestCase(unittest.TestCase):

    def test_all_case(self):
        files = list(pathlib.Path('../examples').glob('*.json'))
        for file in files:
            with open(file) as json_file:
                dct = json.load(json_file)
                problem = decode_problem(dct)
                auction = Auction()
                solution = auction.winner_determination(problem)
                self.assertTrue(solution.surplus >= 0)

    def test1(self):
        sol = load_example('../examples/Lindsay2018_t1_seller_and_2_buyers.json')
        self.assertEqual(2, len(sol.surplus_shares.keys()))
        self.assertEqual(14, sol.surplus_shares['seller'])
        self.assertEqual(2, sol.surplus_shares['buyer H'])

        self.assertEqual(1, sol.problem.bidders[0].bids[0].winning)
        self.assertEqual(0, sol.problem.bidders[1].bids[0].winning)
        self.assertEqual(1, sol.problem.bidders[2].bids[0].winning)

        self.assertEqual(['a'], sol.problem.goods)
        self.assertEqual('lindsay2018', sol.rule)

    def test2(self):
        sol = load_example('../examples/Lindsay2018_t2.1_two_demand_types.json')
        self.assertEqual(2, len(sol.surplus_shares.keys()))
        self.assertEqual(75, sol.surplus_shares['airline'])
        self.assertEqual(15, sol.surplus_shares['tourist'])
        self.assertEqual(['a', 'b'], sol.problem.goods)

    def test3(self):
        sol = load_example('../examples/Lindsay2018_t2.2_two_demand_types_large_market.json')
        self.assertEqual(5, len(sol.surplus_shares.keys()))
        self.assertEqual(86, sol.surplus_shares['airline 1'])
        self.assertEqual(86, sol.surplus_shares['airline 2'])
        self.assertEqual(16, sol.surplus_shares['co-authors 1'])
        self.assertEqual(16, sol.surplus_shares['co-authors 2'])

    def test4(self):
        sol = load_example('../examples/Lindsay2018_t2.3_avoidable_costs.json')
        self.assertEqual(3, len(sol.surplus_shares.keys()))
        self.assertEqual(15, sol.surplus_shares['small airline'])
        self.assertEqual(12.5, sol.surplus_shares['traveler 2'])
        self.assertEqual(17.5, sol.surplus_shares['traveler 3'])

    def test5(self):
        sol = load_example('../examples/Lindsay2018_t3.1_low_vcg_rev.json')
        self.assertEqual(3, len(sol.surplus_shares.keys()))
        self.assertEqual(8 / 3, sol.surplus_shares['airline'])
        self.assertEqual(2 / 3, sol.surplus_shares['single traveler 1'])
        self.assertEqual(2 / 3, sol.surplus_shares['single traveler 2'])

        sol = load_example('../examples/Lindsay2018_t3.1_low_vcg_rev.json', rule=VCG())
        self.assertEqual(3, len(sol.surplus_shares.keys()))
        self.assertEqual(4, sol.surplus_shares['airline'])
        self.assertEqual(2, sol.surplus_shares['single traveler 1'])
        self.assertEqual(2, sol.surplus_shares['single traveler 2'])

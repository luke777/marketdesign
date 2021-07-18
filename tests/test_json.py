import unittest
import json

from md.auction_json import *
from md.auction import *

# Tests encoding and decoding objects as json.

class JsonTests(unittest.TestCase):
    def test_bid_json(self):
        self.encode_then_decode(Bid(-3, {'a': 1}))
        self.encode_then_decode(Bid(-3, {'a': 1}, label='mybid'))

    def encode_then_decode(self, bid):
        bid_json = json.dumps(bid, indent=4, cls=ObjectEncoder)
        bid_dct = json.loads(bid_json)
        decoded_bid = decode_bid(bid_dct)
        self.assertBidsEqual(bid, decoded_bid)

    def assertBidsEqual(self, a, b):
        self.assertIsInstance(a, Bid)
        self.assertIsInstance(b, Bid)
        self.assertEqual(a.v, b.v)
        self.assertEqual(a.q, b.q)
        self.assertEqual(a.label, b.label)
        self.assertEqual(a.xor_group, b.xor_group)
        self.assertEqual(a.winning, b.winning)

    def assertBiddersEqual(self, a, b):
        self.assertIsInstance(a, Bidder)
        self.assertIsInstance(b, Bidder)
        self.assertEqual(a.name, b.name)
        self.assertEqual(len(a.bids), len(b.bids))
        for i in range(len(a.bids)):
            self.assertBidsEqual(a.bids[i], b.bids[i])

    def assertProblemsEqual(self, a, b):
        self.assertIsInstance(a, Problem)
        self.assertIsInstance(b, Problem)

        self.assertEqual(a.description, b.description)
        self.assertEqual(a.free_disposal, b.free_disposal)
        self.assertEqual(a.goods, b.goods)
        self.assertEqual(len(a.bidders), len(a.bidders))

        for i, bidder_a in enumerate(a.bidders):
            bidder_b = b.bidders[i]
            self.assertBiddersEqual(bidder_a, bidder_b)

    def test_bidder_json(self):
        b = Bidder('seller')
        b.add_bid(-3, {'a': 1})
        b.add_bid(-5, {'b': 1})
        json_str = json.dumps(b, indent=4, cls=ObjectEncoder)
        dct = json.loads(json_str)
        decoded_bidder = decode_bidder(dct)
        self.assertBiddersEqual(b, decoded_bidder)

    def test_problem_json(self):
        bidders = [Bidder('seller').add_bid(-3, {'a': 1})]
        p = Problem(bidders=bidders, description='Test case', free_disposal=True)
        json_str = json.dumps(p, indent=4, cls=ObjectEncoder)
        p_dct = json.loads(json_str)
        decoded_problem = decode_problem(p_dct)
        self.assertProblemsEqual(p, decoded_problem)

if __name__ == '__main__':
    unittest.main()

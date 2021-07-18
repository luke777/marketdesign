import unittest
from md.lindsay2018 import *

class MyTestCase(unittest.TestCase):

    def test_lindsay2018(self):
        p = Problem()
        buyer = Bidder('buyer').add_bid(20, {'a': -1})
        seller = Bidder('seller').add_bid(-10, {'a': 1})
        p.bidders = [buyer, seller]

        auction = Auction()
        sol = auction.winner_determination(p)
        rule = Lindsay2018()
        rule.calc_surplus_shares(sol)
        self.assertEqual(2, len(sol.payments.keys()))
        self.assertEqual(2, len(sol.surplus_shares.keys()))
        self.assertEqual(5, sol.surplus_shares['buyer'])
        self.assertEqual(5, sol.surplus_shares['seller'])
        self.assertEqual(15, sol.payments['buyer'])
        self.assertEqual(-15, sol.payments['seller'])

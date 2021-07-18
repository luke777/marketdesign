import unittest
from md.auction import *


class MyTestCase(unittest.TestCase):

    def test_vcg1(self):
        p = Problem()
        buyer1 = Bidder('buyer1').add_bid(10, {'a': -1})
        buyer2 = Bidder('buyer2').add_bid(9, {'a': -1})
        seller = Bidder('seller').add_bid(-5, {'a': 1})
        p.bidders = [buyer1, buyer2, seller]

        auction = Auction()
        sol = auction.winner_determination(p)
        vcg = VCG()
        vcg.calc_surplus_shares(sol)
        self.assertEqual(2, len(sol.payments.keys()))
        self.assertEqual(2, len(sol.surplus_shares.keys()))
        self.assertEqual(1, sol.surplus_shares['buyer1'])
        self.assertEqual(5, sol.surplus_shares['seller'])
        self.assertEqual(9, sol.payments['buyer1'])
        self.assertEqual(-10, sol.payments['seller'])

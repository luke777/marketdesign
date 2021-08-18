import unittest
from io import StringIO

from md.lindsay2018 import *
from md.auction_csv import *


class CsvTest(unittest.TestCase):

    def test1(self):
        p = Problem()
        p.bidders.append(Bidder('buyer1').add_bid(20, {'a': -1}))
        p.bidders.append(Bidder('buyer2').add_bid(15, {'a': -1}))
        p.bidders.append(Bidder('seller').add_bid(-10, {'a': 1}))

        auction = Auction()
        sol = auction.winner_determination(p)
        rule = Lindsay2018()
        rule.calc_surplus_shares(sol)

        si = StringIO()
        encode_csv_solution(sol, si)
        csv_str = si.getvalue()
        rows = csv_str.splitlines()
        # Should be 7 rows, 1 header + 2 for each bidder
        self.assertEqual(7, len(rows))

import unittest
from io import StringIO

from md.auction_txt import to_txt
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


    def assertBadFormat(self, csv_string):
        with self.assertRaises(Exception):
            reader = string2reader(csv_string)
            decode_csv_problem(reader)

    def test_parsing_csv(self):
        # Should throw exception since name is missing.
        self.assertBadFormat("""typo,xor_group,label,divisible,value,a
        seller,,seller's bid,,-10,1
        buyer L,,buyer L's bid,,22,-1
        buyer H,,buyer H's bid,,26,-1""")

        # Should throw exception since demand for good b is missing.
        self.assertBadFormat("""name,xor_group,label,divisible,value,a, b
        seller,,seller's bid,,-10,1
        buyer L,,buyer L's bid,,22,-1
        buyer H,,buyer H's bid,,26,-1""")

        # Should throw exception since good a column appears twice
        self.assertBadFormat("""name,xor_group,label,divisible,value,a, a
        seller,,seller's bid,,-10,1, 0
        buyer L,,buyer L's bid,,22,-1, 0
        buyer H,,buyer H's bid,,26,-1, 0""")

        # The first bid has an extra row
        self.assertBadFormat("""name,xor_group,label,divisible,value,a
                seller,,seller's bid,,-10,1,0
                buyer L,,buyer L's bid,,22,-1
                buyer H,,buyer H's bid,,26,-1""")

        # The bids in the xor group have different divisibility
        self.assertBadFormat("""name,xor_group,label,divisible,value,a
                     seller,xor1,seller's bid,1,-10,1
                     seller,xor1,seller's bid,2,-30,2
                     buyer L,,buyer L's bid,,22,-1
                     buyer H,,buyer H's bid,,26,-1""")


    def test_parsing_csv1(self):
        ex = """name,xor_group,label,divisible,value,a
seller,,seller's bid,,-10,1
buyer L,,buyer L's bid,,22,-1
buyer H,,buyer H's bid,,26,-1"""
        reader = string2reader(ex)
        p = decode_csv_problem(reader)
        a = Auction()
        sol = a.winner_determination(p)
        self.assertEqual(16, sol.surplus)


import unittest
from md.lindsay2018 import *
from md.auction_csv import *
import pathlib
import csv


class CsvTestCase(unittest.TestCase):

    def test_all_case(self):
        files = list(pathlib.Path('../examples').glob('*.csv'))

        for file in files:
            with open(str(file), 'rb') as f:
                reader = file2reader(f)
                bidders = decode_csv_bidders(reader)
                p = Problem(bidders=bidders)
                auction = Auction()
                solution = auction.winner_determination(p)
                self.assertTrue(solution.surplus >= 0)

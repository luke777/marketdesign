import unittest
from md.lindsay2018 import *
from md.auction_txt import *



class CsvTestCase(unittest.TestCase):

    def test1(self):
        bidders = parse_bidders("20 -1\n -10 1")
        self.assertEqual(2, len(bidders))
        self.assertEqual(20, bidders[0].bids[0].v)
        self.assertEqual(-1, bidders[0].bids[0].q['good 1'])
        self.assertEqual(-10, bidders[1].bids[0].v)
        self.assertEqual(1, bidders[1].bids[0].q['good 1'])

    # OR bids
    def test2(self):
        bidders = parse_bidders("20 -1 0 | 30 0 -1 \n -10 1 1")
        self.assertEqual(2, len(bidders))
        self.assertEqual(2, len(bidders[0].bids))
        self.assertEqual(1, len(bidders[1].bids))

        self.assertIsNone(bidders[0].bids[0].xor_group)
        self.assertIsNone(bidders[0].bids[1].xor_group)
        self.assertIsNone(bidders[1].bids[0].xor_group)

    # XOR bids
    def test3(self):
        bidders = parse_bidders("20 -1 0 , 30 0 -1 \n -10 1 1")

        self.assertIsNotNone(bidders[0].bids[0].xor_group)
        self.assertIsNotNone(bidders[0].bids[1].xor_group)
        self.assertIsNone(bidders[1].bids[0].xor_group)

    # Divisible bids
    def test4(self):
        bidders = parse_bidders("d 20 -1 0 , 30 0 -1 \n  m -10 1 1")
        self.assertEqual(Divisibility.DIVISIBLE, bidders[0].bids[0].divisibility)
        self.assertEqual(Divisibility.INDIVISIBLE, bidders[0].bids[1].divisibility)
        self.assertEqual(Divisibility.MIXED, bidders[1].bids[0].divisibility)

    # Extra whitespace
    def test5(self):
        bidders = parse_bidders("\n   20 -1\n\n-10 1\n")
        self.assertEqual(2, len(bidders))

    # Mismatched number of entries
    def test6(self):
        self.assertRaises(ValueError, parse_bidders, "20 -1 1\n -10 1")

    # Repeated trader name
    def test7(self):
        self.assertRaises(ValueError, parse_bidders, "Buyer: 20 -1\n Buyer: 20 -1")

    # Test empty bids
    def test8(self):
        self.assertRaises(ValueError, parse_bidders, "")

    def test9(self):
        self.assertRaises(ValueError, parse_bidders,"Buyer : : 20 -1\n -10 1")

    def test_encode(self):
        p = Problem()
        p.add_bidder(Bidder('buyer').add_bid(20, {'a': -1}))
        p.add_bidder(Bidder('seller').add_bid(-10, {'a': 1}))
        s = encode_problem(p)
        print(s)



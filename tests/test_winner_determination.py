import unittest
from md.auction import *


class MyTestCase(unittest.TestCase):

    def test_1(self):
        p = Problem()
        buyer = Bidder('buyer').add_bid(10, {'a': -1})

        seller = Bidder('seller').add_bid(-5, {'a': 1})
        p.bidders = [buyer, seller]

        auction = Auction()
        sol = auction.winner_determination(p)
        self.assertEqual(5, sol.surplus)
        self.assertEqual(1, sol.problem.bidders[0].bids[0].winning)
        self.assertEqual(1, sol.problem.bidders[1].bids[0].winning)

    def test_2(self):
        p = Problem()
        buyer = Bidder('buyer').add_bid(10, {'a': -1}).add_bid(10, {'b': -1})
        seller = Bidder('seller').add_bid(-5, {'a': 1}).add_bid(-5, {'c': 1})
        p.bidders = [buyer, seller]

        auction = Auction()
        sol = auction.winner_determination(p)
        self.assertEqual(5, sol.surplus)
        self.assertEqual(1, sol.problem.bidders[0].bids[0].winning)
        self.assertEqual(0, sol.problem.bidders[0].bids[1].winning)
        self.assertEqual(1, sol.problem.bidders[1].bids[0].winning)
        self.assertEqual(0, sol.problem.bidders[1].bids[1].winning)

    def test_xor1(self):
        p = Problem()
        buyer = Bidder('buyer').add_bid(20, {'a': -1}, xor_group='field1').add_bid(10, {'a': -1}, xor_group='field1')
        seller = Bidder('seller').add_bid(-4, {'a': 1}).add_bid(-5, {'a': 1})
        p.bidders = [buyer, seller]

        auction = Auction()
        sol = auction.winner_determination(p)
        self.assertEqual(16, sol.surplus)
        self.assertEqual(1, sol.problem.bidders[0].bids[0].winning)
        self.assertEqual(0, sol.problem.bidders[0].bids[1].winning)
        self.assertEqual(1, sol.problem.bidders[1].bids[0].winning)
        self.assertEqual(0, sol.problem.bidders[1].bids[1].winning)

    def test_free_disposal1(self):
        cases = {True: 5, False: 0}
        for fd, expected_surplus in cases.items():
            p = Problem(free_disposal=fd)
            buyer = Bidder('buyer').add_bid(10, {'a': -1})

            seller = Bidder('seller').add_bid(-5, {'a': 2})
            p.bidders = [buyer, seller]

            auction = Auction()
            sol = auction.winner_determination(p)
            self.assertEqual(expected_surplus, sol.surplus)

    def test_divisible_bids(self):
        cases = {True: 5, False: 0}
        for divisible, expected_surplus in cases.items():
            p = Problem()
            buyer = Bidder('buyer').add_bid(10, {'a': -1})

            seller = Bidder('seller').add_bid(-15, {'a': 3}, divisible=divisible)
            p.bidders = [buyer, seller]

            auction = Auction()
            sol = auction.winner_determination(p)
            self.assertEqual(expected_surplus, sol.surplus)
            if divisible:
                self.assertEqual(1, sol.problem.bidders[0].bids[0].winning)
                self.assertEqual(1/3, sol.problem.bidders[1].bids[0].winning)
            else:
                self.assertEqual(0, sol.problem.bidders[0].bids[0].winning)
                self.assertEqual(0, sol.problem.bidders[1].bids[0].winning)

if __name__ == '__main__':
    unittest.main()

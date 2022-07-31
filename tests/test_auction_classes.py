import unittest
from md.auction import *


class MyTestCase(unittest.TestCase):
    def test_bid1(self):
        bid = Bid(3, {"a": 1})
        self.assertEqual(3, bid.v)
        self.assertEqual({"a": 1}, bid.q)

    def test_bidder(self):
        b = Bidder("local")
        b.add_bid(10, {"a": 2})

        self.assertEqual(1, len(b.bids))

    def test_xor_groups(self):
        b = Bidder("local")
        b.add_bid(10, {"a": 2})
        b.add_bid(10, {"a": 2}, xor_group="field1")
        b.add_bid(10, {"a": 2}, xor_group="field1")
        b.add_bid(10, {"a": 2}, xor_group="field2")

        groups = b.xor_groups()
        self.assertEqual(2, len(groups))
        self.assertIn("field1", groups)
        self.assertIn("field2", groups)
        self.assertEqual([1, 2], groups["field1"])

    def test_problem1(self):
        p = Problem()
        b = Bidder("local")
        b.add_bid(10, {"z": 2})
        b.add_bid(10, {"a": 2})
        b.add_bid(10, {"b": 2})
        p.bidders = [b]
        goods = p.list_goods()
        self.assertEqual(["a", "b", "z"], goods)

    # Adding two bidders with same name should raise an exception on validation.
    def test_problem_validation(self):
        p = Problem()
        b1 = Bidder("local")
        b1.add_bid(10, {"z": 2})
        b2 = Bidder("local")
        b2.add_bid(10, {"z": 2})
        p.bidders.append(b1)
        p.bidders.append(b2)
        with self.assertRaises(Exception):
            p.validate()

if __name__ == '__main__':
    unittest.main()

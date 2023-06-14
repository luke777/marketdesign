from mip import Model, xsum, maximize, BINARY, CONTINUOUS
from collections import defaultdict
from copy import copy
from enum import Enum, unique


@unique
class Divisibility(Enum):
    INDIVISIBLE = 0
    DIVISIBLE = 1
    MIXED = 2


class Bid:
    def __init__(self, v, q, xor_group=None, winning=None, label=None,
                 divisible: Divisibility = Divisibility.INDIVISIBLE):
        if not isinstance(divisible, Divisibility):
            raise TypeError
        self.v = v
        self.q = q
        self.xor_group = xor_group
        self.winning = winning
        self.label = label
        self.divisibility = divisible

    # True if taking at least one type of good.
    def is_buying(self):
        for quantity in self.q.values():
            if quantity < 0:
                return True
        return False

    # True if providing at least one type of good.
    def is_selling(self):
        for quantity in self.q.values():
            if quantity > 0:
                return True
        return False

class Bidder:

    def __init__(self, name):
        self.name = name
        self.bids = []

    def add_bid(self, v, q, xor_group=None, label=None, divisible=Divisibility.INDIVISIBLE):
        b = Bid(v, q, label=label, divisible=divisible)
        if xor_group is not None:
            b.xor_group = xor_group
        self.bids.append(b)
        return self

    def bid_ids(self):
        return range(len(self.bids))

    def xor_groups(self):
        groups = defaultdict(list)
        for i, bid in enumerate(self.bids):
            if bid.xor_group is not None:
                groups[bid.xor_group].append(i)
        return groups

    # Return the ids of bids that are not xor bids.
    def non_xor_bid_ids(self):
        return [i for i in self.bid_ids() if self.bids[i].xor_group is None]

class Problem:

    def __init__(self, description=None, goods=None, bidders=None, free_disposal=True):
        if bidders is None:
            bidders = []
        self.description = description
        self.goods = goods
        self.free_disposal = free_disposal
        self.bidders = bidders

    def __copy__(self):
        return Problem(description=self.description, goods=self.goods, bidders=self.bidders,
                       free_disposal=self.free_disposal)

    def add_bidder(self, bidder):
        self.bidders.append(bidder)
        return self

    def get_bidder(self, name):
        for bidder in self.bidders:
            if bidder.name == name:
                return bidder
        raise KeyError(name)


    # Returns an order list of the goods.
    def list_goods(self):
        s = set()
        for bidder in self.bidders:
            for bid in bidder.bids:
                for good in bid.q.keys():
                    s.add(good)
        return sorted(s)

    # Returns a list of bidders' names
    def bidder_names(self):
        names = []
        for bidder in self.bidders:
            names.append(bidder.name)

        return names

    # Returns an upper bound on the surplus.  Calculated as sum of bids with positive value.
    def surplus_upper_bound(self):
        ub = 0
        for bidder in self.bidders:
            for bid in bidder.bids:
                if bid.xor_group is None:
                    ub += max(0, bid.v)

            for name, xor_group in bidder.xor_groups().items():
                group_max = 0
                for i in xor_group:
                    bid = bidder.bids[i]
                    group_max = max(group_max, bid.v)
                ub += group_max

        return ub


    # Raises an exception if an inconsistency is detected.
    def validate(self):
        # Check bids in the same xor group have the same divisibility.
        # Also check for repeated bidder names.
        bidder_names = set()
        for bidder in self.bidders:
            if bidder.name in bidder_names:
                raise ValueError("Repeated bidder name: {}".format(bidder.name))

            bidder_names.add(bidder.name)
            xorgroup2type = {}
            for bid in bidder.bids:
                if bid.xor_group:
                    if bid.xor_group in xorgroup2type:
                        if bid.divisibility != xorgroup2type[bid.xor_group]:
                            raise ValueError(
                                "Bids in same xor group should have the same divisibility: {}, {}".format(bidder.name, bid.xor_group))
                    else:
                        xorgroup2type[bid.xor_group] = bid.divisibility

class Solution:

    def __init__(self, rule=None, surplus=None, surplus_shares=None, payments=None, problem=None):
        if payments is None:
            payments = {}
        if surplus_shares is None:
            surplus_shares = {}
        self.rule = rule
        self.surplus = surplus
        self.surplus_shares = surplus_shares
        self.payments = payments
        self.problem = problem

    def winner_indexes(self):
        winners = []
        for i, bidder in enumerate(self.problem.bidders):
            for bid in bidder.bids:
                if bid.winning > 1e-6:
                    winners.append(i)
                    break
        return winners

    def loser_indexes(self):
        losers = []
        winners = self.winner_indexes()
        for i in range(len(self.problem.bidders)):
            if i not in winners:
                losers.append(i)
        return losers

    def populate_surplus_and_payment(self, bidder, surplus_share):
        self.surplus_shares[bidder.name] = surplus_share

        # payment is sum of winning bids minus surplus share.
        payment = -surplus_share
        for bid in bidder.bids:
            payment += bid.v * bid.winning
        self.payments[bidder.name] = payment

    def sum_payments(self):
        return sum(self.payments.values())


class Auction:

    def build_model(self, p):
        m = Model('winner_determination')
        m.verbose = 0
        I = range(len(p.bidders))

        mixed_xor_groups = set()

        def add_bid_var(i, j):
            name = 'bid({},{})'.format(i, j)
            bid = p.bidders[i].bids[j]
            if bid.divisibility == Divisibility.INDIVISIBLE:
                return m.add_var(var_type=BINARY, name=name)
            else:
                if bid.divisibility == Divisibility.MIXED and bid.xor_group is not None:
                    mixed_xor_groups.add(bid.xor_group)

                return m.add_var(var_type=CONTINUOUS, lb=0, ub=1, name=name)

        # Create variables
        winning = [[add_bid_var(i, j) for j in p.bidders[i].bid_ids()] for i in I]

        # Setup objective
        m.objective = maximize(
            xsum(p.bidders[i].bids[j].v * winning[i][j] for i in I for j in p.bidders[i].bid_ids()))

        # Add supply-demand constraints
        for good in p.list_goods():
            lhs = xsum(winning[i][j] * p.bidders[i].bids[j].q[good] for i in I for j in
                       p.bidders[i].bid_ids() if good in p.bidders[i].bids[j].q)
            if p.free_disposal:
                m += lhs >= 0, 'supply_is_at_least_demand'
            else:
                m += lhs == 0, 'supply_equals_demand'

        # Add XOR constraints
        for i in I:
            for group_name, bid_ids in p.bidders[i].xor_groups().items():
                if group_name in mixed_xor_groups:
                    # Need to set up a variable.
                    name = 'xorgroup_{}'.format(group_name)
                    var = m.add_var(var_type=BINARY, name=name)
                    m += xsum(winning[i][j] for j in bid_ids) == var, 'xor({},{})'.format(i, group_name)
                elif len(bid_ids) > 1:
                    m += xsum(winning[i][j] for j in bid_ids) <= 1, 'xor({},{})'.format(i, group_name)
        return m, I, winning

    def winner_determination(self, p):
        rt = Solution(problem=p)

        m, I, winning = self.build_model(p)
        m.optimize()
        for i in I:
            for j in p.bidders[i].bid_ids():
                if winning[i][j].x > 0:
                    p.bidders[i].bids[j].winning = winning[i][j].x
                else:
                    p.bidders[i].bids[j].winning = 0

        rt.surplus = m.objective_value
        p.goods = p.list_goods()
        return rt

    # Determines and returns surplus without populating the winning bids.  Intended
    # to be used when calculating vcg payment etc.
    def surplus_determination(self, p):
        m, I, winning = self.build_model(p)
        m.optimize()
        return m.objective_value


class PaymentRule:

    def solve(self, problem: Problem):
        a = Auction()
        sol = a.winner_determination(problem)
        self.calc_surplus_shares(sol)
        return sol

    def calc_surplus_shares(self, solution: Solution):
        pass


class PaB(PaymentRule):
    def calc_surplus_shares(self, sol: Solution):
        for i in sol.winner_indexes():
            bidder = sol.problem.bidders[i]
            sol.populate_surplus_and_payment(bidder, 0)

        sol.rule = 'pab'


class VCG(PaymentRule):
    def calc_surplus_shares(self, sol: Solution):
        # Work with a shallow copy of the problem, the list of bidders will be replaced in the loop below.
        problem = copy(sol.problem)
        auction = Auction()
        for i in sol.winner_indexes():
            problem.bidders = copy(sol.problem.bidders)
            bidder = problem.bidders.pop(i)
            surplus_without = auction.surplus_determination(problem)
            surplus_share = sol.surplus - surplus_without
            sol.populate_surplus_and_payment(bidder, surplus_share)

        sol.rule = 'vcg'

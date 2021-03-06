from mip import Model, xsum, maximize, BINARY, CONTINUOUS
from collections import defaultdict
from copy import copy


class Bid:
    def __init__(self, v, q, xor_group=None, winning=None, label=None, divisible=False):
        self.v = v
        self.q = q
        self.xor_group = xor_group
        self.winning = winning
        self.label = label
        self.divisible = divisible


class Bidder:

    def __init__(self, name):
        self.name = name
        self.bids = []

    def add_bid(self, v, q, xor_group=None, label=None, divisible=False):
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

    # Returns an order list of the goods.
    def list_goods(self):
        s = set()
        for bidder in self.bidders:
            for bid in bidder.bids:
                for good in bid.q.keys():
                    s.add(good)
        return sorted(s)


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
                if bid.winning > 0:
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

        def add_bid_var(i, j):
            name = 'bid[{}][{}]'.format(i, j)
            if p.bidders[i].bids[j].divisible:
                return m.add_var(var_type=CONTINUOUS, lb=0, ub=1, name=name)
            else:
                return m.add_var(var_type=BINARY, name=name)

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
                m += lhs >= 0, 'supply is at least demand'
            else:
                m += lhs == 0, 'supply equals demand'

        # Add XOR constraints
        for i in I:
            for group_name, bid_ids in p.bidders[i].xor_groups().items():
                if len(bid_ids) > 1:
                    m += xsum(winning[i][j] for j in bid_ids) <= 1, 'xor[{}][{}]'.format(i, group_name)
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




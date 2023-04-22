from md.auction import *
import math
from random import Random
import itertools
from collections import defaultdict
import time

# Implementation of the payment rule described in the paper "Shapley value based pricing for auctions and exchanges"
# https://doi.org/10.1016/j.geb.2017.10.020

class Lindsay2018(PaymentRule):

    def __init__(self, max_perms_to_generate: int = 100000, max_perms_to_consider: int = 1024, seed: int = 7777):
        self.max_perms_to_generate = max_perms_to_generate
        self.max_perms_to_consider = max_perms_to_consider
        self.seed = seed

    def gen_permutations(self, winners):
        permutations = []
        rnd = Random(self.seed)
        if math.factorial(len(winners)) > self.max_perms_to_generate:
            for i in range(self.max_perms_to_consider):
                perm = copy(winners)
                rnd.shuffle(perm)
                permutations.append(perm)
        else:
            permutations = list(itertools.permutations(winners))

        if len(permutations) > self.max_perms_to_consider:
            rnd.shuffle(permutations)
            permutations = permutations[0:self.max_perms_to_consider]

        return permutations

    def calc_surplus_shares(self, sol: Solution):

        #  Used to give progress updates for slow problems.
        start_time = time.time()
        last_time = start_time

        winners = sol.winner_indexes()


        permutations = self.gen_permutations(winners)
        n_perms = len(permutations)

        surplus_calculator = SurplusCalculator(sol)

        # Stores running sum of shares for each winner.
        shares_sums = defaultdict(lambda: 0)


        for j, perm in enumerate(permutations):
            current_time = time.time()
            if current_time > last_time + 10:
                last_time = current_time
                print('Permutation {} of {}'.format(j, n_perms))
            last_surplus = 0

            for position, i in enumerate(perm):

                surplus = surplus_calculator.calc_surplus(perm[0:position + 1])

                share = surplus - last_surplus
                shares_sums[i] = shares_sums[i] + share
                last_surplus = surplus


        for i in winners:
            surplus_share = shares_sums[i] / n_perms
            sol.populate_surplus_and_payment(sol.problem.bidders[i], surplus_share)

        sol.rule = 'lindsay2018'
        current_time = time.time()
        if current_time > start_time + 10:
            n_winners = len(winners)
            n_bidders = len(sol.problem.bidders)
            solve_time = round(current_time-start_time)
            print('{} bidders and {} winners.  Calculating prices took {} seconds with {} permutations.'.format(n_bidders, n_winners,solve_time, n_perms))

class SurplusCalculator:

    def __init__(self, sol: Solution):
        self.solution = sol
        self.winners = sol.winner_indexes()
        self.losers = sol.loser_indexes()
        self.auction = Auction()
        self.problem = copy(sol.problem)
        # Cache surplus values to avoid repeatedly solving the same MIP problem.
        self.cache = {frozenset(self.winners): sol.surplus}

    def calc_surplus(self, subset_winners):
        key = frozenset(subset_winners)
        if key in self.cache.keys():
            return self.cache[key]
        else:
            self.problem.bidders = []
            for i in self.losers:
                self.problem.bidders.append(self.solution.problem.bidders[i])
            for i in key:
                self.problem.bidders.append(self.solution.problem.bidders[i])
            surplus = self.auction.surplus_determination(self.problem)
            self.cache[key] = surplus
            return surplus

def get_rule(rule_name,  max_perms_to_consider: int = 1024):
    rule_name = rule_name.lower().strip()  # ignore case
    if rule_name == 'lindsay2018':
        rule = Lindsay2018(max_perms_to_consider=max_perms_to_consider)
    elif rule_name == 'vcg':
        rule = VCG()
    elif rule_name == 'pab':
        rule = PaB()
    else:
        raise ValueError('Unrecognised payment rule "{}".'.format(rule_name))
    return rule

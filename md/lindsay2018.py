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

    def calc_surplus_shares(self, sol: Solution):

        #Used to give progress updates for slow problems.
        start_time = time.time()
        last_time = start_time

        winners = sol.winner_indexes()
        losers = sol.loser_indexes()

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

        # Stores running sum of shares for each winner.
        shares_sums = defaultdict(lambda: 0)

        # Cache surplus values to avoid repeatedly solving the same MIP problem.
        cache = {frozenset(winners): sol.surplus}

        problem = copy(sol.problem)
        auction = Auction()
        n_perms = len(permutations)

        for j, perm in enumerate(permutations):
            current_time = time.time()
            if current_time > last_time + 10:
                last_time = current_time
                print('Permutation {} of {}'.format(j, n_perms))
            last_surplus = 0
            problem.bidders = [sol.problem.bidders[i] for i in losers]
            for position, i in enumerate(perm):
                problem.bidders.append(sol.problem.bidders[i])

                key = frozenset(perm[0:position + 1])
                if key in cache.keys():
                    surplus = cache[key]
                else:
                    surplus = auction.surplus_determination(problem)
                    cache[key] = surplus

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
            n_bidders = n_winners + len(losers)
            solve_time = round(current_time-start_time)
            print('{} bidders and {} winners.  Calculating prices took {} seconds with {} permutations.'.format(n_bidders, n_winners,solve_time, n_perms))


def get_rule(rule_name):
    rule_name = rule_name.lower().strip()  # ignore case
    if rule_name == 'lindsay2018':
        rule = Lindsay2018()
    elif rule_name == 'vcg':
        rule = VCG()
    elif rule_name == 'pab':
        rule = PaB()
    else:
        raise ValueError('Unrecognised payment rule "{}".'.format(rule_name))
    return rule

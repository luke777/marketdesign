from md.auction import Bid, Bidder, Divisibility
from md.auction_csv import to_number, encode_csv_solution
import re
from io import StringIO
from tabulate import tabulate

def parse_bidders(s):
    s = s.strip()
    lines = re.split('\n\\s*', s)
    bidders = []
    names = set()
    trader_id = 1
    last_n_goods = None
    for line in lines:
        if not line:
            continue

        # Optional bidder name is separated from bids by ':'
        if ':' in line:
            parts = line.split(':')
            if len(parts) > 2:
                raise ValueError('More than one colon in "{}"'.format(line))
            name = parts[0].strip()
            line = parts[1].strip()
        else:
            name = 'trader {}'.format(trader_id)
            trader_id += 1
        if name in names:
            raise ValueError('Two bidders with name {}'.format(name))
        else:
            names.add(name)
        bidder = Bidder(name)
        bidders.append(bidder)

        # XOR groups are separated by '|', bids by ',' and entries by ' '
        xor_groups = [x.strip() for x in line.split('|')]
        group_id = 1
        for group in xor_groups:
            bids = [x.strip() for x in group.split(',')]
            for bid_str in bids:
                items = bid_str.split()
                if items[0].lower() == 'd':
                    divisible = Divisibility.DIVISIBLE
                    items.pop(0)
                elif items[0].lower() == 'm':
                    divisible = Divisibility.MIXED
                    items.pop(0)
                else:
                    divisible = Divisibility.INDIVISIBLE

                n_goods = len(items)

                value = to_number(items[0])
                q = {}
                for i in range(1, len(items)):
                    good = 'good {}'.format(i)
                    q[good] = to_number(items[i])
                if len(bids) > 1:
                    xor_group = "xor_{}".format(group_id)
                else:
                    xor_group = None
                bidder.bids.append(Bid(value, q, divisible=divisible, xor_group=xor_group))

                if last_n_goods is not None:
                    if last_n_goods != n_goods:
                        raise ValueError(
                            "Not all bids have the same number of entries ({} and {})".format(last_n_goods, n_goods))
                last_n_goods = n_goods
            group_id += 1
    if len(bidders) < 2:
        raise ValueError("There must be at least 2 bidders.")
    return bidders

def to_txt(solution):
    si = StringIO()
    encode_csv_solution(solution, si, delimiter='|')

    data = []
    for row in si.getvalue().strip().split('\n'):
        data.append(row.strip().split('|'))
    note = 'Pricing = {}, total surplus = {}, sum of payments = {}'.format(solution.rule, solution.surplus,
                                                                           solution.sum_payments())
    table = tabulate(data, headers='firstrow', tablefmt='rst')
    return table + '\n' + note

def encode_problem(problem):
    si = StringIO()
    goods = problem.list_goods()
    def write_bid(bid):
        if bid.divisibility == Divisibility.DIVISIBLE:
            si.write(" d ")
        elif bid.divisibility == Divisibility.MIXED:
            si.write(" m ")

        si.write(str(bid.v))
        for good in goods:
            if good in bid.q:
                si.write(" " + str(bid.q[good]))
            else:
                si.write(" 0")

    for bidder in problem.bidders:
        si.write(bidder.name)
        si.write(": ")
        xor_groups = bidder.xor_groups()

        first_group = True
        # Write xor groups
        for key, bid_ids in xor_groups.items():
            if not first_group:
                si.write("| ")
            first_bid = True
            for bid_id in bid_ids:
                if not first_bid:
                    si.write(", ")
                bid = bidder.bids[bid_id]
                write_bid(bid)
                first_bid = False
                first_group = False
        # Write bids not in xor groups.
        for bid in bidder.bids:
            if bid.xor_group is None:
                if not first_group:
                    si.write("| ")
                write_bid(bid)
                first_group = False

        si.write("\n")
    return si.getvalue()
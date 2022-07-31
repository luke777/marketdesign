from md.auction import Bid, Bidder, Problem, Divisibility
from json import JSONEncoder


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Divisibility):
            return o.value
        dct = o.__dict__
        # Remove None keys with value None
        return {k: v for k, v in dct.items() if v is not None}


def decode_bid(dct):
    if 'divisible' in dct and 'divisibility' in dct:
        raise ValueError("Has both divisible and divisibility")

    for k in ['label', 'winning', 'xor_group']:
        if k not in dct:
            dct[k] = None

    divisible = Divisibility.INDIVISIBLE
    #Old api
    if 'divisible' in dct:
        if dct['divisible']:
            divisible = Divisibility.DIVISIBLE
        else:
            divisible = Divisibility.INDIVISIBLE

    #Newer api
    if 'divisibility' in dct:
        divisible = Divisibility(dct['divisibility'])

    return Bid(dct['v'], dct['q'], label=dct['label'], winning=dct['winning'], xor_group=dct['xor_group'],
               divisible=divisible)


def decode_bidder(dct):
    b = Bidder(dct['name'])
    for bid in dct['bids']:
        b.bids.append(decode_bid(bid))

    return b


def decode_problem(dct):
    bidders = []
    for bidder in dct['bidders']:
        bidders.append(decode_bidder(bidder))
    for k in ['description', 'goods']:
        if k not in dct:
            dct[k] = None
    if 'free_disposal' not in dct:
        dct['free_disposal'] = True
    problem = Problem(bidders=bidders, description=dct['description'], goods=dct['goods'],
                   free_disposal=dct['free_disposal'])
    problem.validate()
    return problem

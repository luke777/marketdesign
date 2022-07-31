from md.auction import Bid, Bidder, Divisibility, Problem
import csv
import chardet as chardet
import os

HEADERS = ('name', 'xor_group', 'label', 'divisible', 'value')


def to_number(s):
    try:
        x = int(s)
    except ValueError:
        x = float(s)
    return x

def get_file_extension(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower()

def decode_csv_bid(dct, goods):
    for k in ['label', 'divisible', 'xor_group']:
        if k not in dct:
            dct[k] = None
        elif dct[k] is not None:
            if dct[k].strip() == '':
                dct[k] = None

    # Set xor_group to None in case of empty string.
    if dct['xor_group'] is not None:
        if dct['xor_group'].strip() == '':
            dct['xor_group'] = None
    q = {}
    for good in goods:
        if good in dct.keys():
            s = dct[good].strip()
            # Ignore empty strings
            if s:
                q[good] = to_number(s)
    v = to_number(dct['value'])
    if dct['divisible'] == '1':
        divisible = Divisibility.DIVISIBLE
    elif dct['divisible'] == '2':
        divisible = Divisibility.MIXED
    else:
        divisible = Divisibility.INDIVISIBLE
    return Bid(v, q, label=dct['label'], xor_group=dct['xor_group'], divisible=divisible)

def decode_csv_problem(reader: csv.DictReader):
    bidders = decode_csv_bidders(reader)
    problem = Problem(bidders=bidders)
    problem.validate()
    return problem

def decode_csv_bidders(reader: csv.DictReader):
    # Check for duplicate column names
    n_columns = len(reader.fieldnames)
    if n_columns != len(set(reader.fieldnames)):
        raise ValueError(str(reader.fieldnames))

    goods = [good for good in reader.fieldnames if good not in HEADERS]
    bidders = []
    name2bidder = {}
    for row in reader:
        if n_columns != len(row):
            raise ValueError(row)
        name = row['name']
        if name not in name2bidder.keys():
            bidder = Bidder(name)
            name2bidder[name] = bidder
            bidders.append(bidder)
        else:
            bidder = name2bidder[name]
        bidder.bids.append(decode_csv_bid(row, goods))

    return bidders


def encode_csv_solution(solution, csv_file, delimiter=','):
    goods = solution.problem.list_goods()
    extra = ['winning', 'surplus share', 'payment']
    headers = list(HEADERS) + goods + extra
    writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()

    for bidder in solution.problem.bidders:
        # First write the bids.
        for bid in bidder.bids:
            row = {'name': bidder.name, 'value': bid.v}
            if bid.xor_group:
                row['xor_group'] = bid.xor_group
            if bid.label:
                row['label'] = bid.label
            if bid.divisibility:
                v = bid.divisibility.value
                if v == 0:
                    v = None
                row['divisible'] = v
            for good in bid.q.keys():
                row[good] = bid.q[good]
            row['winning'] = bid.winning
            writer.writerow(row)

        # Second write the surplus shares row.
        row = {'name': bidder.name,
               'surplus share': solution.surplus_shares.get(bidder.name),
               'payment': solution.payments.get(bidder.name)}
        writer.writerow(row)

def encode_csv_problem(problem, csv_file, delimiter=','):
    goods = problem.list_goods()
    headers = list(HEADERS) + goods
    writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()

    for bidder in problem.bidders:
        # First write the bids.
        for bid in bidder.bids:
            row = {'name': bidder.name, 'value': bid.v}
            if bid.xor_group:
                row['xor_group'] = bid.xor_group
            if bid.label:
                row['label'] = bid.label
            if bid.divisibility:
                v = bid.divisibility.value
                if v == 0:
                    v = None
                row['divisible'] = v
            for good in bid.q.keys():
                row[good] = bid.q[good]
            writer.writerow(row)

def file2reader(f):
    # Use chardet to infer the encoding of the csv file.
    result = chardet.detect(f.read())
    encoding = result['encoding']
    f.seek(0)

    fstring = f.read().decode(encoding)

    lines = fstring.splitlines()
    header = [h.strip() for h in lines[0].split(',')]
    lines.pop(0)
    return csv.DictReader(lines, fieldnames=header)

def string2reader(s):
    lines = s.splitlines()
    header = [h.strip() for h in lines[0].split(',')]
    lines.pop(0)
    return csv.DictReader(lines, fieldnames=header)
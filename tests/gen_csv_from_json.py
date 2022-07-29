import json
import csv
import pathlib

from md.auction_json import decode_problem

if __name__ == '__main__':

    files = list(pathlib.Path('../examples').glob('*.json'))
    for filename_json in files:
        with open(filename_json) as json_file:
            dct = json.load(json_file)
            problem = decode_problem(dct)

            goods = problem.list_goods()
            headers = ['name', 'xor_group', 'label', 'divisible', 'value'] + goods

            filename_csv = str(filename_json).replace('json', 'csv')
            with open(filename_csv, mode='w', newline='', encoding='utf-8') as output:
                writer = csv.DictWriter(output, fieldnames=headers)
                writer.writeheader()
                for bidder in problem.bidders:
                    for bid in bidder.bids:
                        dct = {'name': bidder.name, 'xor_group': bid.xor_group, 'label': bid.label,
                               'value': bid.v}
                        if bid.divisibility is True:
                            dct['divisible'] = 1
                        for good in goods:
                            if good in bid.q.keys():
                                dct[good] = bid.q[good]

                        writer.writerow(dct)

import argparse
import json
import time

from md.auction import Problem, Auction
from md.auction_csv import file2reader, decode_csv_bidders, encode_csv_solution, get_file_extension
from md.auction_json import decode_problem, ObjectEncoder
from md.auction_txt import parse_bidders, to_txt
from md.lindsay2018 import get_rule


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-o', dest='output', help='output filename')
    parser.add_argument('-r', '--rule', dest='rule', help='the payment rule', choices=['lindsay2018', 'pab', 'vcg'],
                        default='lindsay2018')
    parser.add_argument('--no-free-disposal', dest='free_disposal', action='store_false')
    parser.set_defaults(free_disposal=True)

    args = parser.parse_args()

    p = read_problem(args.input, free_disposal=args.free_disposal)

    auction = Auction()
    solution = auction.winner_determination(p)
    rule = get_rule(args.rule)
    rule.calc_surplus_shares(solution)

    if args.output:
        with open(args.output, 'w', newline='') as f:
            output_extension = get_file_extension(args.output)
            if output_extension == '.csv':
                encode_csv_solution(solution, f)
            elif output_extension == '.json':
                json.dump(solution, f, indent=4, cls=ObjectEncoder)
            else:
                f.write(to_txt(solution))

    else:
        print(to_txt(solution))

    print("--- %s seconds ---" % (time.time() - start_time))

def read_problem(input_filename, free_disposal=None):
    input_extension = get_file_extension(input_filename)
    if input_extension == '.csv':
        with open(input_filename, 'rb') as f:
            reader = file2reader(f)
            bidders = decode_csv_bidders(reader)
            p = Problem(bidders=bidders)
            p.free_disposal = free_disposal
    elif input_extension == '.json':
        with open(input_filename) as json_file:
            dct = json.load(json_file)
            p = decode_problem(dct)
            if not free_disposal:
                raise ValueError('free-disposal should be set in the json not via command line.')
    else:
        with open(input_filename) as txt_file:
            txt = txt_file.read()
            bidders = parse_bidders(txt)
            p = Problem(bidders=bidders)
            p.validate()
            p.free_disposal = free_disposal
    return p


if __name__ == "__main__":
    main()

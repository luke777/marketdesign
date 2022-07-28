import argparse
import json
from md.auction import Problem, Auction
from md.auction_csv import file2reader, decode_csv_bidders, encode_csv_solution, get_file_extension, encode_csv_problem
from md.auction_json import decode_problem, ObjectEncoder
from md.auction_txt import parse_bidders, to_txt
from solver import read_problem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-o', dest='output', help='output filename')
    parser.add_argument('--no-free-disposal', dest='free_disposal', action='store_false')
    parser.set_defaults(free_disposal=True)

    args = parser.parse_args()
    p = read_problem(args.input, free_disposal=args.free_disposal)

    if args.output:
        with open(args.output, 'w', newline='') as f:
            output_extension = get_file_extension(args.output)
            if output_extension == '.csv':
                encode_csv_problem(p, f)
            elif output_extension == '.json':
                json.dump(p, f, indent=4, cls=ObjectEncoder)
            else:
                raise NotImplementedError("Not implemented yet")

    else:
        raise NotImplementedError("Not implemented yet")

if __name__ == "__main__":
    main()

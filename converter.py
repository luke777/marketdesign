import argparse
import json

from md.auction_csv import get_file_extension, encode_csv_problem
from md.auction_json import ObjectEncoder
from md.auction_txt import encode_problem
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
                s = encode_problem(p)
                f.write(s)

    else:
        s = encode_problem(p)
        print(s)

if __name__ == "__main__":
    main()

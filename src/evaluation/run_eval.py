import argparse
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold_standard_file', type=str, required=True)
    parser.add_argument('--system_output_file', type=str, required=True)
    parser.add_argument('--ontology_file', type=str, required=True)
    args = parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
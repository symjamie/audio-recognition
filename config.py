# Filename: config.py
# Description: configurations for main.py.
# Author: Yiming Sun
# Created: Dec 10, 2019

import argparse

parser = argparse.ArgumentParser()

def add_argument_group(name):
    arg = parser.add_argument_group(name)

    return arg


# ----------------------------------------
# Arguments for the main program.
main_arg = add_argument_group("main")

main_arg.add_argument("--mode", type=str,
					default="query",
					choices=["build", "query"],
					help="Run mode (build or query).")

main_arg.add_argument("--db", type=str,
					help="Filename of fingerprint database.")

main_arg.add_argument("--sr", type=int,
					default=22050,
					help="Universal sample rate.")

# ----------------------------------------
# Arguments for build.
build_arg = add_argument_group("build")

build_arg.add_argument("--dataset", type=str,
                    help="Directory of audio dataset.")

build_arg.add_argument("--win_size", type=int,
                    default=4096,
                    help="Window size.")

build_arg.add_argument("--anchor_dist", type=int,
                    default=5,
                    help="Distance from each anchor point to its target zone (default: 5).")

build_arg.add_argument("--fan_out", type=int,
                    default=10,
                    help="Fan out factor: number of points in each target zone (default: 10).")


# ----------------------------------------
# Arguments for query.
query_arg = add_argument_group("query")

query_arg.add_argument("--sample", type=str,
                    default=None,
                    help="Filename of sample audio file for query.")


def get_config():
    config, unparsed = parser.parse_known_args()

    return config, unparsed


def print_usage():
    parser.print_usage()
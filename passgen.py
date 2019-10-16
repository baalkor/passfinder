# Passgen
# Goal : This tool will generate all possible mutations for a given string based on tables
# Usage : ./passgen.py <basepassword>
#


import argparse
import os
import glob
import yaml
import hashlib
import sys
VERBOSE=True
NO_PASSWORD_PROVIDED=2
NO_TABLES_FOUND=1
EXIT_SUCCESS=0
DefaultScriptDir = os.path.dirname(os.path.realpath(__file__))


def listTable(basePath):

    tables = [file for file in glob.glob( basePath +  os.sep + "*.yml")]
    if len(tables) == 0:
        print("No tables found !")
        return NO_TABLES_FOUND
    else:
        for table in tables:
            print("%s" % os.path.basename(table))
        return EXIT_SUCCESS

# Recursively get all the permutations
def passgen(symbol_list, existing_output=None):
    out_list = []

    # Grab the first list of symbols from the symbol_list

    char_symbols = symbol_list.pop(0)

    # If output was passed, create the permutations for it and char_symbols
    if existing_output:
        out_list = [a + b for b in char_symbols for a in existing_output]
    # If no output was passed, this is first execution, make a new out_list
    else:
        out_list = char_symbols

    # If we haven't exhausted the input symbols, recurse
    if symbol_list:
        return passgen(symbol_list, existing_output=out_list)

    # If we are out of input symbol lists, return to break the recursion
    return out_list

def loadTable(filename):
    with open(filename, 'r') as tableFile:
        mt = yaml.load(tableFile, Loader=yaml.SafeLoader)
    return mt

def debug(message):
    if VERBOSE:
        print(message, file=sys.stderr)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
        passgen.py
        Author : baalkor@gmail.com
        Goal : Tools that generate all possible mutations against a string
    """)
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-p","--password", help="Base password where all mutations will be performed")
    group.add_argument("-l", "--list-mutation-tables", help="List mutation tables", action="store_true")
    parser.add_argument("--mutations-table-path", help="Path to file containing tables YAML", default=DefaultScriptDir)

    parser.add_argument("-m", "--mask", help="""Allow to specify a mask for unkown character. The character will be inserted at the given position.
        Examples
            ./passgen.py -p 'Test' -m '__[0-9]'      :  Te[0-9]st
            ./passgen.py -p 'abd' -m '__[a-z]_[0-9]' :  ab[a-z]d[0-9]
        However the mask cannot be longer that length of string + 1
            ./passgen.py -p 'abd' -m '__[a-z]____[0-9]' => ERROR don't know what to do"""
        )
    parser.add_argument("-t", "--mutation-table", help="Tables to use", default="simple.yml")
    parser.add_argument("-o","--output", help="Output file",metavar="FILE", type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument("-v", "--verbose", help="Display more information on stderr", default=False,action="store_true")
    groupHash = parser.add_mutually_exclusive_group()
    groupHash.add_argument("-n", "--disable-build-hash", help="Disable hash computation", action="store_true", default=False)
    groupHash.add_argument("--hash-alg", help="Select hash mechanism, default=sha1-224", choices=['sha1', 'sha224'], default='sha1')

    args = parser.parse_args()


    VERBOSE = args.verbose

    debug("+Starting program")


    if args.list_mutation_tables:
        debug("Looking for yml in %s " % args.mutations_table_path + os.sep)
        listTable(args.mutations_table_path)
        exit(EXIT_SUCCESS)
    else:
        basePassword = args.password
        mask = args.mask
        if basePassword is None:
            debug("No password given")
            exit(NO_PASSWORD_PROVIDED)

        if len(basePassword) >= 10:
            print("!Warning can take very long to compute")
            input("Press <enter> to continue or abort with Ctrl-C!")

    debug("Looking for yml in %s " % args.mutations_table_path + os.sep)
    symbols = loadTable(args.mutations_table_path + os.sep + args.mutation_table)

    symbol_list = [symbols[char] for char in basePassword.upper()]
    passwords = set(passgen(symbol_list))

    debug("%d passwords generated" % len(passwords))
    if args.disable_build_hash:
        for proposal in passwords:
            args.output.write("%s\n" % proposal)
    else:
        for proposal in passwords:
            h = hashlib.new(args.hash_alg)
            h.update(bytearray(proposal, encoding="utf-8"))
            args.output.write( "%s %s\n" % (h.hexdigest(), proposal) )

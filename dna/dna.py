import csv
import sys
from sys import argv

"""
debug50 python dna.py databases/large.csv sequences/1.txt
"""
def main():

    argv.pop(0)
    args = cmd(argv, True)
        
    rows = []
    while True:
        try:    
            with open(args[0]) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    rows.append(row)
            break
        except FileNotFoundError:
            args = cmd(args, False)

    while True:
        try:    
            with open(args[1]) as file:
                dna = file.read()
            break
        except FileNotFoundError:
            args = cmd(args, False)



    # TODO: Find longest match of each STR in DNA sequence
    results = dict(rows[1])
    del results["name"]
    for i in results:
        results[i] = str(longest_match(dna, i))

    # TODO: Check database for matching profiles
    for row in rows:
        for key in results:
            if row[key] != results[key]:
                break
        else:
            print(row['name'])
            break
    else:
        print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


def cmd(files, found):
    args = files
    if found:
        if len(args) != 2:
            print("Missing command-line arguments")
            args.clear()
            args.append(input("Input path for database: "))
            args.append(input("Input path for sequence: "))
            return cmd(args, True)
        
        if ".txt" not in args[1] or ".csv" not in args[0]:
            print("No file")
            args.clear()
            args.append(input("Input path for database: "))
            args.append(input("Input path for sequence: "))
            return cmd(args, True)
    else:
        print("Not found")
        args.clear()
        args.append(input("Input path for database: "))
        args.append(input("Input path for sequence: "))
        return cmd(args, True)
    return args


main()

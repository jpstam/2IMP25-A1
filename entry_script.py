import csv
import sys
import os
import time


def write_output_file():
    '''
    Writes a dummy output file using the python csv writer, update this 
    to accept as parameter the found trace links. 
    '''

    if not os.path.exists('/output'):
        os.makedirs('/output')

    with open('/output/links.csv', 'w+') as csvfile:

        writer = csv.writer(csvfile, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)


        fieldnames = ["id", "links"]

        writer.writerow(fieldnames)

        writer.writerow(["UC1", "L1, L34, L5"]) 
        writer.writerow(["UC2", "L5, L4"])

def read_input_file(ifile):
    '''
    Parses an input file to a list of requirements that are lists of words.
    :param ifile: The csv file to read
    :return: The list of requirements
    '''

    print("hoi")
    with open(ifile) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        reqs = {}
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                reqs[row[0]] = row[1].split(" ")
            line_count += 1
        return reqs


if __name__ == "__main__":
    '''
    Entry point for the script
    '''
    if len(sys.argv) < 2:
        print("Please provide an argument to indicate which matcher should be used")
        exit(1)

    match_type = 0

    try:
        match_type = int(sys.argv[1])
    except ValueError as e:
        print("Match type provided is not a valid number")
        exit(1)    

    print(f"Hello world, running with matchtype {match_type}!")

    # Read input low-level requirements and count them (ignore header line).
    with open("/input/low.csv") as inputfile:
        print(f"There are {len(inputfile.readlines()) - 1} low-level requirements")

    lowreqs = read_input_file("/input/low.csv")
    print(lowreqs)

    write_output_file()
    time.sleep(15)
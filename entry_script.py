import csv
import sys
import os
import time
import re
from nltk import word_tokenize
from nltk.stem import PorterStemmer


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
        spacesre = re.compile(r'^\s*$')
        for row in csv_reader:
            if line_count > 0:
                reqs[row[0]] = [i for i in row[1].lower().replace(".", "").replace(",", "").split(" ") if not spacesre.match(i)]
            line_count += 1
        return reqs

def get_stopwords():
    try:
        stopfile = open("stopwords.txt", 'r')
    except IOError:
        print("Error: File with stopwords does not exist.")
        return 0

    stopwords = stopfile.read().lower().splitlines()
    stopfile.close()
    return stopwords

def tokenize(reqs):
    outreqs = {}
    for k, v in reqs.items():
        print(v)
        outreqs[k] = word_tokenize(v)
    return outreqs

def remove_stop_words(inreqs):
    stopwords = get_stopwords()
    outreqs = {}
    for k, v in inreqs.items():
        app = []
        for x in v:
            if x not in stopwords:
                app.append(x)
        outreqs[k] = app
    return outreqs

def stem_words(reqs):
    porter = PorterStemmer()
    stem_reqs= {}
    for k, v in reqs.items():
        app = []
        for x in v:
            app.append(porter.stem(x))
        stem_reqs[k] = app
    return stem_reqs

def preproc(reqs):
    #reqtok = tokenize(reqs)
    reqrsw = remove_stop_words(reqs)
    reqstem = stem_words(reqrsw)
    return reqstem

def create_master_vocab(high, low):
    #using set instead of list to remove duplicates in master_vocab
    vocab = set()
    for k, v in high.items():
        for x in v:
            vocab.add(x)
    for k, v in low.items():
        for x in v:
            vocab.add(x)
    return vocab

def create_vector_rep(voc, reqs):

#return a vector as described

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
    with open("/input/low.csv", 'r') as inputfile:
        print(f"There are {len(inputfile.readlines()) - 1} low-level requirements")


    lowreqs = read_input_file("/input/low.csv")
    highreqs = read_input_file("/input/high.csv")
    prohigh = preproc(highreqs)
    prolow = preproc(lowreqs)

    masterVocab = create_master_vocab(prohigh, prolow)
    highvec = create_vector_rep(masterVocab, prohigh)

    write_output_file()
    time.sleep(15)

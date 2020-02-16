import csv
import sys
import os
import time
import re
import math
from nltk import word_tokenize
from nltk.stem import PorterStemmer as Stemmer


def write_output_file(result):
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
        for k, v in result.items():
            writer.writerow([k,v])



def read_input_file(ifile):
    '''
    Parses an input file to a list of requirements that are lists of words.
    :param ifile: The csv file to read
    :return: The list of requirements
    '''

    with open(ifile) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        reqs = {}
        line_count = 0
        spacesre = re.compile(r'^\s*$')
        for row in csv_reader:
            if line_count > 0:
                reqs[row[0]] = [i for i in row[1].lower().replace(".", "").replace(",", "").split(" ") if
                                not spacesre.match(i)]
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
    porter = Stemmer()
    stem_reqs = {}
    for k, v in reqs.items():
        app = []
        for x in v:
            app.append(porter.stem(x))
        stem_reqs[k] = app
    return stem_reqs


def preproc(reqs):
    # reqtok = tokenize(reqs)
    reqrsw = remove_stop_words(reqs)
    reqstem = stem_words(reqrsw)
    return reqstem


def create_master_vocab(high, low):
    # using set instead of list to remove duplicates in master_vocab
    vocab = set()
    for k, v in high.items():
        for x in v:
            vocab.add(x)
    for k, v in low.items():
        for x in v:
            vocab.add(x)
    return vocab


def create_vector_rep(voc, reqs):
    vector_rep = {}
    vector_temp = {}
    req_counter = 0
    for k, v in reqs.items():
        vector_temp = create_vector(voc, v)
        vector_rep[k] = vector_temp
        req_counter += 1
    vector_result = add_idf(req_counter, vector_rep)
    return vector_result


def create_vector(voc, req):
    vector = []
    x = 0
    for k in voc:
        counter = 0
        for z in req:
            if z == k:
                counter += 1
        vector.append(counter)
        x += 1
    return vector


def add_idf(n, vectors):
    d = 0
    for k, v in vectors.items():
        counter = 0
        for p in v:
            if p > 0:
                d = 0
                for x, y in vectors.items():
                    if y[counter] > 0:
                        d += 1
                vectors[str(k)][int(p)] = calc_idf(n, d)
            counter += 1
    return vectors


def calc_idf(n, d):
    number = n / d
    return math.log2(number)


def create_simmatrix(high, low):
    resultmatrix = {}
    for k, v in high.items():
        tempvector = {}
        for x, y in low.items():
            tempvector[x] = calculate_cos(v, y)
        resultmatrix[k] = tempvector
    return resultmatrix


def calculate_cos(highvec, lowvec):
    top = 0
    count = 0
    for v in highvec:
        top = top + (highvec[count] * lowvec[count])
        count += 1
    bottoml = 0
    bottomr = 0
    for v in highvec:
        bottoml = bottoml + (v * v)
    bottoml = math.sqrt(bottoml)
    for v in lowvec:
        bottomr = bottomr + (v * v)
    bottomr = math.sqrt(bottomr)
    bottom = bottoml * bottomr
    return top / bottom


def tracelink(matrix, var):
    result = {}
    temp = {}
    if var == 0:
        for k, l in matrix.items():
            counter = 0
            for v, w in l.items():
                if w > 0:
                    temp[counter] = v
                    counter += 1
            result[k] = temp
    if var == 1:
        for k, l in matrix.items():
            counter = 0
            for v, w in l.items():
                if w >= 0.25:
                    temp[counter] = v
                    counter += 1
            result[k] = temp
    if var == 2:
        for k, l in matrix.items():
            top = 0
            toppair = "" 
            print(toppair)
            print(top)
            for v, w in l.items():
                if w >= 0.67 and w > top:
                    top = w
                    toppair = v
            #if top != 0:
            result[k] = toppair
            #else:
             #   result[k] ="" 
    return result

#def evaluate ():
    # output = open("/output/link.csv","r")
    # validator = open("/asdasdasa ","r")  




# return a vector as described

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
    lowvec = create_vector_rep(masterVocab, prolow)
    simmatrix = create_simmatrix(highvec, lowvec)
    result = tracelink(simmatrix, match_type)
    #print(simmatrix)
    print(result)
    write_output_file(result)
    #evaluate()

import csv
import sys
import os
import math
import nltk
import numpy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer as Stemmer


def ntlk_prereq():
    nltk.download('stopwords')
    nltk.download('punkt')


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
        for row in csv_reader:
            if line_count > 0:
                reqs[row[0]] = row[1]
            line_count += 1
        return reqs



def tokenize(reqs):
    outreqs = {}
    for k, v in reqs.items():
        outreqs[k] = word_tokenize(v)
    return outreqs


def remove_stop_words(inreqs):
    stop_words = set(stopwords.words('english'))
    outreqs = {}
    for k, v in inreqs.items():
        outreqs[k] = [w for w in v if not w in stop_words]
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
    reqtok = tokenize(reqs)
    reqrsw = remove_stop_words(reqtok)
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
    # initialize d (in how many requirements each word occurs) to all 0's
    d = numpy.array([0 for i in voc])
    for k, v in reqs.items():
        vector_rep[k] = [v.count(k) for k in voc]
        # add 1 if word occurs.
        d += numpy.array([1 if t > 0 else 0 for t in vector_rep[k]])
    # long comprehension, but explanation:
    # create new dict with same keys as vector_rep
    # value is an list, based on list from vector_rep
    # if the value is > 0 then:
    # log(n/d) n = number of requirement by len, d is constructed above and index is obtained by enumerate construct
    # else value 0
    vector_result = {k:[math.log2(len(reqs)/d[i]) if int(val) > 0 else 0 for i, val in enumerate(v)] for k, v in vector_rep.items()}
    return vector_result


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
            # print(toppair)
            # print(top)
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

    ntlk_prereq()

    lowreqs = read_input_file("/input/low.csv")
    highreqs = read_input_file("/input/high.csv")
    prohigh = preproc(highreqs)
    prolow = preproc(lowreqs)
    masterVocab = create_master_vocab(prohigh, prolow)
    highvec = create_vector_rep(masterVocab, prohigh)
    lowvec = create_vector_rep(masterVocab, prolow)
    simmatrix = create_simmatrix(highvec, lowvec)
    result = tracelink(simmatrix, match_type)
    write_output_file(result)
    #evaluate()

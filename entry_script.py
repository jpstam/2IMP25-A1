import csv
import sys
import os
import math
import nltk
import numpy
import pprint
from scipy import spatial
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer as Stemmer


def nltk_prereq():
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
        writer = csv.writer(csvfile, delimiter=",", quotechar="\"", quoting=csv.QUOTE_ALL)

        fieldnames = ["id", "links"]

        writer.writerow(fieldnames)
        for k, v in result.items():
            writer.writerow([k, ','.join(v)])


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
    return {k: word_tokenize(v) for k, v in reqs.items()}


def remove_stop_words(inreqs):
    stop_words = set(stopwords.words('english'))
    return {k: [w for w in v if not w in stop_words] for k, v in inreqs.items()}


def stem_words(reqs):
    porter = Stemmer()
    return {k: [
        porter.stem(x) for x in v
    ] for k, v in reqs.items()}


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
    vector_result = {k: [
        val * math.log2(len(reqs) / d[i]) if int(val) > 0 else 0 for i, val in enumerate(v)
    ] for k, v in vector_rep.items()}
    return vector_result


def create_simmatrix(high, low):
    # return two dimensional dict.
    # for each high level req:
    # calculate cos similarity for each low level req.
    return {k: {
        x: (1 - spatial.distance.cosine(v, y)) for x, y in low.items()
    } for k, v in high.items()}


def tracelink(matrix, var):
    if var == 0:
        return {k: [
            x for x, y in v.items() if y > 0
        ] for k, v in matrix.items()}
    if var == 1:
        return {k: [
            x for x, y in v.items() if y >= 0.25
        ] for k, v in matrix.items()}
    if var == 2:
        return {k: [
            x for x, y in v.items() if y >= 0.67 * max(v.values())
        ] for k, v in matrix.items()}


def evaluate(res, valid):
    manualtool = 0
    notmanualtool = 0
    manualnottool = 0
    notmanualnottool = 0
    # valid = tokenize(valid)
    for k, v in res.items():
        for x in v:
            if x in valid[k].split(","):
                manualtool += 1
            else:
                notmanualtool += 1
                print(f'Misclassification: {x} linked with {k}')
    for k, v in valid.items():
        for x in v.split(","):
            # if x.strip for empty sets in valid
            if x.strip() and x not in res[k]:
                manualnottool += 1
                print(f'Link not found: {x} not linked with {k}')
    lengthlow = len(read_input_file("/input/low.csv"))
    lengthhigh = len(read_input_file("/input/high.csv"))
    notmanualnottool = (lengthlow * lengthhigh) - manualtool - notmanualtool - manualnottool

    recall = manualtool / (manualtool + manualnottool)
    precision = manualtool / (manualtool + notmanualtool)
    fmeasure = 2 * precision * recall / (precision + recall)

    print("number of predicted which are identified " + str(manualtool))
    print("number of predicted which are not identified " + str(manualnottool))
    print("number of not predicted which are identified " + str(notmanualtool))
    print("number of not predicted which are not identified " + str(notmanualnottool))
    print("\n")
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F-measure: {fmeasure}')


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

    nltk_prereq()

    pp = pprint.PrettyPrinter(width=41, compact=True)

    lowreqs = read_input_file("/input/low.csv")
    highreqs = read_input_file("/input/high.csv")
    validation = read_input_file("/input/links.csv")
    prohigh = preproc(highreqs)
    prolow = preproc(lowreqs)
    masterVocab = create_master_vocab(prohigh, prolow)
    highvec = create_vector_rep(masterVocab, prohigh)
    lowvec = create_vector_rep(masterVocab, prolow)
    simmatrix = create_simmatrix(highvec, lowvec)
    result = tracelink(simmatrix, match_type)
    # pp.pprint(result)
    write_output_file(result)
    evaluate(result, validation)

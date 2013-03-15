# Part 1
import sys
from collections import defaultdict
from count_freqs import Hmm

def show_rare(counts_file):
    words_count = defaultdict(int)
    for line in open(counts_file):

        items = line.split()
        if items[1] == "WORDTAG":

            word = items[3]
            count = float(items[0])

            words_count[word] += count

    for word, count in words_count.iteritems():
        if count < 5:
            print word

from sets import Set
def replaceRare(train_file, rare_file):

    rare_words = Set()
    for word in open(rare_file, 'r'):
        rare_words.add(word.strip())

    for line in open(train_file, 'r'):
        items = line.split()

        if len(items) > 0 and items[0] in rare_words:

            items[0] = "_RARE_"
            line = "%s %s" % (items[0], items[1])

        print line

def tag(rare_file, test_file, counts_file):
    hmm = Hmm(3)
    hmm.read_counts(open(counts_file, 'r'))
    print hmm.emission_counts

def usage():
    print """
    1) python simple_tagger.py rare [counts_file] > [rare_file]
    show these words couts < 5

    2) python simple_tagger.py replace [rare_file] [train_file] > [replace_file]
    replace these words in train_file with _RARE_

    3) python simple_tagger.py tag [rare_file] [test_file] [replace_counts_file] > [tag_result_file]
    show the final tagging result
    """

if __name__ == '__main__':

    if len(sys.argv) < 2:
        usage()
        sys.exit(2)

    oper = sys.argv[1]
    if oper == "rare":
        if len(sys.argv) == 3:
            show_rare(sys.argv[2])
        else:
            usage()
            sys.exit(2)

    elif oper == "replace":
        if len(sys.argv) == 4:
            replaceRare(sys.argv[2], sys.argv[3])
        else:
            usage()
            sys.exit(2)
    elif oper == "tag":
        pass
    else:
        usage()
        sys.exit(2)




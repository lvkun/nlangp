# Part 1
import sys
from collections import defaultdict
from count_freqs import Hmm

def show_common(counts_file):
    words_count = defaultdict(int)
    for line in open(counts_file):

        items = line.split()
        if items[1] == "WORDTAG":

            word = items[3]
            count = float(items[0])

            words_count[word] += count

    for word, count in words_count.iteritems():
        if count >= 5:
            print word

from sets import Set
def replaceRare(train_file, common_file):

    common_words = Set()
    for word in open(common_file, 'r'):
        common_words.add(word.strip())

    result = []
    for line in open(train_file, 'r'):
        items = line.strip().split()

        if len(items) > 0 and items[0] not in common_words:

            items[0] = "_RARE_"
            line = "%s %s\n" % (items[0], items[1])

        result.append(line)

    print "".join(result)

def tag(common_file, test_file, counts_file):
    hmm = Hmm(3)
    hmm.read_counts(open(counts_file, 'r'))

    common_words = Set()
    for word in open(common_file, 'r'):
        common_words.add(word.strip())

    total_O_count = 0
    total_GENE_count = 0
    for k,v in hmm.emission_counts.iteritems():
        if k[1] == "O":
            total_O_count += v
        else:
            total_GENE_count += v

    for line in open(test_file, 'r'):
        word = line.strip()

        if len(word) == 0:
            print ""
            continue

        if word not in common_words:
            O_count = hmm.emission_counts[("_RARE_", "O")]
            GENE_count = hmm.emission_counts[("_RARE_", "I-GENE")]
        else:
            O_count = hmm.emission_counts[(word, "O")]
            GENE_count = hmm.emission_counts[(word, "I-GENE")]

        tag = ""
        if O_count/total_O_count > GENE_count/total_GENE_count:
            tag = 'O'
        else:
            tag = 'I-GENE'

        print "%s %s" % (word, tag)


def usage():
    print """
    1) python simple_tagger.py common [counts_file] > [common_file]
    show these words couts >= 5

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
    if oper == "common":
        if len(sys.argv) == 3:
            show_common(sys.argv[2])
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
        if len(sys.argv) == 5:
            tag(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)




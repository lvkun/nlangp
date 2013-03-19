
import sys
from collections import defaultdict
from count_freqs import Hmm


def show_common(counts_file):
    words_count = defaultdict(int)
    for line in counts_file:

        items = line.split()
        if items[1] == "WORDTAG":

            word = items[3]
            count = float(items[0])

            words_count[word] += count

    for word, count in words_count.iteritems():
        if count >= 5:
            print word

from sets import Set
def replace_rare(train_file, common_file):

    common_words = Set()
    for word in common_file:
        common_words.add(word.strip())

    result = []
    for line in train_file:
        items = line.strip().split()

        if len(items) > 0 and items[0] not in common_words:

            items[0] = "_RARE_"
            line = "%s %s\n" % (items[0], items[1])

        result.append(line)

    print "".join(result)

def unigram_tag(common_file, test_file, counts_file):
    hmm = Hmm(3)
    hmm.read_counts(counts_file)

    common_words = Set()
    for word in common_file:
        common_words.add(word.strip())

    total_O_count = 0
    total_GENE_count = 0
    for k,v in hmm.emission_counts.iteritems():
        if k[1] == "O":
            total_O_count += v
        else:
            total_GENE_count += v

    for line in test_file:
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

import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='a simple tagger implement')
    parser.add_argument('action', metavar='action',
                        help="""the action should be performed, possible action:
                        show_common_words replace_rare unigram_tag trigram_tag extend_tag""")
    parser.add_argument('--counts_file', type=argparse.FileType('r'),
                        help="counts result from count_freqs.py")
    parser.add_argument('--common_file', type=argparse.FileType('r'),
                        help="common words (which count >= 5)")
    parser.add_argument('--train_file', type=argparse.FileType('r'),
                        help="tagged file for model training")
    parser.add_argument('--test_file', type=argparse.FileType('r'),
                        help="test file which need to be tagged")

    args = parser.parse_args()

    if args.action == "show_common_words":
        if args.counts_file:
            show_common(args.counts_file)
        else:
            parser.print_usage()

    elif args.action == "replace_rare":
        if args.common_file and args.train_file:
            replace_rare(args.train_file, args.common_file)
        else:
            parser.print_usage()

    elif args.action == "unigram_tag":
        if args.common_file and args.test_file and args.counts_file:
            unigram_tag(args.common_file, args.test_file, args.counts_file)
        else:
            parser.print_usage()


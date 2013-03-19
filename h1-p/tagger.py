
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
        if O_count/hmm.ngram_counts[0][("O",)] > GENE_count/hmm.ngram_counts[0][("I-GENE",)] :
            tag = 'O'
        else:
            tag = 'I-GENE'

        print "%s %s" % (word, tag)

import math

class Tag_Node:

    def __init__(self, word, tag):
        self.word = word
        self.tag = tag
        self.value = 0
        self.prev = None

    def search(self, prev_nodes, hmm):
        if len(prev_nodes) == 0:
            self.value = math.log(self.get_trigram_prob(hmm, "*", "*", self.tag)) + math.log(self.get_emission_prob(hmm))
            return

        max_prev_node = None
        max_value = 0
        for node in prev_nodes:
            curr_value = 0
            if node.prev:
                curr_value = node.value + math.log(self.get_trigram_prob(hmm, node.prev.tag, node.tag, self.tag)) + math.log(self.get_emission_prob(hmm))
            else:
                curr_value = node.value + math.log(self.get_trigram_prob(hmm, "*", node.tag, self.tag)) + math.log(self.get_emission_prob(hmm))

            if curr_value > max_value:
                max_prev_node = node
                max_value = value

        self.prev = max_prev_node
        self.value = max_value

    def get_emission_prob(self, hmm):
        count_word_tag = hmm.emission_counts[(self.word, self.tag)]

        return count_word_tag / hmm.ngram_counts[0][(self.tag,)]

    def get_trigram_prob(self, hmm, yi_2, yi_1, yi):
        trigram_count = hmm.ngram_counts[2][(yi_2, yi_1, yi)]
        bigram_count = hmm.ngram_counts[1][(yi_2, yi_1)]
        return trigram_count / bigram_count

def print_tag_result(node_list):
    print node_list

def create_nodes_from_word(hmm, common_words, word):
    if word not in common_words:
        word = "_RARE_"
    
    ret = []
    for tag in hmm.all_states:
        if hmm.emission_counts[word, tag] > 0:
            ret.append(Tag_Node(word, tag))

    return ret

def trigram_tag(common_file, test_file, counts_file):
    hmm = Hmm(3)
    hmm.read_counts(counts_file)

    common_words = Set()
    for word in common_file:
        common_words.add(word.strip())

    node_list = []
    index = 0
    for line in test_file:
        word = line.strip()

        if len(word) == 0:
            print_tag_result(node_list)
            node_list = []
            continue

        nodes = create_nodes_from_word(hmm, common_words, word)
        prev_nodes = []
        if len(node_list) > 0:
            prev_nodes = node_list[index - 1]

        for node in nodes:
            node.search(prev_nodes, hmm)

        node_list.append(nodes)

    if len(node_list) > 0:
        print_tag_result(node_list)

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a simple tagger implement')
    parser.add_argument('action', metavar='action',
                        help="""the action should be performed, possible action:
                        show_common_words replace_rare replace_rare_extend unigram_tag trigram_tag extend_tag""")
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

    elif args.action == "trigram_tag":
        if args.common_file and args.test_file and args.counts_file:
            trigram_tag(args.common_file, args.test_file, args.counts_file)
        else:
            parser.print_usage()

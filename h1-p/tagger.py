
import sys
from collections import defaultdict
from count_freqs import Hmm

from sets import Set

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

    def __init__(self, word, tag, replace):
        self.word = word
        self.tag = tag
        self.value = 0
        self.prev = None
        self.replace = replace

    def search(self, prev_nodes, hmm):

        #print "self: ", self.word, self.tag
        #print "emission_prob: ", math.log(self.get_emission_prob(hmm))

        if len(prev_nodes) == 0:
            #print "trigram: ", "*", "*", self.tag, math.log(self.get_trigram_prob(hmm, "*", "*", self.tag))
            self.value = math.log(self.get_trigram_prob(hmm, "*", "*", self.tag)) + math.log(self.get_emission_prob(hmm))
            #print ""
            return

        max_prev_node = None
        max_value = 0

        for node in prev_nodes:
            curr_value = 0
            #print "prev node: ", node.word, node.tag, "prev node value: ", node.value

            if node.prev:
                #print "trigram: ", node.prev.tag, node.tag, self.tag, math.log(self.get_trigram_prob(hmm, node.prev.tag, node.tag, self.tag))
                curr_value = node.value + math.log(self.get_trigram_prob(hmm, node.prev.tag, node.tag, self.tag)) + math.log(self.get_emission_prob(hmm))
            else:
                #print "trigram: ", "*", node.tag, self.tag, math.log(self.get_trigram_prob(hmm, "*", node.tag, self.tag))
                curr_value = node.value + math.log(self.get_trigram_prob(hmm, "*", node.tag, self.tag)) + math.log(self.get_emission_prob(hmm))

            if curr_value > max_value or not max_prev_node:
                max_prev_node = node
                max_value = curr_value

        #print "self.prev ", max_prev_node.word, max_prev_node.tag
        self.prev = max_prev_node
        self.value = max_value

        #print ""

    def stop(self, hmm):
        if self.prev:
            self.value += math.log(self.get_trigram_prob(hmm, self.prev.tag, self.tag, "STOP"))
        else:
            self.value += math.log(self.get_trigram_prob(hmm, "*", self.tag, "STOP"))

    def get_emission_prob(self, hmm):

        if self.replace:
            #print "get_emission_prob replace ", self.replace, self.tag, hmm.emission_counts[(self.replace, self.tag)]
            count_word_tag = hmm.emission_counts[(self.replace, self.tag)]
        else:
            count_word_tag = hmm.emission_counts[(self.word, self.tag)]
            #print "get_emission_prob word ", self.word, self.tag, hmm.emission_counts[(self.word, self.tag)]

        #print "get_emission_prob total count: ", self.tag, hmm.ngram_counts[0][(self.tag,)]
        return count_word_tag / hmm.ngram_counts[0][(self.tag,)]

    def get_trigram_prob(self, hmm, yi_2, yi_1, yi):
        trigram_count = hmm.ngram_counts[2][(yi_2, yi_1, yi)]
        bigram_count = hmm.ngram_counts[1][(yi_2, yi_1)]
        return trigram_count / bigram_count

    def print_out(self):
        if self.prev:
            self.prev.print_out()
        print "%s %s" % (self.word, self.tag)

def print_tag_result(node_list, hmm):
    # add STOP tag probability for each node at the end
    list_length = len(node_list)

    if list_length == 0:
        return

    max_node = None
    max_value = 0
    for node in node_list[list_length - 1]:
        node.stop(hmm)

        if node.value > max_value or (not max_node):
            max_value = node.value
            max_node = node

    max_node.print_out()

    # for nodes in node_list:
    #     for node in nodes:
    #         print node.word, node.tag, node.value
    #     print ""
    print ""

def create_nodes_from_word(hmm, common_words, word):
    replace = None
    if word not in common_words:
        replace = "_RARE_"

    ret = []
    for tag in hmm.all_states:
        emission_counts = 0
        if replace:
            emission_counts = hmm.emission_counts[replace, tag]
        else:
            emission_counts = hmm.emission_counts[word, tag]
        if emission_counts > 0:
            ret.append(Tag_Node(word, tag, replace))

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
            print_tag_result(node_list, hmm)
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

import re

def map_rare_word(word):
    
    if re.search("\d+", word):
        return "_Numeric_"

    if word.isalpha() and word.isupper():
        return "_All_Capitals_"

    if word[-1].isupper():
        return "_Last_Capital_"

    return "_RARE_"

def replace_rare_extend(train_file, common_file):

    common_words = Set()
    for word in common_file:
        common_words.add(word.strip())

    result = []
    for line in train_file:
        items = line.strip().split()

        if len(items) > 0 and items[0] not in common_words:

            items[0] = map_rare_word(items[0])
            line = "%s %s\n" % (items[0], items[1])

        result.append(line)

    print "".join(result)

def create_nodes_from_word_extend(hmm, common_words, word):
    replace = None
    if word not in common_words:
        replace = map_rare_word(word)

    ret = []
    for tag in hmm.all_states:
        emission_counts = 0
        if replace:
            emission_counts = hmm.emission_counts[replace, tag]
        else:
            emission_counts = hmm.emission_counts[word, tag]
        if emission_counts > 0:
            ret.append(Tag_Node(word, tag, replace))

    return ret

def extend_tag(common_file, test_file, counts_file):
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
            print_tag_result(node_list, hmm)
            node_list = []
            continue

        nodes = create_nodes_from_word_extend(hmm, common_words, word)
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

    elif args.action == "replace_rare_extend":
        if args.common_file and args.train_file:
            replace_rare_extend(args.train_file, args.common_file)
        else:
            parser.print_usage()

    elif args.action == "extend_tag":
        if args.common_file and args.test_file and args.counts_file:
            trigram_tag(args.common_file, args.test_file, args.counts_file)
        else:
            parser.print_usage()
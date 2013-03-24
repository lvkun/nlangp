
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

def get_common_words(common_file):
    common_words = Set()
    for word in common_file:
        common_words.add(word.strip())
    return common_words

def map_rare_word(word):
    return "_RARE_"

def replace_rare(train_file, common_file, map_rare):

    common_words = get_common_words(common_file)

    for line in train_file:
        items = line.strip().split()

        if len(items) > 0:
            if items[0] not in common_words:
                items[0] = map_rare(items[0])
            print "%s %s" % (items[0], items[1])
        else:
            print ""

class Tagger:

    def __init__(self, common_file, counts_file):
        self.common_words = get_common_words(common_file)
        
        self.hmm = Hmm(3)
        self.hmm.read_counts(counts_file)

class Unigram_Tagger(Tagger):

    def tag(self, test_file):
        for line in test_file:
            word = line.strip()

            if len(word) == 0:
                print ""
                continue

            if word not in self.common_words:
                O_count = self.hmm.emission_counts[("_RARE_", "O")]
                GENE_count = self.hmm.emission_counts[("_RARE_", "I-GENE")]
            else:
                O_count = self.hmm.emission_counts[(word, "O")]
                GENE_count = self.hmm.emission_counts[(word, "I-GENE")]

            tag = ""
            if O_count/self.hmm.ngram_counts[0][("O",)] > GENE_count/self.hmm.ngram_counts[0][("I-GENE",)] :
                tag = 'O'
            else:
                tag = 'I-GENE'

            print "%s %s" % (word, tag)


import math

class Trigram_Tagger(Tagger):

    def begin_tag(self):
        self.pi = defaultdict(float)
        self.pi[(-1, "*", "*")] = 1.0
        self.bp = defaultdict(str)
        self.words = []

        self.index = -1

    def tag(self, test_file):

        self.begin_tag()

        for line in test_file:
            word = line.strip()

            if len(word) == 0:
                self.print_out()
                self.begin_tag()

            self.add_word(word)

    def states(self, k):

        if k < 0:
            return ["*"]

        return self.hmm.all_states

    def add_word(self, word):
        self.index += 1
        self.words.append(word)

        for u in self.states(self.index - 1):
            for v in self.states(self.index):

                max_value = None
                max_tag = None
                for w in self.states(self.index - 2):

                    value = self.pi[(self.index - 1, w, u)] + self.trigram_prob(w, u, v) + self.emission(self.words[self.index], v) 

                    if max_value and value > max_value:
                        max_value = value
                        max_tag = w

                self.pi[(self.index, u, v)] = max_value
                self.bp[(self.index, u, v)] = w

    def print_out(self):
        # consider "stop" tag

        tags = [""] * (self.index + 1)
        max_value = None

        for u in self.states(self.index - 1):
            for v in self.states(self.index):

                value = self.pi[(self.index, u, v)] + self.trigram_prob(u, v, "STOP")

                if max_value and value > max_value:
                    tags[-1] = v # yn
                    tags[-2] = u # yn-1
                    max_value = value

        
        for i in xrange(self.index - 2, 0, -1):
            tags[i] = self.bp[(i + 2, tags[i+1], tags[i+2])]



    def emission(self, word, tag):
        return 0

    def trigram_prob(self, yi_2, yi_1, yi):
        return 0


import re

def map_rare_word_extend(word):

    if re.search("\d+", word):
        return "_Numeric_"

    if word.isalpha() and word.isupper():
        return "_All_Capitals_"

    if word[-1].isupper():
        return "_Last_Capital_"

    return "_RARE_"

class Extend_Tagger(Trigram_Tagger):

    def map_word(self, word):
        return map_rare_word_extend(word)

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
            replace_rare(args.train_file, args.common_file, map_rare_word)
        else:
            parser.print_usage()

    elif args.action == "unigram_tag":
        if args.common_file and args.test_file and args.counts_file:
            tagger = Unigram_Tagger(args.common_file, args.counts_file)
            tagger.tag(args.test_file)
        else:
            parser.print_usage()

    elif args.action == "trigram_tag":
        if args.common_file and args.test_file and args.counts_file:
            tagger = Trigram_Tagger(args.common_file, args.counts_file)
            tagger.tag(args.test_file)
        else:
            parser.print_usage()

    elif args.action == "replace_rare_extend":
        if args.common_file and args.train_file:
            replace_rare(args.train_file, args.common_file, map_rare_word_extend)
        else:
            parser.print_usage()

    elif args.action == "extend_tag":
        if args.common_file and args.test_file and args.counts_file:
            tagger = Extend_Tagger(args.common_file, args.counts_file)
            tagger.tag(args.test_file)
        else:
            parser.print_usage()

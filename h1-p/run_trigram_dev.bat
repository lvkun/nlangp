set PATH=C:\Python27\;%PATH%

python count_freqs.py gene.train > gene.counts

python tagger.py show_common_words --counts_file=gene.counts > gene.common

python tagger.py replace_rare --train_file=gene.train --common_file=gene.common > gene.replace

python count_freqs.py gene.replace > gene.replace.counts

python tagger.py trigram_tag --common_file=gene.common --test_file=gene.dev --counts_file=gene.replace.counts > gene_dev.p2.out

python eval_gene_tagger.py gene.key gene_dev.p2.out
set PATH=C:\Python27\;%PATH%

python count_freqs.py gene.train > gene.counts
python unigram_tagger.py common gene.counts > gene.common
python unigram_tagger.py replace gene.train gene.common > gene.replace
python count_freqs.py gene.replace > gene.replace.counts
python unigram_tagger.py tag gene.common gene.test gene.replace.counts > gene_test.p1.out
python eval_gene_tagger.py gene.key gene_test.p1.out
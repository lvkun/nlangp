set PATH=C:\Python27\;%PATH%

python count_freqs.py gene.train > gene.counts
python simple_tagger.py common gene.counts > gene.common
python simple_tagger.py replace gene.train gene.common > gene.replace
python count_freqs.py gene.replace > gene.replace.counts
python simple_tagger.py tag gene.common gene.dev gene.replace.counts > gene.dev.p1.out
python eval_gene_tagger.py gene.key gene.dev.p1.out
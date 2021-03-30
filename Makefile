.PHONY: data step1 events networks

DTMAX = 1 2 4 8 16 32 64 128 256 512
COOCCURRENCEFILES = $(patsubst %,networks/%/cooccurrences.pkl,$(DTMAX))

data: step1 step2 step3

step1: data/1-import/zip-data.pkl data/1-import/csv-data.pkl

step2: data/2-merge/data.pkl

step3: data/3-process/data.pkl

data/1-import/zip-data.pkl:
	python src/data/make_zip_dataset.py data/0-raw/zip/ $@

data/1-import/csv-data.pkl:
	python src/data/make_csv_dataset.py data/0-raw/csv $@

data/2-merge/data.pkl: data/1-import/csv-data.pkl data/1-import/zip-data.pkl
	python src/data/merging.py --csv_file $< --zip_file $(word 2,$^) --out $@

data/3-process/data.pkl: data/2-merge/data.pkl
	python src/data/clean.py $< $@

src/teexgraph/teexgraph:
	cd src/teexgraph && make listener

networks/%: 
	mkdir $@

networks/%/cooccurrences.pkl: data/3-process/data.pkl networks/%
	python -m src.network.determine_random_systematic $< $@ --dt_max $*

networks: $(COOCCURRENCEFILES)
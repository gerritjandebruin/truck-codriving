.PHONY: data step1 events networks

OBJECTS = 1 2 4 8 16 32 64 128 256 512
OBJ_DIR = $(patsubst %,networks/%,$(OBJECTS))
COOCCURRENCEFILES = $(patsubst %,networks/%/giant_component.pkl,$(OBJECTS))

.PHONY : data
data: step1 step2 step3

.PHONY: step1
step1: data/1-import/zip-data.pkl data/1-import/csv-data.pkl

.PHONY: step2
step2: data/2-merge/data.pkl

.PHONY: step3
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

networks/%/cooccurrences.pkl: data/3-process/data.pkl | networks/%/
	python -m src.network.cooccurrence $< $@ networks/$*/randoms.pkl --dt_max $*

networks/%/graph.pkl: networks/%/cooccurrences.pkl
	python -m src.network.network $< $@

networks/%/giant_component.pkl: networks/%/graph.pkl
	python -m src.network.giant_component $< $@

networks/%/:
	mkdir -p $@

networks: $(COOCCURRENCEFILES)
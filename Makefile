OBJECTS = 1 2 4 8 16 32 64 128 256 512
OBJ_DIR = $(patsubst %,networks/%,$(OBJECTS))
OBJ_GIANT_COMPONENT = $(patsubst %,networks/%/giant_component.pkl,$(OBJECTS))
OBJ_GRAPH = $(patsubst %,networks/%/graph.pkl,$(OBJECTS))
OBJ_COOCCURRENCES = $(patsubst %,networks/%/cooccurrences.pkl,$(OBJECTS))

all: data networks

## clean		: Clean pycache directories.
clean:
	find . -name '__pycache__' -exec rm -fr {} +

## data 	  : Process raw data.
.PHONY : data
data: data/3-process/data.pkl

data/1-import/zip-data.pkl:
	python src/data/make_zip_dataset.py data/0-raw/zip/ $@

data/1-import/csv-data.pkl:
	python src/data/make_csv_dataset.py data/0-raw/csv $@

data/2-merge/data.pkl: data/1-import/csv-data.pkl data/1-import/zip-data.pkl
	python src/data/merging.py --csv_file $< --zip_file $(word 2,$^) --out $@

data/3-process/data.pkl: data/2-merge/data.pkl
	python src/data/clean.py $< $@

## networks	: Construct networks for various values of delta_t_max
.PHONY: networks
networks: $(OBJ_DIR) $(OBJ_GIANT_COMPONENT) $(OBJ_GRAPH) $(OBJ_COOCCURRENCES) 

networks/%/:
	mkdir -p $@

# This rule creates also the randoms.pkl
networks/%/cooccurrences.pkl: data/3-process/data.pkl | networks/%/
	python -m src.network.cooccurrence $< $@ networks/$*/randoms.pkl --dt_max $*

networks/%/graph.pkl: networks/%/cooccurrences.pkl
	python -m src.network.network $< $@

networks/%/giant_component.pkl: networks/%/graph.pkl
	python -m src.network.giant_component $< $@

## teexgraph: Install teexgraph
.PHONY : teexgraph
teexgraph: src/teexgraph/teexgraph

src/teexgraph/teexgraph:
	cd src/teexgraph && make listener
OBJECTS = 1 2 4 8 16 32 64 128 256 512
OBJ_DIR = $(patsubst %,networks/%,$(OBJECTS))
OBJ_GRAPH = $(patsubst %,networks/%/graph.pkl,$(OBJECTS))
OBJ_COOCCURRENCES = $(patsubst %,networks/%/cooccurrences.pkl,$(OBJECTS))

OBJ_GIANT_COMPONENT = $(patsubst %,networks/%/giant_component.pkl,$(OBJECTS))
OBJ_DISTANCE_DISTRIBUTION = $(patsubst %,networks/%/distance_distribution.txt,$(OBJECTS))

all: data networks networkanalysis

## clean          : Clean pycache directories.
PHONY: clean
clean:
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.ipynb_checkpoints' -exec rm -fr {} +

## remove_intermediate: Remove all intermediate files.
PHONY: remove_intermediate
remove_intermediate:
	rm data/1-import/* data/2-merge/data.pkl data/3-process/* models/*.* networks/*.*

## help           : Show this message.
PHONY: help
help:           
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

## data           : Process raw data.
.PHONY : data
data: data/3-process/data.pkl data/3-process/rdw.pkl

data/1-import/zip-data.pkl:
	python src/data/make_zip_dataset.py data/0-raw/zip/ $@

data/1-import/csv-data.pkl:
	python src/data/make_csv_dataset.py data/0-raw/csv $@

data/2-merge/data.pkl: data/1-import/csv-data.pkl data/1-import/zip-data.pkl
	python src/data/merging.py --csv_file $< --zip_file $(word 2,$^) --out $@

data/3-process/data.pkl: data/2-merge/data.pkl
	python src/data/clean.py $< $@

data/3-process/rdw.pkl: data/0-raw/other/rdw1.csv data/0-raw/other/rdw2.csv
	python -m src.data.make_rdw_dataset $^ $@

## networks       : Construct networks for various values of delta_t_max
.PHONY: networks
networks: $(OBJ_DIR) $(OBJ_GRAPH) $(OBJ_COOCCURRENCES) 

networks/%/:
	mkdir -p $@

# This rule creates also the randoms.pkl
networks/%/cooccurrences.pkl: data/3-process/data.pkl | networks/%/
	python -m src.network.cooccurrence $< $@ networks/$*/randoms.pkl --dt_max $*

networks/%/graph.pkl: networks/%/cooccurrences.pkl
	python -m src.network.network $< $@

## networkanalysis: Calculate giant_component and distance_distribution for all networks and attributes for dt_max = 8s
.PHONY: networkanalysis
networkanalysis: $(OBJ_GIANT_COMPONENT) $(OBJ_DISTANCE_DISTRIBUTION) networks/8/dutch_graph_attributes.pkl networks/8/graph_attributes.pkl
networks/%/giant_component.pkl: networks/%/graph.pkl
	python -m src.network.giant_component $< $@

networks/%/distance_distribution.txt: networks/%/giant_component.pkl
	python -m src.network.distance_distribution $< $@

networks/8/dutch_graph_attributes.pkl: networks/8/graph.pkl data/3-process/data.pkl data/3-process/rdw.pkl
	python -m src.network.attributes $< $(word 2,$^) --type dutch --rdw $(word 3,$^) -o $@

networks/8/graph_attributes.pkl: networks/8/graph.pkl data/3-process/data.pkl
	python -m src.network.attributes $^ --type full -o $@

## teexgraph: Install teexgraph
.PHONY : teexgraph
teexgraph: src/teexgraph/teexgraph

src/teexgraph/teexgraph:
	cd src/teexgraph && make listener

## reports: Make reports
.PHONY : reports
reports/Fig1.pdf: data/3-process/data.pkl
	python -m src.visualization.Figure1 $< $@
    
## model1: Entire pipeline for model 1
.PHONY : model1
model1: models/1/graph_tau.pkl models/1/examples.npy models/1/targets.npy models/1/features.pkl models/1/gridsearch.pkl

## model2: Entire pipeline for model 2
.PHONY : model2
model2: models/2/graph_tau.pkl models/2/examples.npy models/2/targets.npy models/2/features.pkl models/2/gridsearch.pkl

models/%/graph_tau.pkl: networks/8/cooccurrences.pkl models/%/configuration.json
	python -m src.link_prediction.get_graph_tau $^ $@

models/%/examples.npy: models/%/graph_tau.pkl models/%/configuration.json
	python -m src.link_prediction.get_examples $^ $@
 
models/%/targets.npy: networks/8/graph.pkl models/%/examples.npy
	python -m src.link_prediction.get_targets $^ $@
 
models/%/features.pkl: models/%/graph_tau.pkl data/3-process/data.pkl models/%/examples.npy
	python -m src.link_prediction.get_features $^ $@

# Grouped targets & automatic variable does not work.
models/1/xtrain.pkl models/1/xtest.pkl models/1/ytrain.npy models/1/ytest.npy &: models/1/features.pkl models/1/targets.npy
	python -m src.link_prediction.get_split $^ models/2/xtrain.pkl models/2/xtest.pkl models/2/ytrain.npy models/2/ytest.npy

models/2/xtrain.pkl models/2/xtest.pkl models/2/ytrain.npy models/2/ytest.npy &: models/2/features.pkl models/2/targets.npy
	python -m src.link_prediction.get_split $^ models/2/xtrain.pkl models/2/xtest.pkl models/2/ytrain.npy models/2/ytest.npy

models/3/xtrain.pkl models/3/xtest.pkl models/3/ytrain.npy models/3/ytest.npy &: models/3/features.pkl models/3/targets.npy
	python -m src.link_prediction.get_split $^ models/3/xtrain.pkl models/3/xtest.pkl models/3/ytrain.npy models/3/ytest.npy

models/%/gridsearch.pkl: models/%/xtrain.pkl models/%/ytrain.npy
	python -m src.link_prediction.gridsearch $^ $@

models/%/performance.pkl: models/%/xtrain.pkl models/%/xtest.pkl models/%/ytrain.npy models/%/ytest.npy
	python -m src.link_prediction.learn $^ $@
.PHONY: data step1 events networks

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

networks: data/3-process/data.pkl
	python src/network/make_networks.py $< networks/ -dt 1 -dt 2 -dt 4 -dt 8 -dt 16 -dt 32 -dt 64 -dt 128 -dt 256 -dt 512
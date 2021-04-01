# Understanding Behavioral Patterns in Truck Co-driving Networks
This repository provides the code used in the following publication:
> Bruin G.J.., Veenman C.J., van den Herik H.J., Takes F.W. (2019) Understanding Behavioral Patterns in Truck Co-driving Networks. In: Aiello L., Cherifi C., Cherifi H., Lambiotte R., Lió P., Rocha L. (eds) Complex Networks and Their Applications VII. COMPLEX NETWORKS 2018. Studies in Computational Intelligence, vol 813. Springer, Cham. https://doi.org/10.1007/978-3-030-05414-4_18

## Organization

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make help`, `make data`, `make networks` and `make networkanalysis`
    ├── README.md          <- This file
    ├── data
    │   ├── 0-raw          <- The original, immutable data dump.
    │   ├── 1-import       <- After importing
    │   ├── 2-merged       
    │   └── 3-process      <- Fully cleaned data
    ├── networks           <- Networks obtained for various values of delta_t
    ├── notebooks          <- Notebooks used for exploratory data analysis and figures.
    │   └── 03-gj-figures.ipynb <- Generated graphics and figures to be used in reporting    
    ├── reports            <- Generated figures
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   ├── data           <- Scripts to download or generate data
    │   ├── networks       <- Scripts to create and process network
    │   ├── progress_parallel <- Convenient class for parallel programming
    │   └── teexgraph      <- Package to analyze distance distribution, compile with `make teexgraph`
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    └── environment.yml    <- Packages used in this work

## Contact
Please e-mail me at g.j.de.bruin@liacs.leidenuniv.nl.
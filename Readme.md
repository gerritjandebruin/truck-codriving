# Understanding Behavioral Patterns in Truck Co-driving Networks
This repository provides the code used in the following publication:
> Bruin G.J.., Veenman C.J., van den Herik H.J., Takes F.W. (2019) Understanding Behavioral Patterns in Truck Co-driving Networks. In: Aiello L., Cherifi C., Cherifi H., Lambiotte R., Lió P., Rocha L. (eds) Complex Networks and Their Applications VII. COMPLEX NETWORKS 2018. Studies in Computational Intelligence, vol 813. Springer, Cham. https://doi.org/10.1007/978-3-030-05414-4_18

## Organization

    ├── LICENSE
    ├── Makefile           <- Run `make help` to see all available commands
    ├── README.md          <- This file
    ├── data
    │   ├── 0-raw          <- The original, immutable data dump.
    │   ├── 1-import       <- After importing
    │   ├── 2-merged       
    │   └── 3-process      <- Fully cleaned data
    ├── models             <- Models used in link prediction. See configuration.json of each.
    │   ├── 1          
    │   ├── 2
    │   └── 3       
    ├── networks           <- Networks obtained for various values of delta_t
    ├── notebooks          <- Notebooks used for exploratory data analysis and figures.
    │   ├── 02-reports-cn2018.ipynb <- Generated graphics and figures in reports/cn2018
    |   └── 04-reports-cn2019.ipynb <- Generated graphics and figures in reports/cn2019
    ├── reports            <- Generated figures
    │   ├── cn2018         <- Generated graphics and figures in reports/cn2018
    |   └── cn2019         <- Generated graphics and figures in reports/cn2019
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
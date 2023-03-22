# Data Analysis: Statistical Modelling and Computation in Applications

This repository contains the course work for the MITx course `Data Analysis: Statistical Modelling and Computation in Applications`. The material is separated by module with each one covering a different topic:

- Module 0: Practice, Grading and Other
- Module 1: Review
- Module 2: Genomics and High Dimensional Data

Inside each module, you will find a notebook for each of the lectures found in the course. You will also find a folder called `Project` which contains the last assignment for each module. You can also tend to find a `Recitation` folder, which should contain all of the content for the recitation sessions of the module, in case there was one.

## Usage

Most of the material is written in either Jupyter notebooks (`ipynb`) or R scripts. All the Jupyter notebook dependencies can be installed by running the command `poetry install` after installing poetry in python (`pip install poetry`).

The only exception to this rule is the `graphviz` package, which needs additional steps to be installed. You can find the instructions [here](https://pygraphviz.github.io/documentation/stable/install.html) but in windows you need to first install graphviz with chocolatey `choco install graphviz` and then run the pip installation.

None of the data used to generate the results is included in the repository, both for space and privacy reasons. The data can be downloaded from the course website.

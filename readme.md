# Introduction

A Python implementation utilising an LP-Solver to solve the Shannon Entropy and Fractional Clique Cover Number problems for an input graph.

# Usage

The program requires the installation of two python pip packages. Run the following command
to install them:

```bash
pip3 install networkx ortools
```

 ##Running the program

Run the linear optimisation solver program with the following command in a terminal.
Replace `filename.txt' and `optional filename.txt' with your own input text file and optional
name of the file to save the output of the program to. Each line of the text file starts with a
node number followed by the nodes numbers that it shares edges with (delimited with spaces).
There is no limit to the number of nodes that can be in the graph. A simple graph is generated
within the program accordingly to be used in the calculation. This type of graph is undirected,
contains no loops and has an edge weight of 1.

Example input text file for the
complete graph K4
```bash
1 2 3 4
2 1 3 4
3 1 2 4
4 1 2 3
```

```
python3 Solver.py filename.txt optional_filename.txt
```

The program will print to the console the rational answers to the two optimisation problems
outlined in parts one and two of the assignment. If the optional output filename is given, a text
file will be generated containing the input graph and the rational solutions to both LPs.

The program will exit if there is an error reading from the input file, or if the input file is not
provided.
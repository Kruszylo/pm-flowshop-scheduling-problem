# Parallel-machine flowshop scheduling problem

This project requires **IBM ILOG CPLEX Optimization Studio 12.8.0**

(https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.studio.help/Optimization_Studio/topics/COS_relnotes_intro.html)

## Description 
The first line contains two numbers m and n, the first of which is the number of tasks and the second one is the number of machines. In the following lines there is a description of m tasks (machine number, time of execution on this machine). We assume the prefix dependency according to the order of the definition of the operation

We assume that the machines from 0-4 have k copies and the remaining 1 copy, where k is from 1 to 5 and is given as a parameter for running the program.

The aim is to minimize the end of the last operation.

To run the program:
```
titov.py path_to_folder_with_input_data -k
```
The command is to run the program on all files in the input folder `train` and return the file describing the solution to everyone. The last parameter denotes the number of machines no. 0-4.
### Output file format
For a given set, n lines should be returned, each of which describes the sequence of tasks performed on a given machine (job number, start time) written out in ascending order of start times (each number is separated by a space). In the last line n+1 enter the value of the macespan and the time of program execution (I know that the time depends on the computer).

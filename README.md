# About

**Under construction**

This is a personal learning project where I implemented a [CDCL](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning) based [SAT-solver](https://en.wikipedia.org/wiki/SAT_solver) with [2-watched literals](https://www.youtube.com/watch?v=n3e-f0vMHz8). 
For parsing logical formulas, the project also implements a [recursive descent parser](https://www.cs.rochester.edu/u/nelson/courses/csc_173/grammars/parsing.html) for propositional logic. 
As an application of the SAT-solver, the project includes an automatic sudoku solver.
In addition to checking if a given formula is satisfiable, the CDCL solver also builds a [resolution proof](https://en.wikipedia.org/wiki/Resolution_(logic)) if the formula is not satisfiable.

The file `background.pdf` gives a more detailed explanation of the theoretical background and an overview of the CDCL algorithm.

# Basic usage
To check the satisfiability of an arbitrary formula, run `python3 main.py formula '<formula>'` where `<formula>` is the given formula (see below for the syntax of formulas). 
For example: `python3 main.py formula '(a -> b) & a -> b'`.

To check the satisfiability of a CNF (conjunctive normal form) formula given as a DIMACS CNF file, run 
`python3 main.py cnf <file>` where `<file>` is the name of the file (see below for more about the file format). 
For example: `python3 main.py cnf hole6.cnf`

To solve a sudoku, run 
`python3 main.py sudoku <file>` where `<file>` is the given sudoku file (see below for more about the file format).
For example: `python3 main.py sudoku sudoku_example.txt`

# Installing/Running
Download all files into the same directory and run your python interpreter with arguments as shown above. The only dependency is the standard python library.

# Syntax of formulas
When giving propositional formulas as input, the following syntax is assumed.
- Variables can be any alphabetic characters **except** `v`, `T` and `F`. To create longer variable symbols, a string  can be enclosed inside square brackets, e.g. `[some text]`.
- The letter `T` is used for the atomic formula "True", and `F` is used for the atomic formula "False".
- Logical connectives are:
  - `<->` equivalence (if and only if)
  - `->`  implication (if then)
  - `v`   disjunction (or)
  - `&`   conjunction (and)
  - `~`   negation (not)
- Formulas can be grouped with parenthesis `( )`.
- The following precedence is assumed (from lowest to highest): equivalence, implication, disjunction, conjunction, negation, parenthesis. For example, `a -> b <-> ~c v a & b` is parsed as `(a -> b) <-> (~c v (a & b))`.
- The binary connectives are left associative. For example, `a & b & c` is parsed as `(a & b) & c`.

Some examples of formulas: 
- `[it has rained] -> [ground is wet] <-> ~[ground is wet] -> ~[it has rained]`
- `(A -> T) -> (~A -> F)`
- `(A <-> ~~A) -> [unconstructive!]`
- `[X = 100] -> [X != 101]`

If the given formula does not match this syntax, a scanning/parsing error is raised and the first occurrence of an error is highlighted.

For example, `python3 main.py formula 'a -> b & <-> c'` outputs 
```
Parsing error!
Expected '(', VAR, '~', 'T' or 'F' but got '<->' instead. 

a -> b & <-> c  
         ^  
```
# DIMACS CNF files
When given a CNF DIMACS file, the file is assumed to follow the following format.
- Each line starts with either `p`, `c`, `-` or a digit.
- Lines starting with `c` are comments, and lines starting with `p` are the "problem lines" that record, for example, the size of the problem. Lines starting with `c` and `p` are optional.
- The other lines represent clauses. Each such line consists of integers separated by spaces where the integers represent literals. Positive integers represent variables and negative integers represent negations of variables.
- Each clause line ends with a `0` representing the end of the clause (these are not strictly necessary in this project).
 In this project, **each clause needs be on one line** and **no two clauses can be on the same line**.

The file `hole6.cnf` shows an example of such a file.

# Sudoku files
When given a sudoku file, the file is assumed to be a plain text file that uses the following format.
- The file has exactly 9 lines and each line has exactly 9 characters.
- Each character is either `.`, which represents an empty square, or a digit 1-9, which represents the fixed number in the corresponding square.

The file `sudoku_example.txt` gives an example of such a file.


# Further details
Tseitin set, subformula labels, resolution proof, etc.



# References
- https://users.aalto.fi/~tjunttil/2022-DP-AUT/notes-sat/index.html
- https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
- https://www.cs.princeton.edu/~zkincaid/courses/fall18/readings/SATHandbook-CDCL.pdf
- https://kienyew.github.io/CDCL-SAT-Solver-from-Scratch/
- https://craftinginterpreters.com/introduction.html


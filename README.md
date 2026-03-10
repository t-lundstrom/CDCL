# About

**Under construction**

This is a personal learning project where I implemented a [CDCL](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning) based [SAT-solver](https://en.wikipedia.org/wiki/SAT_solver) with [2-watched literals](https://www.youtube.com/watch?v=n3e-f0vMHz8). For parsing logical formulas, the project also implements a [recursive descent parser](https://www.cs.rochester.edu/u/nelson/courses/csc_173/grammars/parsing.html) for propositional logic. As an application of the SAT-solver, the project includes an automatic sudoku solver. In addition to checking if a given formula is satisfiable, the CDCL solver also builds a [resolution proof](https://en.wikipedia.org/wiki/Resolution_(logic)) if the formula is not satisfiable.

The file `background.pdf` gives a more detailed explanation of the theoretical background.

# Basic usage
three things you can do
## Arbitrary formulas
To check the satisfiability of an arbitrary formula: `python3 main.py formula '<formula>'` where `<formula>` is the given formula (see below for the syntax of formulas).
  
**Example**: `python3 main.py formula '(a -> b) & a -> a'`.


## CNF files
To check the satisfiability of a CNF (conjunctive normal form) formula given as a DIMACS file: `python3 main.py cnf <file>` where `<file>` is the name of the file (see below for the file format).

**Example**: `python3 main.py cnf hole6.cnf`

## Sudokus
To solve a sudoku: `python3 main.py sudoku <file>` where `<file>` is the given sudoku file (see below for the file format)

**Exampl**e: `python3 main.py sudoku sudoku_example.txt`

# Installing/Running
Download all files into a directory and run your python interpreter with arguments as shown above. The only dependency is the standard python library.

# Syntax for formulas
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

If the given formula does not match this syntax, a scanning/parsing error occurs and the first occurrence of an error is highlighted.

**Example:** `python3 main.py formula 'a -> b & <->'` outputs 
```
Parsing error!
Expected '(', VAR, '~', 'T' or 'F' but got '<->' instead. 

a -> b & <->  
         ^ 
```


# Further details




# References
- https://users.aalto.fi/~tjunttil/2022-DP-AUT/notes-sat/index.html
- https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
- https://www.cs.princeton.edu/~zkincaid/courses/fall18/readings/SATHandbook-CDCL.pdf
- https://kienyew.github.io/CDCL-SAT-Solver-from-Scratch/
- https://craftinginterpreters.com/introduction.html


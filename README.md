# About
This is a personal learning project where I implemented a [CDCL](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning) based [SAT-solver](https://en.wikipedia.org/wiki/SAT_solver) with [2-watched literals](https://www.youtube.com/watch?v=n3e-f0vMHz8). For parsing logical formulas, the project also implements a [recursive descent parser](https://www.cs.rochester.edu/u/nelson/courses/csc_173/grammars/parsing.html) for propositional logic. As an application of the SAT-solver, the project includes an automatic sudoku solver.

# Basic features
Depending on the shell you're using, you may want to enclose the formula in single quotes `' '` instead of double quotes `" "`.

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
- `(A -> T) -> (~B -> F)`
- `(A <-> ~~A) -> [unconstructive!]`
- `[X = 100] -> [X != 101]`


# References
- https://users.aalto.fi/~tjunttil/2022-DP-AUT/notes-sat/index.html
- https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
- https://www.cs.princeton.edu/~zkincaid/courses/fall18/readings/SATHandbook-CDCL.pdf
- https://kienyew.github.io/CDCL-SAT-Solver-from-Scratch/
- https://craftinginterpreters.com/introduction.html


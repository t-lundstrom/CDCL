import random
from parser import Atomic, Binary, Unary, TokenType, ParseError, split_into_tokens, Parser
from cdcl import cdcl


def syntax_tree_to_string(node):
    # We turn the given syntax tree into the corresponding formula with all parenthesis.
    # The purpose of this function is to map a syntax tree into a string in an injective way
    # so that syntax trees can be used as keys in dictionaries.
    if type(node) == Atomic:
        return node.symbol
    
    if type(node) == Unary:
        return node.connective_token.lexeme + syntax_tree_to_string(node.child)
    
    if type(node) == Binary:
        return "(" + syntax_tree_to_string(node.left) + node.connective_token.lexeme + syntax_tree_to_string(node.right) + ")"


class Counter:
    def __init__(self,start):
        self.number = start

    def next(self):
        i = self.number
        self.number += 1
        return i    

def label_subformulas(node,subformula_labels,counter):
    # Gives a unique label (integer) to each subformula
    tree_as_string = syntax_tree_to_string(node) # turns the syntax tree into a unique string, to be used as a key for the dictionary

    # the atomic formulas 'T' and 'F' have these characters as their labels
    if type(node) == Atomic and node.atomtype == TokenType.TRUE:
        subformula_labels[tree_as_string] = 'T' 

    elif type(node) == Atomic and node.atomtype == TokenType.FALSE:
        subformula_labels[tree_as_string] = 'F' 

    elif type(node) == Atomic and node.atomtype == TokenType.VAR and node.symbol not in subformula_labels.keys():
        subformula_labels[tree_as_string] = counter.next() # variables get assigned a number

    elif type(node) == Unary and tree_as_string not in subformula_labels.keys():
        subformula_labels[tree_as_string] = counter.next() # subformulas get assigned a number
        label_subformulas(node.child,subformula_labels,counter)

    elif type(node) == Binary and tree_as_string not in subformula_labels.keys():
        subformula_labels[tree_as_string] = counter.next() # subformulas get assigned a number
        label_subformulas(node.left,subformula_labels,counter)
        label_subformulas(node.right,subformula_labels,counter)
 
            

def tseitin_set_and_labels(syntax_tree):
    # Input: syntax tree of a propositional formula
    # Output: the Tseitin set of the formula together with dictionary 'subformula_labels' 
    # that gives the label (i.e. integer or T/F) for each subformula.
    counter = Counter(1)
    subformula_labels = {}
    label_subformulas(syntax_tree,subformula_labels,counter)
    
    tseitin_set = []
    code_for_whole_formula = subformula_labels[syntax_tree_to_string(syntax_tree)]
    tseitin_set.append([code_for_whole_formula])
    compute_tseitin_set(syntax_tree,tseitin_set,subformula_labels)
    
    return tseitin_set,subformula_labels

def opposite(x):
    if type(x) == int:
        return -x
    elif x == 'T':
        return 'F'
    elif x == 'F':
        return 'T'

def compute_tseitin_set(node,tseitin_set,subformula_labels):
    # Computes the tseitin set from the syntax tree 'node'
    if type(node) == Atomic:
        return # we don't create clauses from atomic formulas
    
    elif type(node) == Unary:
        # The case for negation
        # 'node' is the syntax tree of a formula of the form ~C  for some formula C
        a = subformula_labels[syntax_tree_to_string(node)] # code for ~C
        b = subformula_labels[syntax_tree_to_string(node.child)] # code for C
        a_op = opposite(a)
        b_op = opposite(b)
        
        tseitin_set.append([a,b])
        tseitin_set.append([a_op,b_op])
        compute_tseitin_set(node.child,tseitin_set,subformula_labels)
        return 

    elif type(node) == Binary:
        # 'node' is the syntax_tree of a formula of the form C1 * C2  for some formulas C1 and C2 and binary connective *
        a  = subformula_labels[syntax_tree_to_string(node)] # code for C1 * C2
        c1 = subformula_labels[syntax_tree_to_string(node.left)] # code for C1
        c2 = subformula_labels[syntax_tree_to_string(node.right)] # code for C2
        a_op  = opposite(a)
        c1_op = opposite(c1)
        c2_op = opposite(c2)

        match node.connective_token.tokentype:
            case TokenType.DISJ:
                tseitin_set.append([a_op,c1,c2])
                tseitin_set.append([a,c1_op])
                tseitin_set.append([a,c2_op])
            
            case TokenType.CONJ:
                tseitin_set.append([a_op,c1])
                tseitin_set.append([a_op,c2])
                tseitin_set.append([a,c1_op,c2_op])

            case TokenType.IMPLY:
                tseitin_set.append([a_op,c1_op,c2])
                tseitin_set.append([a,c1])
                tseitin_set.append([a,c2_op])
            
            case TokenType.EQUIV:
                tseitin_set.append([a_op,c1,c2_op])
                tseitin_set.append([a_op,c1_op,c2])
                tseitin_set.append([a,c1,c2])
                tseitin_set.append([a,c1_op,c2_op])
        
        compute_tseitin_set(node.left,tseitin_set,subformula_labels)
        compute_tseitin_set(node.right,tseitin_set,subformula_labels)

        return


def random_clauses(max_number_of_clauses,max_number_of_variables,min_size_of_clause,max_size_of_clause):
    # Random clauses used for testing
    clauses = []
    for i in range(max_number_of_clauses):
        clause = []
        number_of_literals_in_clause = random.randrange(min_size_of_clause,max_size_of_clause +1)
        for j in range(number_of_literals_in_clause):
            variable = random.randrange(1,max_number_of_variables+1)
            sign = random.choice([-1,1])
            clause.append(sign * variable)
        
        clauses.append(clause)

    return clauses

def clauses_from_dimacs(filename):
    # Constructs clauses from a given dimacs file.
    # We assume that the given file has clauses on their own lines,
    # each clause line ends with a 0, and 
    # and that every line starts with either 'c', 'p', '-' or a digit.
    clauses = []
    with open(filename,'r') as file:
        for line in file:
            words = line.split() # use whitespace to split the line into a list of words
            if len(words) > 0 and words[0][0] not in ['p','c']: 
                clause = [int(k) for k in words if int(k) != 0]
                clauses.append(clause)
    
    return clauses


def solve_sudoku(sudoku_file):
    # We assume that the given file uses the following format:
    # Each line in the file is 9 characters long and there are exactly 9 lines in the file.
    # Each character is either a dot . or a digit 1-9.
    # Dots represent empty squares.
    # If the file does not follow this format exactly, errors might occur.
    
    n = 9 # In theory, we could also solve n x n sudokus where n = d^2 is the side length of the board and d is the side length of each box. 
    d = 3 # We'll keep these hard-coded for now.
    clauses = []
    variables = {} # keys: tuples (i,j,k). Values: integers representing the corresponding variable x_{i,j,k}
    # which is set to true if and only if the square in row i column j has the number k in it.
    # Rows and columns of the sudoku grid are indexed by 0-8 but the numbers in the squares are in the range 1-9.
    next_label = 1
    for i in range(n):
        for j in range(n):
            for k in range(1,n+1):
                variables[(i,j,k)] = next_label
                next_label += 1
    
    fixed_squares = [] # a list of tuples (i,j,k) where each tuple represents that in row i column j we have the given number k
    with open(sudoku_file,'r') as file:
        for i,line in enumerate(file):
            for j,s in enumerate(line.strip()): # remove new line character from the end
                if s != '.':
                    fixed_squares.append((i,j,int(s)))

    # Each square has at least one number in it
    for i in range(n):
        for j in range(n):
            clauses.append([variables[(i,j,k)] for k in range(1,n+1)])

    # No square has two numbers in it
    for i in range(n):
        for j in range(n):
            for k,l in [(k,l) for k in range(1,n+1) for l in range(k+1,n+1)]:
                clauses.append([-variables[i,j,k],-variables[i,j,l]])
    
    # Every row has every number at least once
    for i in range(n):
        for k in range(1,n+1):
            clauses.append([variables[(i,j,k)] for j in range(n)])

    # Every column has every number at least once
    for j in range(n):
        for k in range(1,n+1):
            clauses.append([variables[(i,j,k)] for i in range(n)])

    # Every box has has every number at least once
    for b1 in range(d):
        for b2 in range(d):
            box_coordinates = [(b1*d + i ,b2*d + j) for i in range(d) for j in range(d)]
            for k in range(1,n+1):
                clauses.append([variables[(i,j,k)] for i,j in box_coordinates])            

    # The fixed squares have the given numbers in them
    for i,j,k in fixed_squares:
        clauses.append([variables[(i,j,k)]])

    sat, outcome, time  = cdcl(clauses)
    print(f"Search took {time:.3f} seconds")
    
    if not sat:
        proof = outcome # 'outcome' is a proof object
        print("The sudoku was not solvable")
        answer = input(f"Proof has {len(proof.proof_lines)} lines. Print proof? (y/n) ")
        if answer == 'y':
            for line in proof.formatted_lines():
                print(line)

        return
    
    assignment = outcome # The set of clauses was satisfiable, 'outcome' is a truth assignment
    rows_of_solution = [] 
    for i in range(n):
        row = []
        for j in range(n):
            for k in range(1,n+1):
                if assignment[variables[(i,j,k)]] == True:
                    row.append(k)
        rows_of_solution.append(row)

    # Printing the solution
    for row_index,row in enumerate(rows_of_solution):
        for column_index,number in enumerate(row):
            print(number,end=" ")
            if (column_index + 1) % d == 0 and column_index+1 < n:
                print("|",end=" ")
        print()
        if (row_index+1) % d == 0 and row_index + 1 < n:
            print("- "*(n+d-1)) 


def print_parse_error(error,tokens):
    print("Parsing error!")
    print(error.message, '\n')

    # print given formula
    for t in tokens:
        print(t.lexeme, end=' ')
    print()

    # print where the error occurs
    for i in range(len(tokens)):
        if i == error.error_pos:
            print("^",end="")
        else:
            print(" "*len(tokens[i].lexeme),end= " ")    
    print() 

def print_scan_error(error,input_string):
    print("Scanning error!")
    print(error.message,'\n')
    print(input_string)
    for i in range(len(input_string)):
        if i == error.error_pos:
            print("^")
            return
        else:
            print(" ",end="")

def run_tests():
    # Run CDCL with randomly generated CNF formulas.
    test_number = 0
    sats = 0
    unsats = 0
    max_number_of_clauses = 1000
    max_number_of_variables = 50
    min_size_of_clause = 3 
    max_size_of_clause = 10

    while True:
        test_number += 1
        clauses = random_clauses(max_number_of_clauses,max_number_of_variables,min_size_of_clause,max_size_of_clause)
        sat, outcome, time = cdcl(clauses,silent=True)
        if sat:
            sats += 1
        else:
            unsats += 1
        print(f"  Tests: {test_number} Sats: {sats} Unsats: {unsats}",end='\r')


def solve_cnf_file(file):
    clauses = clauses_from_dimacs(file)
    sat, outcome, time = cdcl(clauses)
    print(f"Search took {time:.3f} seconds")
    if sat:
        assignment = outcome
        variables = list(set([abs(k) for k in assignment.keys()])) # literals are represented by non-zero integers
        variables.sort()
        print("Is sat")
        answer = input(f"Print truth assignment ({len(variables)} variables)? (y/n)? ")
        if answer == 'y':
            for k in variables:
                print(f"{k}: {assignment[k]}")
    else:
        proof = outcome
        print(f"Is not sat")
        answer = input(f"Print proof (proof has {len(proof.proof_lines)} lines)? (y/n) ")
        if answer == 'y':
            for line in proof.formatted_lines():
                print(line)


def solve_formula(input_string):
    try:
        tokens = split_into_tokens(input_string)
    except ParseError as e:
        print_scan_error(e,input_string)
        return
    
    variables = list(set([t.lexeme for t in tokens if t.tokentype == TokenType.VAR]))
    parser = Parser(tokens)

    try:
        syntax_tree = parser.syntax_tree()
    except ParseError as e:
        print_parse_error(e,tokens)
        return
        
    tseitin_set, subformula_labels = tseitin_set_and_labels(syntax_tree)
    
    pre_processed_clauses = [c for c in tseitin_set if 'T' not in c] # remove all clauses that have 'T' in them
    pre_processed_clauses = [[i for i in clause if i != 'F'] for clause in pre_processed_clauses] # remove 'F' from every clause

    is_sat, outcome, time = cdcl(pre_processed_clauses)

    if is_sat:
        assignment = outcome
        print("Formula is sat with:")
        for v in variables:
            code_for_variable = subformula_labels[v]
            print(f"{v}: {assignment[code_for_variable]}")
    else:
        print("Formula is not sat")
        answer = input("Print proof (y/n)? ")
        if answer == 'y':
            proof = outcome
            print("Subformula labels:")
            for sf,label in subformula_labels.items():
                print(f"{label}: {sf}")
            print("Tseitin set:")
            for c in tseitin_set:
                print(c)
            print("Resolution proof (with 'T' and 'F' possibly removed)")
            for line in proof.formatted_lines():
                print(line)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Excpected two arguments after script name")
        exit()

    mode = sys.argv[1]
    match mode:
        case 'sudoku':
            file = sys.argv[2]
            solve_sudoku(file)
        
        case 'cnf':
            file = sys.argv[2]
            solve_cnf_file(file)

        case 'formula':
            input_string = sys.argv[2]
            solve_formula(input_string)
            
        

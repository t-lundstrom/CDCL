from collections import deque
from time import time

class ProofLine:
    def __init__(self,line_number,clause,comment):
        self.line_number = line_number
        self.clause = clause # frozenset
        self.comment = comment # A string explaining if the clause is an original clause or obtained from clauses earlier in the proof via resolution

class Proof:
    def __init__(self):
        self.proof_lines = [] 
        self.line_numbers = {} # Key: a clause as frozensets. Value: the line number where that clause appears in the proof
        self.current_line = 0

    def add_to_proof(self,clause):
        if clause not in self.line_numbers.keys():
            line_number = self.next_line_number()
            self.line_numbers[clause] = line_number
            pl = ProofLine(line_number,clause,"Original clause") # in this case we know 'clause' must be among the original clauses, see Section 3.5 of the pdf.
            self.proof_lines.append(pl)

    def next_line_number(self):
        i = self.current_line 
        self.current_line += 1
        return i

    def resolution(self,clause1,clause2,literal):
        res = frozenset([x for x in list(clause1) + list(clause2) if x not in [literal,-literal]])
        if res not in self.line_numbers.keys(): # it could be that the clause obtained by resolution is already in the proof. In that case, there's no need to add it there again.
            new_line_number = self.next_line_number()
            self.line_numbers[res] = new_line_number
            line1 = self.line_numbers[frozenset(clause1)] 
            line2 = self.line_numbers[frozenset(clause2)]  
            pl = ProofLine(new_line_number,res,f"Res({line1},{line2},{abs(literal)})")
            self.proof_lines.append(pl)
        
        return res
    
    def formatted_lines(self):
        # Proof lines formatted nicely for printing.
        # Each line will be string of the form: <line_number> <clause> <comment>
        # We add spaces between <clause> and <comment> so that the comments line up nicely.
        line_number_and_clause = [str(pl.line_number) + ": " + " ".join([str(i) for i in pl.clause]) for pl in self.proof_lines] 
        padding_length = max([len(s) for s in line_number_and_clause]) 
        lines = []
        for i in range(len(self.proof_lines)):
            lines.append(f"{line_number_and_clause[i]:{padding_length}}  {self.proof_lines[i].comment}")

        return lines    

class Trail:
    def __init__(self):
        self.trail = [] # here 'trail' will consist of unannotated literals
        self.level = {}
        self.reason = {} # Gives the reason clause for each literal in the trail. For decision literals this will be None.
        self.assignment = {} # the truth assignment corresponding to the trail.
        self.current_level = 0
    
    def add_to_trail(self,lit,reason_clause):
        self.trail.append(lit)
        self.assignment[lit] = True
        self.assignment[-lit] = False
        self.reason[lit] = reason_clause
        if reason_clause == None:
            self.current_level += 1
        self.level[lit] = self.current_level
        self.level[-lit] = self.current_level

    def backtrack(self,m):
        # We backtrack by removing all literals of level > m from the trail.
        self.trail = [k for k in self.trail if self.level[k] <= m] 
        self.current_level = [self.reason[l] for l in self.trail].count(None) # the number of decision literals
        # The levels, reason sets and truth values stay the same for literals that remain in the trail.
        old_levels = self.level.copy()
        self.level = {}
        for l in self.trail:
            self.level[l] = old_levels[l]
            self.level[-l] = old_levels[l]
        self.reason = {l : self.reason[l] for l in self.trail}
        self.assignment = {}
        for l in self.trail:
            self.assignment[l] = True
            self.assignment[-l] = False

def init_watched_literals(clauses,watched_in_clauses,watched_literals,to_propagate):
    # Set the watched literals for each clause.
    # Report if we find an empty clause.
    for clause in clauses:
        if len(clause) == 0:
            return clause

        elif len(clause) == 1:
            # For singleton clauses the two watched literals are both equal to the same literal.
            l = list(clause)[0]
            watched_in_clauses[l].append(clause)
            watched_literals[clause] = [l,l]
            to_propagate.append((l,clause)) # singleton clauses are units at the beginning so we need to propagate them to true

        else:
            # We pick two literals as the watched literals.
            # As we removed tautologies and duplicate literals earlier, the two watched literals will have different variables.
            as_list = list(clause)
            watch1 = as_list[0]
            watch2 = as_list[1]
            watched_in_clauses[watch1].append(clause)
            watched_in_clauses[watch2].append(clause)
            watched_literals[clause] = [watch1,watch2]

    return None


def unit_propagation(trail,proof,watched_in_clauses,watched_literals,to_propagate):
    # We execute unit propagations until no more units remain or until we obtain a falsified clause.
    while len(to_propagate) > 0:
        popped_literal,reason = to_propagate.popleft()
        if popped_literal in trail.trail: # It is possible that 'popped_literal' is already in the trail
            continue

        trail.add_to_trail(popped_literal,reason)

        if reason != None and trail.current_level == 0:
            # We have unit propagation at level 0: we add these to the proof.
            # See Section 3.5 of the pdf.

            proof.add_to_proof(reason) 
            falsified_literals = [l for l in reason if l != popped_literal]
            for i,l in enumerate(falsified_literals):
                proof.resolution(falsified_literals[i:] + [popped_literal],[-l],l)

        # Since 'popped_literal' is now false, we go through all clauses where -popped_literal is watched.
        clauses_to_check = watched_in_clauses[-popped_literal].copy() # we need to copy this since we might remove clauses from it during the loop.
        for clause in clauses_to_check:
            # Look for a new watched literal to replace -popped_literal and replace it if one is found.
            for candidate in clause:
                if candidate in watched_literals[clause]:
                    continue
                elif candidate in trail.assignment.keys() and trail.assignment[candidate] == False:
                    continue
                else:
                    # 'candidate' is a non-false literal not equal to the either of the old watched literals.
                    # We may choose it as the new watched literal.
                    watched_literals[clause].remove(-popped_literal)
                    watched_literals[clause].append(candidate)
                    watched_in_clauses[-popped_literal].remove(clause)
                    watched_in_clauses[candidate].append(clause)
                    break
            else: 
                # No new watched literal was found.
                # We check whether we do unit propagation or if we have a falsified clause.

                # The other watched literal (which can be equal to '-popped_literal' if 'clause' is a singleton).
                other = watched_literals[clause][0] if watched_literals[clause][0] != -popped_literal else watched_literals[clause][1] 

                if other not in trail.assignment.keys():
                    # We know 'clause' is a unit and 'other' is implied
                    to_propagate.append((other,clause)) 
                
                elif trail.assignment[other] == True:
                    # The other watched literal is true: no need to do anything
                    continue
                else:
                    # 'other' must be false.
                    # We know 'clause' is falsified as both watched literals are now false and every unwatched literal was also false.
                    return clause
    
    return None # no clause was falsified during this unit propagation


def clause_learning(falsified_clause,trail,proof):
    # Given recently falsified clause, we learn a new clause with resolution.
    # The learned clause will be a 1-UIP clause: it has exactly one literal whose level is the current level.

    learned_clause = falsified_clause
    while [trail.level[l] for l in learned_clause].count(trail.current_level) >= 2:
        # We look for l that maximizes max {pos(-l) | l in learned_clause}.
        # The negation of every literal in learned_clause appears in the trail
        latest_in_trail = sorted([-l for l in learned_clause], key=lambda lit: trail.trail.index(lit))[-1] 
        reason_clause = trail.reason[latest_in_trail]
        proof.add_to_proof(reason_clause)
        proof.add_to_proof(learned_clause)
        learned_clause = proof.resolution(learned_clause,reason_clause,latest_in_trail)

    return learned_clause


def backtrack(learned_clause,trail,watched_in_clauses,watched_literals,to_propagate):
    # Given the newly learned clause 'learned_clause', we compute the correct backtrack level 
    # and set the watched literals for 'learned_clause'.
    if len(learned_clause) == 1:
        l = list(learned_clause)[0]
        # we set the only literal as the watched literal
        watched_in_clauses[l].append(learned_clause)
        watched_literals[learned_clause] = [l,l]
        trail.backtrack(0) # Backtrack to level 0.
        # We know l is now undefined and hence implied by 'learned_clause'
        # One can show that 'learned_clause' is the only implied clause at this point
        to_propagate.clear()
        to_propagate.append((l,learned_clause))
    else:
        # 'learned_clause' has at least two literals in it
        # The watched literals for 'learned_clause' will be the two with the highest levels.
        # At this point 'learned_clause' is falsified so every literal in 'learned_clause' has a level.
        sorted_by_level = sorted(learned_clause, key=lambda lit: trail.level[lit])
        
        watch1 = sorted_by_level[-1] # This one has level equal to the current level
        watch2 = sorted_by_level[-2] # The second highest level in 'learned_clause'
        watched_literals[learned_clause] = [watch1,watch2]
        watched_in_clauses[watch1].append(learned_clause)
        watched_in_clauses[watch2].append(learned_clause)
        
        backtrack_level = trail.level[watch2]
        trail.backtrack(backtrack_level) # Now 'watch1' is implied by 'learned_clause' and it is the only implied clause.
        to_propagate.clear()
        to_propagate.append((watch1,learned_clause))


def is_tautology(clause):
    for l in clause:
        if -l in clause:
            return True
    
    return False


def cdcl(clauses,silent=False):
    # We assume the literals are non-zero integers where negative integers represent negations of variables.   
    
    # We turn clauses to frozensets so we may use them as keys and to also remove duplicate literals.
    # We also remove tautologies, i.e. clauses that contain some literal l and -l.
    clauses = [frozenset(c) for c in clauses if not is_tautology(c)] 
    
    # Since we will use clauses as keys in the dictionary 'watched_literals' that gives the watched literals in a given clause,
    # it's important that no clause appears more than once as otherwise it becomes ambiguous whose watched literals we get 
    # when we call 'watched_literals[c]' for some clause 'c'
    clauses = list(set(clauses)) 

    trail = Trail()
    proof = Proof() # The resolution proof we build during the algorithm.
    variables = list(set([abs(l) for c in clauses for l in c])) # all possible variables with the given clauses
    literals = variables + [-k for k in variables] # all possible literals with the given clauses
    watched_in_clauses = {l : [] for l in literals} # gives the list of clauses where a literal is watched
    watched_literals = {} # Keys: clauses. Values: a 2-element list of the watched literals for that clause.
    to_propagate = deque() # Whenever we either make a new decision or we find that a literal is implied by a clause, we add the literal here.
    # We use this as a queue, adding to the right, popping from the left.
    # The literals we add are annotated literals, which we implement as tuples (l,R),
    # where l is a literal (i.e. an integer) and R is either a clause or 'None'.
    # We use 'None' if l is a decision literal.

    if not silent:
        print(f"Starting CDCL with {len(variables)} variables and {len(clauses)} clauses")
    
    start = time()

    # Setting watched literals
    # If 'init_watched_literals' finds an empty clause, we can report that the formula is not sat.
    empty_clause = init_watched_literals(clauses,watched_in_clauses,watched_literals,to_propagate)
    if empty_clause != None:
        proof.add_to_proof(empty_clause)
        return False, proof, time() - start

    # The main loop
    while True:
        # We do unit propagation and see if there is a falsified clause
        falsified_clause = unit_propagation(trail,proof,watched_in_clauses,watched_literals,to_propagate)

        if falsified_clause != None:
            if trail.current_level == 0:
                # We found a falsified clause at level 0: the formula is not satisfiable.
                # We are now able to deduce the empty clause: see section 3.5 of the pdf
                proof.add_to_proof(falsified_clause) 
                falsified_clause = list(falsified_clause)

                for i,l in enumerate(falsified_clause):
                    proof.resolution(falsified_clause[i:],[-l],l)
                
                return False, proof, time() - start
            
            # Level is > 0, we do clause learning and backtracking
            learned_clause = clause_learning(falsified_clause,trail,proof)
            clauses.append(learned_clause) 
            backtrack(learned_clause,trail,watched_in_clauses,watched_literals,to_propagate)

        else:
            # no falsified clauses on this round
            unassigned = [l for l in literals if l not in trail.assignment.keys()]

            if len(unassigned) == 0: 
                # all literals have been assigned, we must have a satisfying assignment
                return True, trail.assignment, time() - start
            
            # we make a new decision
            l = unassigned[0]
            to_propagate.append((l,None))
            
            
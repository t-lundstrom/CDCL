from enum import Enum, auto

# Context free grammar for formulas:

# Terminals: EOF, VAR, T, F, (, ), <->, ->, v, &, ~
# Non-terminals: START, E, I, O, A, N, P

# START ::= E EOF
# E     ::= I (<-> I)*            //  equivalence
# I     ::= O (-> O)*             //  implication
# O     ::= A (v A)*              //  disjunction 
# A     ::= N (& N)*              //  conjunction
# N     ::= ~ N | P               //  negation
# P     ::= VAR | T | F | ( E )   //  primary

# VAR matches a single letter (except not 'v', 'T' or 'F'), or a string of the form '[S]' where 'S' is any string.
# We use 'v' for disjunction, 'T' for True and 'F' for False.
# White characters are ignored in formulas.

# First sets of START,E,I,O,A are all equal to {'~', VAR, '('}.
# First set of N ::= ~ N is {'~'} and first set of N ::= P is {VAR, '(', 'T', 'F'}.
# First set of P ::= VAR is {VAR}
# First set of P ::= T is {'T'}
# First set of P ::= F is {'F'}
# First set of P ::= ( E ) is {'('}.

class TokenType(Enum):
    IMPLY   = auto()
    EQUIV   = auto()
    CONJ    = auto()
    DISJ    = auto()
    NEG     = auto()
    LPAREN  = auto()
    RPAREN  = auto()
    VAR     = auto() # variables
    TRUE    = auto()
    FALSE   = auto()
    EOF     = auto() # end of formula

class Token:
    def __init__(self,tokentype, lexeme):
        self.tokentype = tokentype
        self.lexeme = lexeme

class Atomic:
    # atomic formulas are 'T', 'F', and variables
    def __init__(self,atomtype,symbol):
        self.atomtype = atomtype
        self.symbol = symbol

class Binary:
    def __init__(self,left,right,connective):
        self.left = left
        self.connective_token = connective
        self.right = right

class Unary:
    def __init__(self,child,connective):
        self.child = child
        self.connective_token = connective

class ParseError(Exception):
    def __init__(self,message,error_pos):
        super().__init__(message)
        self.message = message
        self.error_pos = error_pos

class Parser:
    def __init__(self,tokens):
        self._tokens = tokens
        self._current_token_index = None
        self._current_token = None

    def syntax_tree(self):
        self._current_token_index = 0
        self._current_token = self._tokens[0]
        
        tree = self._equivalence() # throws ParseError if an error occurs during parsing
        if self._at_end():
            return tree
        else:
            raise ParseError("Formula should have ended here",self._current_token_index)
        
    def _at_end(self):
        return self._current_token.tokentype == TokenType.EOF

    def _advance(self):
        # Note: every call of this function happens after checking that 
        # the current token is something other than EOF.
        # Since EOF is always the last token, current_token_index never goes
        # out of bounds.
        self._current_token_index += 1
        self._current_token = self._tokens[self._current_token_index]

    def _equivalence(self):
        tree = self._implication()

        while self._current_token.tokentype == TokenType.EQUIV:
            connective_token = self._current_token
            self._advance() # eat the equivalence <->
            right = self._implication()
            tree = Binary(tree,right,connective_token)

        return tree    


    def _implication(self):
        tree = self._disjunction()

        while self._current_token.tokentype == TokenType.IMPLY:
            connective_token = self._current_token
            self._advance() # eat the implication ->
            right = self._disjunction()
            tree = Binary(tree,right,connective_token)

        return tree
    
    def _disjunction(self):
        tree = self._conjunction()

        while self._current_token.tokentype == TokenType.DISJ:
            connective_token = self._current_token
            self._advance() # eat the disjunction v 
            right = self._conjunction()
            tree = Binary(tree,right,connective_token)

        return tree
    
    def _conjunction(self):
        tree = self._negation()

        while self._current_token.tokentype == TokenType.CONJ:
            connective_token = self._current_token
            self._advance() # eat the conjunction &
            right = self._negation()
            tree = Binary(tree,right,connective_token)

        return tree
    
    def _negation(self):
        if self._current_token.tokentype == TokenType.NEG:
            connective_token = self._current_token
            self._advance() # eat the negation ~
            child = self._negation()
            return Unary(child,connective_token)
        
        return self._primary()
        
    def _primary(self):
        if self._current_token.tokentype in [TokenType.VAR, TokenType.TRUE, TokenType.FALSE]:
            atomtype = self._current_token.tokentype
            symbol = self._current_token.lexeme
            atom = Atomic(atomtype,symbol)
            self._advance() # eat the atomic formula
            return atom
        
        elif self._current_token.tokentype == TokenType.LPAREN:
            self._advance() # eat the left paren '('
            eq = self._equivalence()
            if self._current_token.tokentype == TokenType.RPAREN:
                self._advance() # eat the right paren ')'
                return eq
            else:
                self._error("')'")
        else:
            self._error("'(', VAR, '~', 'T' or 'F'")

    def _error(self, expected):
        error_pos = self._current_token_index
        if self._at_end():
            message = f"Expected {expected}. Formula ended unexpectedly."
        else:
            message = f"Expected {expected} but got '{self._current_token.lexeme}' instead."

        raise ParseError(message,error_pos)    
 
def print_syntax_tree(node,indentation):
    # Prints the syntax tree.
    # Used mainly for debugging.
    if type(node) == Atomic:
        print(f"{" "*indentation}{node.symbol}")
    
    elif type(node) == Binary:
        print(f"{" "*indentation}{node.connective_token.lexeme}")
        print_syntax_tree(node.left,indentation+4)
        print_syntax_tree(node.right,indentation+4)

    elif type(node) == Unary:
        print(f"{" "*indentation}{node.connective_token.lexeme}")
        print_syntax_tree(node.child,indentation+4)


def split_into_tokens(s):
    # Scans the input string 's' and constructs a list of tokens or throws ParseError
    tokens = []
    i = 0
    while i < len(s):
        if s[i] == '[':
            # see if we have a propositional variable of the form '[some string]'
            j = i+1 
            while j < len(s) and s[j] != ']':
                j+=1
            if j == len(s):
                raise ParseError("Square bracket was never closed",j-1)
            tokens.append(Token(TokenType.VAR,s[i:j+1])) # s[i:j+1] is a string of the form '[S]' for some string 'S'
            i = j+1
        
        elif s[i].isalpha() and s[i] not in ['v','T','F']:    
            tokens.append(Token(TokenType.VAR,s[i]))
            i+=1

        elif s[i] == 'T':
            tokens.append(Token(TokenType.TRUE,'T'))
            i+=1

        elif s[i] == 'F':
            tokens.append(Token(TokenType.FALSE,'F'))
            i+=1

        elif i+2 < len(s) and s[i] + s[i+1] + s[i+2] == '<->':
            tokens.append(Token(TokenType.EQUIV,'<->'))
            i+=3

        elif i+1 < len(s) and s[i] + s[i+1] == '->':
            tokens.append(Token(TokenType.IMPLY,'->'))
            i+=2

        elif s[i] == 'v':
            tokens.append(Token(TokenType.DISJ,'v'))
            i+=1

        elif s[i] == '&':
            tokens.append(Token(TokenType.CONJ,'&'))
            i+=1

        elif s[i] == '~':
            tokens.append(Token(TokenType.NEG,'~'))
            i+=1

        elif s[i] == '(':
            tokens.append(Token(TokenType.LPAREN,'('))
            i+=1

        elif s[i] == ')':
            tokens.append(Token(TokenType.RPAREN,')'))
            i+=1
        
        elif s[i] in [' ', '\t', '\r', '\n']:
            i+=1 # we ignore whitespace

        else:
            raise ParseError(f"Unexpected character: {s[i]}",i)
        
    tokens.append(Token(TokenType.EOF,''))

    return tokens




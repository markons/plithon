# Version 1.09
# =============================================================================
# This version supports following PL/I constructs:
#    
# programname: proc options(main);
#   supported_statements...
# end programname;  
#
# Supported statements:
#   1  dcl variable_name <fixed bin(15|31) | char(length)>;
#   2  variable = <arithmetic-expression> | <string-expression>;
#   3  operators in arithmetic_expression: + - * / ( )
#   4  operators in string-expression: builtins: substr index decimal
#   5  if relational-expression then statement else statement;
#   6  select(expression) when(value) statement; other statement; end; 
#   7  put skip list(variable | constant);
#   8  exec sql "select  sql-select-field" into variable; - only MySQL connection, sample db sakila
#   9  get list(variable-list); - read variables from console per prompt
#  10  one-dimensional arrays are now supported (only integer indexing is possible)
#  11  record i/o simple version (open close read write) works
# ============================================================================= 
# New features in 1.09:
#   - 2D arrays supported
#   - mySql parameters (host,user,password,DB-name) are read from a local file 
#   - several minor error corrections
# =============================================================================
# ============================================================================= 
# Open:
#   define and read simple structures like this (long-term implementation):
#   dcl 1 struc,
#         2 first_name    char(30),
#         2 family_name   char(30),
#         2 salary        char(10),
#         2 dummy         char(10);      
# =============================================================================
# Development environment is the Python Spyder IDE
# ============================================================================= 

# Now you can set up your PLY parser
import ply.lex as lex
import ply.yacc as yacc

import sys, os

from datetime import datetime

level=1

# Getting the current date and time
dt = datetime.now()

# getting the timestamp
ts = datetime.timestamp(dt)

print('start at:', dt)
# List of token names
tokens = (
    'ID', 'NUMBER', 'CHAR_CONST', 'ASSIGN',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',
    'COLON', 'SEMICOLON', 'COMMA',  
    'PUT', 'SKIP', 'LIST', 'END', 'WHEN', 'OTHER', 'SELECT', 'DO', 'WHILE',
    'PROC', 'OPTIONS', 'MAIN', 'DCL', 'FIXED', 'BIN', 'CHAR',  
    'IF', 'THEN', 'ELSE', 'BLOCK_COMMENT', 'SUBSTR', 'CONCAT','DECIMAL','MOD',
    'EXEC', 'SQL', 'INTO', 'STRING', 'INDEX', 'GET',
    'OPEN','CLOSE','READ','WRITE','FILE','FROM','MODE','INPUT','OUTPUT'
)

# Regular expression rules for tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ASSIGN = r'='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'<>'
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','
t_CONCAT = r'\|\|'
t_EXEC = r'EXEC'
t_SQL = r'SQL'
t_INTO = r'INTO'


# Reserved keywords
reserved = {
    'proc': 'PROC',
    'options': 'OPTIONS',
    'main': 'MAIN',
    'dcl': 'DCL',
    'fixed': 'FIXED',
    'bin': 'BIN',
    'char': 'CHAR',
    'varying': 'VARYING',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'put': 'PUT',
    'get': 'GET',
    'skip': 'SKIP',
    'list': 'LIST',
    'end': 'END',
    'when': 'WHEN',
    'other': 'OTHER',
    'select': 'SELECT',
    'do': 'DO',
    'while': 'WHILE',  
    'substr': 'SUBSTR',  
    'index': 'INDEX',
    'mod': 'MOD',
    'into': 'INTO',
    'exec': 'EXEC',
    'sql': 'SQL',
    'open': 'OPEN',
    'close': 'CLOSE',
    'read': 'READ',
    'write': 'WRITE',
    'file': 'FILE',
    'input': 'INPUT',
    'output': 'OUTPUT',
    'from': 'FROM',
    'decimal': 'DECIMAL',
}

# Disable print  
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore print 
def enablePrint():
    sys.stdout = sys.__stdout__

# Disable print for production version
# blockPrint()

# Identifiers (variables)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID')  # Check for reserved words
    return t

# Numbers
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Character constants (strings in single quotes)
def t_CHAR_CONST(t):
    r"\'([^\\\n]|(\\.))*?\'"
    return t

# file name (strings in single quotes)
def t_FILENAME(t):
    r"\'([^\\\n]|(\\.))*?\'"
    return t

# Ignored characters (spaces and tabs)
t_ignore = ' \t'

# Block comment
def t_BLOCK_COMMENT(t):
    r'/\*([^*]|\*+[^*/])*\*+/'
    pass  # Block comments are ignored

# Newline rule
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)
    
# Recognize string literals with single or double quotes
#t_CHAR_CONST = r"\'([^\\']|\\.)*\'"   # Single-quoted strings
t_STRING = r'\"([^\\"]|\\.)*\"'       # Double-quoted strings for SQL    
    
# Build the lexer
lexer = lex.lex()


def indent_block(code, level=1, is_function=False):
    """
    Creates a block of code with indentation based on the level and whether it's within a function.

    Args:
        code: The code string to be indented.
        level: The indentation level (defaults to 1).
        is_function: Whether the code is within a function definition (defaults to False).

    Returns:
        The indented code string.
    """
    indent = "  " * level    
    lines = code.splitlines()
    indented_lines = [] 
    for line in lines:
        indented_lines.append(indent + line)
    return "\n".join(indented_lines)

# Print parsing rules for trace
def print_tokens(input_text):
    lexer.input(input_text)
    while True:
        token = lexer.token()
        if not token:
            break
        print(token)
    
# PL/I program: progname:proc options(main);<declares> <execs> end progname;
def p_program(p):
    '''program : procedure_header declaration_list statement_list END ID SEMICOLON'''
    print('in program:', f"p[:] values: {p[:]}", flush=True)
    # Extract the procedure name from the ID token (which is the fifth element in p)
    procedure_name = p[5]
    
    # Combine the procedure header, declarations, and the list of statements
    # Declaration list and statement list are both lists, so they should be joined properly
    declarations = "\n".join(p[2]) if p[2] else ""
    declarations = indent_block(declarations, 2)
    statements = "\n".join(p[3]) if p[3] else ""
    statements = indent_block(statements, 2)
    
    # The main function code, including the call to the procedure itself in the if __name__ block
    p[0] = f"{p[1]}\n{declarations}\n{statements}\nif __name__ == '__main__':\n    {procedure_name}()"
    p[0] = indent_block(p[0], level=0, is_function=True) 
    
    print('end program:\n', p[0], flush=True)    

# Procedure header and its syntax
def p_procedure_header(p):
    '''procedure_header : ID COLON PROC OPTIONS LPAREN MAIN RPAREN SEMICOLON'''
    print('in procedure_header', f"p[:] values: {p[:]}", flush=True)
    p[0] = f"def {p[1]}():"
    print('in procedure_header result:', f"p[:] values: {p[:]}", flush=True)
    
# def p_variable_access(p):
#     '''variable_access : ID LPAREN NUMBER COMMA NUMBER RPAREN
#                        | ID LPAREN ID COMMA ID RPAREN
#                        | ID LPAREN NUMBER RPAREN
#                        | ID LPAREN ID RPAREN
#                        | ID'''
#     print('in variable_access', f"p[:] values: {p[:]}", flush=True)                    
#     if len(p) == 7:  # Two-dimensional array access
#         p[0] = f"{p[1]}[{p[3] - 1}][{p[5] - 1}]"  # Adjust indices for 0-based indexing
#     elif len(p) == 5:  # One-dimensional array access or variable access
#         if isinstance(p[3], int):
#             p[0] = f"{p[1]}[{p[3] - 1}]"
#         else:
#             p[0] = f"{p[1]}[{p[3]}]"  # Assume variable index without adjustment
#     else:
#         p[0] = p[1]
#     print('end variable_access:', p[0], flush=True)  

def p_variable_access(p):
    """
    variable_access : ID LPAREN NUMBER COMMA NUMBER RPAREN
                   | ID LPAREN ID COMMA ID RPAREN
                   | ID LPAREN ID COMMA NUMBER RPAREN
                   | ID LPAREN NUMBER RPAREN                   
                   | ID LPAREN ID RPAREN
                   | ID                          
    """   
     
    #| ID LPAREN NUMBER COMMA NUMBER RPAREN ASSIGN expression  
    print('in variable_access', f"p[:] values: {p[:]}", flush=True) 
    print('len(p)', len(p), flush=True) 
    if len(p) == 7:  # Two-dimensional array access or assignment
        print('p[1]:', p[1], flush=True) 
        print('p[2]:', p[2], flush=True) 
        print('p[3]:', p[3], flush=True) 
        print('p[4]:', p[4], flush=True) 
        print('p[5]:', p[5], flush=True) 
        print('p[6]:', p[6], flush=True) 
        # print('p[7]:', p[7], flush=True)
        
        if len(p) == 7:  # Assignment
            # Handle integer indices with adjustment
            if isinstance(p[3], int) and isinstance(p[5], int):
                print('case(1)', flush=True) 
                #p[0] = f"{p[1]}[{p[3] - 1}][{p[5] - 1}] = {p[7]}"
                p[0] = f"{p[1]}[{p[3]}][{p[5]}]"
            # Check if ID with NUMBER pattern
            elif isinstance(p[3], str) and isinstance(p[5], int):
                print('case(1) - ID with NUMBER', flush=True)
                p[0] = f"{p[1]}[{p[3]}][{p[5]}]"  # Handle variable and integer index    
            else:
                # Handle variable indices (no adjustment)
                print('case(2)', flush=True) 
                # p[0] = f"{p[1]}[{p[3]}][{p[5]}] = {p[7]}"
                p[0] = f"{p[1]}[{p[3]}][{p[5]}]"
                
        else:  # Access
            # Handle integer indices with adjustment
            if isinstance(p[3], int) and isinstance(p[5], int):
                print('case(3)', flush=True) 
                p[0] = f"{p[1]}[{p[3]}][{p[5]}]"
            else:
                # Handle variable indices (no adjustment)
                print('case(4)', flush=True) 
                p[0] = f"{p[1]}[{p[3]}][{p[5]}]"
                
                
    elif len(p) == 5:  # One-dimensional array access or variable access or assignment
        p[0] = f"{p[1]}[{p[3]}]"                             
    else:
        p[0] = p[1]
    print('end variable_access:', p[0], flush=True)      
    
def p_declaration_list(p):
    '''declaration_list : declaration_list declaration SEMICOLON
                        | declaration SEMICOLON'''
    print('in declaration_list:', f"p[:] values: {p[:]}", flush=True)
    if len(p) == 4:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

   
def p_declaration(p):
    '''declaration : DCL id_list type_declaration
                   | DCL id_list array_spec type_declaration'''
    print('in declaration:', f"p[:] values: {p[:]}", flush=True)
    decls = []
    if len(p) == 4:  # Scalar declaration
        typ = p[3].upper()
        for var in p[2]:
            if "FIXED BIN" in typ:
                decls.append(f"{var} = 0")
            elif "CHAR" in typ:
                decls.append(f"{var} = ''")  # Initialize CHAR variables as empty strings
    elif len(p) == 5:  # Array declaration
        typ = p[4].upper()
        print('typ:', typ, flush=True)
        if isinstance(p[3], int):  # Check if size is an integer (one-dimensional)
            array_dims = (p[3],)  # Convert size to a tuple
        else:  # Assuming p[3] is a tuple for two-dimensional arrays
            array_dims = p[3]
        print('array_dims:', array_dims, flush=True)

        for var in p[2]:
            if "FIXED BIN" in typ:
                if len(array_dims) == 1:
                    decls.append(f"{var} = [0] * {array_dims[0] + 2}")
                    # Initialize the first element of the array
                    decls.append(f"{var}[0] = 0 #pseudo-init")
                elif len(array_dims) == 2:
                    decls.append(f"{var} = [[0] * {array_dims[1] + 2} for _ in range({array_dims[0] + 2})]")
                    # Initialize the first element of the 2D array
                    decls.append(f"{var}[0][0] = 0 #pseudo-init")
            elif "CHAR" in typ:
                if len(array_dims) == 1:
                    decls.append(f"{var} = [''] * {array_dims[0] + 2}")
                    # Initialize the first element of the array
                    decls.append(f"{var}[0] = '' #pseudo-init")
                elif len(array_dims) == 2:
                    decls.append(f"{var} = [[''] * {array_dims[1] + 2} for _ in range({array_dims[0] + 2})]")
                    # Initialize the first element of the 2D array
                    decls.append(f"{var}[0][0] = '' #pseudo-init")
                    
    p[0] = "\n".join(decls)
    print('end declaration:', p[0], flush=True)


def p_id_list(p):
    '''id_list : ID
               | id_list COMMA ID
               | id_list COMMA ID array_spec'''
    print('in id_list:', f"p[:] values: {p[:]}", flush=True)             
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:  # ID or array spec list (comma separated)
        p[0] = p[1] + [p[3]]
    elif len(p) == 5:  # Handle array spec as part of id_list
        p[0] = p[1] + [f"{p[3]}({p[4]})"]

# def p_array_spec(p):
#     '''array_spec : LPAREN NUMBER RPAREN'''
#     p[0] = p[2]  # The array size
    
def p_array_spec(p):
    '''array_spec : LPAREN NUMBER RPAREN
                 | LPAREN NUMBER COMMA NUMBER RPAREN'''
    print('in array_spec:', f"p[:] values: {p[:]}", flush=True)               
    if len(p) == 4:
        p[0] = (p[2])  # One-dimensional array
    elif len(p) == 6:
        p[0] = (p[2], p[4])  # Two-dimensional array
    
def p_type_declaration(p):
    '''type_declaration : FIXED BIN LPAREN NUMBER RPAREN
                        | CHAR LPAREN NUMBER RPAREN'''
    print('in type_declaration:', f"p[:] values: {p[:]}", flush=True)                    
    if len(p) == 6:  # FIXED BIN(n)
        p[0] = f"{p[1]} {p[2]}({p[4] + 2})" #additional dummy first entry!
    elif p[1].lower() == 'char':  # CHAR(n)
        p[0] = f"{p[1]}({p[3]})"


# def p_id_list(p):
#     '''id_list : ID
#                | id_list ',' ID'''
#     if len(p) == 2:
#         p[0] = [p[1]]
#     else:
#         p[0] = p[1] + [p[3]]

def p_statement_list(p):
    '''statement_list : statement_list statement  
                      | statement     
                      | empty'''
    print('in statement_list:', f"p[:] values: {p[:]} (len: {len(p)})", flush=True)
    
    if len(p) == 3:  # Recursive case: multiple statements
        if isinstance(p[1], list):
            p[0] = p[1] + ([p[2]] if p[2] else [])
        else:
            p[0] = [p[1]] + ([p[2]] if p[2] else [])
    else:
        p[0] = [p[1]] if p[1] else []
    
    print('end statement_list:', p[0], flush=True)

def p_empty(p):
    'empty :'
    p[0] = None  # Use None to signify an empty production
    
       
# Define the rule to handle 'write file from' statements
def p_write_file(p):
    '''write_file : WRITE FILE LPAREN CHAR_CONST RPAREN FROM LPAREN ID RPAREN SEMICOLON'''
    print('in write:', f"p[:] values: {p[:]}", flush=True)
    fname = p[4].replace("'", "")                
    p[0] = f"{fname}.write({p[8]} + '\\n')"
    print('end write:', p[0])      

def p_statement(p):    
    '''statement : assignment_statement  
                 | declaration                 
                 | if_statement
                 | select_statement
                 | do_while_statement
                 | do_end_block
                 | put_statement
                 | get_list_statement
                 | block_comment_statement
                 | open_file
                 | read_file
                 | write_file
                 | close_file                
                 | sql_statement'''             
                  
    print('in statement:', f"p[:] values: {p[:]}", flush=True)             
    p[0] = p[1]
    print('end statement:', p[0], flush=True) 
    
def p_block_comment_statement(p):
    '''block_comment_statement : BLOCK_COMMENT'''
    print('in block_comment_statement:', f"p[:] values: {p[:]}", flush=True)
    p[0] = "#" + p[0]

def p_assignment_statement(p):
    '''assignment_statement : variable_access ASSIGN expression SEMICOLON'''
    print('in assignment:', f"p[:] values: {p[:]}", flush=True)
    print('in assignment,length:', len(p), flush=True)
    p[0] = f"{p[1]} = {p[3]}"
    print('end assignment:', p[0], flush=True)

def p_expression(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | LPAREN expression RPAREN
                  | NUMBER
                  | CHAR_CONST
                  | SUBSTR
                  | MOD
                  | INDEX
                  | DECIMAL
                  | variable_access'''
    print('in expression:', f"p[:] values: {p[:]}", flush=True)
    print('in expression,length:', len(p), flush=True)   
          
    if len(p) == 2:
        # This handles single ID or NUMBER tokens
        p[0] = p[1]
    elif len(p) == 4 and p[1] == '(':
        # This handles expressions in parentheses
        p[0] = f"({p[2]})"
    else:
        # This handles binary operations like PLUS, MINUS, etc.
        p[0] = f"({p[1]} {p[2]} {p[3]})"
    print('end expression:', p[0], flush=True)    
        
def p_expression_substr(p):
    '''expression : SUBSTR LPAREN ID COMMA NUMBER COMMA NUMBER RPAREN
                  | SUBSTR LPAREN ID COMMA NUMBER RPAREN'''
    print('in substr:', f"p[:] values: {p[:]}", flush=True)              
    if len(p) == 9:  # SUBSTR with start and length
        start = p[5] - 1  # PL/I starts at 1, Python starts at 0
        length = p[7]
        p[0] = f"{p[3]}[{start}:{start + length}]"
    elif len(p) == 7:  # SUBSTR with only start
        start = p[5] - 1
        p[0] = f"{p[3]}[{start}:]"
    print('end substr:', p[0], flush=True)    
    
def p_expression_mod(p):
    '''expression : MOD LPAREN ID COMMA NUMBER RPAREN'''
    print('in mod:', f"p[:] values: {p[:]}", flush=True)              
    p[0] = f"{p[3]}%{p[5]}"
    print('end substr:', p[0], flush=True)        
        
def p_expression_index(p):
    '''expression : INDEX LPAREN ID COMMA CHAR_CONST RPAREN'''    
    print('in index:', f"p[:] values: {p[:]}", flush=True)              
    p[0] = f"{p[3]}.find({p[5]}) + 1"   
    print('end index:', p[0], flush=True)  
    
def p_expression_decimal(p):
    '''expression : DECIMAL LPAREN ID RPAREN''' 
    print('in decimal:', f"p[:] values: {p[:]}", flush=True)              
    
    # Convert the ID to a string using Python's str() function
    p[0] = f"str({p[3]})"
    
    print('end decimal:', p[0], flush=True)
 
        
def p_if_statement(p):
    '''if_statement : IF relational_expression THEN statement ELSE statement   
                    | IF relational_expression THEN statement ELSE do_end_block
                    | IF relational_expression THEN do_end_block ELSE statement  
                    | IF relational_expression THEN do_end_block ELSE do_end_block'''
    
    print('in if_statement:', f"p[:] values: {p[:]}", flush=True)  
    print('len:', len(p), flush=True)                
    
    # Check if p[4] (then block) is a list, otherwise wrap it in a list
    then_block = p[4] if isinstance(p[4], list) else [p[4]]
    
    # Check if p[6] (else block) is a list, otherwise wrap it in a list
    else_block = p[6] if isinstance(p[6], list) else [p[6]]
    
    then_code = "\n".join(then_block)
    else_code = "\n".join(else_block)
      
    p[0] = f"if {p[2]}:\n{indent_block(then_code, level=1)}\nelse:\n{indent_block(else_code, level=1)}"
    # p[0] = f"if {p[2]}:\n{then_code}\nelse:\n{else_code}"
        

def p_do_end_block(p):
    '''do_end_block : DO SEMICOLON statement_list END SEMICOLON'''
    print('in do_end:', f"p[:] values: {p[:]}", flush=True) 
    p[0] = p[3]
    print('end do_end:', p[0], flush=True)

# Relational expressions to handle comparisons
def p_relational_expression(p):
    '''relational_expression : expression EQ expression
                             | expression NE expression
                             | expression LT expression
                             | expression LE expression
                             | expression GT expression
                             | expression GE expression
                             | expression ASSIGN expression'''
    print('in relational_expression:', f"p[:] values: {p[:]}", flush=True)                           
    if p[2] == '=':
        p[0] = f"({p[1]} == {p[3]})"
    else:
        p[0] = f"({p[1]} {p[2]} {p[3]})"
    print('end relational_expression:', p[0], flush=True) 

def p_expression_concat(p):
    '''expression : expression CONCAT expression'''
    p[0] = f"{p[1]} + {p[3]}"

# PUT statement rule: translates 'put skip list' to Python's print function
def p_put_statement(p): 
    '''put_statement : PUT SKIP LIST LPAREN element_list RPAREN SEMICOLON'''
    print('in put_statement:', f"p[:] values: {p[:]}", flush=True)
    elements = ", ".join(map(str, p[5]))
    p[0] = f"print({elements})"
    
def p_get_list_statement(p):
    '''get_list_statement : GET LIST LPAREN id_list RPAREN SEMICOLON'''
    print('in get_list:', f"p[:] values: {p[:]}", flush=True)
    vars_to_get = p[4]  # List of variable names
    
    # Generate input statements with dynamic type checking
    python_input_statements = []
    for var in vars_to_get:
        python_input_statements.append(f'''
try:
    {var}_input = input("Enter {var}: ")
    {var} = int({var}_input)
except ValueError:
    {var} = {var}_input  # Fall back to string if not an integer
''')
    
    # Join statements to form the complete block of code
    p[0] = '\n'.join(python_input_statements)
    print('end get_list:', p[0], flush=True)

    
# List of variable names (e.g., var1, var2, var3)
def p_id_list_multiple(p):
    '''id_list : ID COMMA id_list'''
    p[0] = [p[1]] + p[3]  # Combine current ID with rest of the list

# def p_id_list_single(p):
#     '''id_list : ID'''
#     p[0] = [p[1]]  # Single ID
   

def p_element_list(p):
    '''element_list : element
                    | element_list COMMA element'''
    print('in element_list:', f"p[:] values: {p[:]}", flush=True)                
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_element(p):
    '''element : ID
               | NUMBER
               | CHAR_CONST'''
    p[0] = p[1]


def p_select_statement(p):
    '''select_statement : SELECT LPAREN expression RPAREN SEMICOLON when_list other_statement END SEMICOLON'''
    print('in select_statement:', f"p[:] values: {p[:]}")

    # Start building the if-elif-else structure
    select_var = p[3]
    when_cases = p[6]  # when_list provides a list of tuples (condition, code block)

    print('when_cases:', when_cases)

    # Create the initial if statement
    python_code = f"if {select_var} == ({when_cases[0][0]}):\n{indent_block(when_cases[0][1], level=1)}"
    #python_code = f"if {select_var} == ({when_cases[0][0]}):\n{when_cases[0][1]}"

    # Add elif statements for the rest of the cases
    for condition, code in when_cases[1:]:
        python_code += f"\nelif {select_var} == {condition}:\n{indent_block(code, level=1)}"
        #python_code += f"\nelif {select_var} == {condition}:\n{code}"

    # Handle the 'other' block if present
    if p[7]:  # Use p[7] for the other block
        other_block = indent_block(p[7], level=1)       
        python_code += f"\nelse:\n{other_block}"

    # Add the 'end' statement
    python_code += "\n #end-select"

    p[0] = "#select-start \n" + python_code
    print('end select_statement:', p[0])


def p_select_end(p):
    '''select_end : END SEMICOLON'''
    print('in select_end:', f"p[:] values: {p[:]}", flush=True)
    p[0] = "end select"

def p_when_list(p):
    '''when_list : when_list WHEN LPAREN expression RPAREN statement  
                 | when_list WHEN LPAREN expression RPAREN do_end_block
                 | WHEN LPAREN expression RPAREN statement  
                 | WHEN LPAREN expression RPAREN do_end_block
                 | empty'''    
    print('in when_list:', f"p[:] values: {p[:]}", flush=True)
    print('len(p):', len(p), flush=True)

    # Add 'when' clauses as tuples of (condition, flattened statement)
    if len(p) == 7:  # This is for "when_list WHEN ( expression ) statement" format
        # Flatten the statement if necessary
        statement_block = "\n".join(p[6]) if isinstance(p[6], list) else p[6]
        if isinstance(p[1], list):  # Continuing the existing list
            p[0] = p[1] + [(p[4], statement_block)]
        else:  # First entry in the list
            p[0] = [(p[4], statement_block)]
    else:  # This is for "WHEN ( expression ) statement" format (without preceding when_list)
        statement_block = "\n".join(p[5]) if isinstance(p[5], list) else p[5]
        p[0] = [(p[3], statement_block)]

    print('end when_list:', p[0], flush=True)

def p_other_statement(p):
    '''other_statement : OTHER statement  
                       | OTHER do_end_block
                       | empty'''
    print('in other_statement:', f"p[:] values: {p[:]}")

    if len(p) > 1 and p[2]:  # If there is an 'other' clause
        if isinstance(p[2], list):  # Flatten if it's a list
            p[0] = "\n".join(p[2])
        else:
            p[0] = p[2]
    else:
        p[0] = ""

    print('end other_statement:', p[0])


def p_do_while_statement(p):
    '''do_while_statement : DO WHILE LPAREN relational_expression RPAREN SEMICOLON statement do_end
                          | DO WHILE LPAREN relational_expression RPAREN SEMICOLON statement_list do_end'''                       
    print('in do_while_statement:', f"p[:] values: {p[:]}", flush=True) 

    # Get the relational expression (condition) and the loop body
    loop_condition = p[4]  # This holds the relational expression
    stmt = ''
    if isinstance(p[7], list):        
        loop_body = "\n".join([stmt for stmt in p[7]])        
        print('stmt in do_while_statement:', loop_body, flush=True)
    else:
        loop_body = p[7]
        print('p[7] is no list:', p[7], flush=True)
    loop_body = indent_block(loop_body, level + 1)    
    
    # Translate to Python's 'while' construct    
    loop_body = loop_body + "\n" + "#end simulated" 
    p[0] = f"while {loop_condition}:\n{loop_body}"
        
    print('end do_while_statement:', p[0], flush=True)
    
def p_do_end(p):
    '''do_end : END SEMICOLON'''
    print('in do_end_statement:', f"p[:] values: {p[:]}", flush=True) 
    p[0] = "#end simulated"
    print('end do_end_statement:', p[0], flush=True)
    # p[0] = None
    
# Define the rule to handle 'open file' statements
def p_open_file(p):
    '''open_file : OPEN FILE LPAREN CHAR_CONST RPAREN INPUT SEMICOLON
                 | OPEN FILE LPAREN CHAR_CONST RPAREN OUTPUT SEMICOLON'''   
    print('in open_file:', f"p[:] values: {p[:]} (len: {len(p)})", flush=True)             
    mode = "r" if p[6].lower() == "input" else "w"
    fname = p[4].replace("'", "")
    p[0] = f"{fname} = open('{fname}.txt', '{mode}')"
    print('end open:', p[0])

# Define the rule to handle 'read file into' statements
def p_read_file(p):
    '''read_file : READ FILE LPAREN CHAR_CONST RPAREN INTO LPAREN ID RPAREN SEMICOLON'''
    print('in read:', f"p[:] values: {p[:]}", flush=True)  
    fname = p[4].replace("'", "")            
    p[0] = f"{p[8]} = {fname}.readline().strip()"
    print('end read:', p[0])

# Global dictionary to store EOF flags for each file
eof_flags = {}


# Define the rule to handle 'close file' statements
def p_close_file(p):
    '''close_file : CLOSE FILE LPAREN CHAR_CONST RPAREN SEMICOLON'''
    print('in close:', f"p[:] values: {p[:]}", flush=True)  
    fname = p[4].replace("'", "")              
    p[0] = f"{fname}.close()"
    print('end close:', p[0])    
    
import mysql.connector
import os

host = '' 
user = ''
password = '' 
db_name = '' 

def read_parameters_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            parameter_list = file.read().strip()
        return parameter_list
    else:
        print(f"***Error: File '{filename}' not found. SQL error!")
        return None

def p_sql_statement(p):
    'sql_statement : EXEC SQL STRING INTO ID SEMICOLON'
    print('in sql_statement:', f"p[:] values: {p[:]}", flush=True)
    
    global host, user, password, db_name

    # Load parameters from the file and strip any surrounding quotes
    filename = "c:/temp/creds.txt"
    parameter_list = read_parameters_from_file(filename)
    
    # Split into key-value pairs and strip unwanted quotes
    params = {}
    pairs = parameter_list.split(', ')
    for pair in pairs:
        key, value = pair.split('=')
        params[key.strip()] = value.strip().strip('"').strip("'")

    # Assign parameters
    host = params['host']
    user = params['user']
    password = params['password']
    db_name = params['database']
    
    print('Parameters:', host, user, password, db_name)
    
    # Extract the SQL query and PL/I variable
    sql_query = p[3].strip('"')
    pl1_var = p[5]
    
    # Generate Python code for SQL execution with parameters
    p[0] = f'''
import mysql.connector

def execute_sql_query(host, db_name, user, password):
    try:
        print("*** Executing SQL Query: {sql_query}")
        
        # Establish MySQL connection with parameters
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = connection.cursor()

        # Execute the SQL query
        sql_query = "{sql_query}"
        cursor.execute(sql_query)

        # Fetch the result and assign it to the PL/I variable (Python variable)
        result = cursor.fetchone()
        {pl1_var} = result[0] if result else None

        # Close the connection
        cursor.close()
        connection.close()

        print(f'*** SQL Result: {{result}}')
        return {pl1_var}

    except mysql.connector.Error as err:
        sqlcode = err.errno
        sqlstate = err.sqlstate
        error_message = err.msg
        print(f"SQL Error: SQLCODE={{sqlcode}}, SQLSTATE={{sqlstate}}, Message={{error_message}}")
        return None

print('Parameters:', host, user, password, db_name)
{pl1_var} = execute_sql_query(host, db_name, user, password)
print('Final result stored in:', {pl1_var})
'''




def p_pl1_var(p):
    '''pl1_var : ID'''
    print('in pl1_var:', f"p[:] values: {p[:]}", flush=True)
    p[0] = p[1]  # PL/I variable is an identifier (ID)

def p_sql_query(p):
    '''sql_query : STRING'''
    print('in sql_query:', f"p[:] values: {p[:]}", flush=True)
    p[0] = p[1]  # The SQL query is a string

# Error handling
def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}'", flush=True)
    else:
        print("Syntax error at EOF", flush=True)
        
parser = yacc.yacc(debug=True, write_tables=True, outputdir='.')

# =============================================================================
# After building the parser, print the state tables (option)
# =============================================================================
def print_lr_state_table(parser):
    """Prints the LR parsing state table."""
    # Check if the parser has the required attributes
    if not hasattr(parser, 'action') or not hasattr(parser, 'goto'):
        print("The parser does not have 'action' or 'goto' attributes.")
        return

    print("State | Action")
    print("-" * 20)

    # Accessing and printing the LR action table
    for state, actions in parser.action.items():
        print(f"State {state}:")
        for token, action in actions.items():
            print(f"  On token {token}: {action}")

    # Accessing and printing the LR goto table
    print("\nGoto Table:")
    for state, gotos in parser.goto.items():
        print(f"State {state}:")
        for nonterminal, next_state in gotos.items():
            print(f"  On non-terminal {nonterminal}: Go to state {next_state}")

# Example call after parser is created
# print_lr_state_table(parser)

# =============================================================================
# Call the TK interface to select the input PL/1 code
# =============================================================================
pl1_code = ""

import tkinter as tk
from tkinter import filedialog

# Global variable to store the selected file path
selected_file_path = None

def select_file():
    """Opens a file dialog for the user to select a PL/I file if not already selected."""
    global selected_file_path

    # Check if file has already been selected, avoid re-opening the file dialog
    if selected_file_path is None:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        selected_file_path = filedialog.askopenfilename(
            title="Select PL/I Input File",
            filetypes=[("PL/I Files", "*.pli"), ("All Files", "*.*")]
        )
        if selected_file_path:
            print(f"Selected file: {selected_file_path}")
        else:
            print("No file selected.")
    
    return selected_file_path

def read_pli_from_file(file_path):
    """Reads PL/I code from the specified file."""
    if not file_path:
        raise ValueError("No file path provided")
    
    with open(file_path, 'r') as file:
        pl1_input = file.read()
    return pl1_input

def pli_to_python(pl1_input):
    """Placeholder for the PL/I to Python transpiler logic."""
    # Your transpiler code logic goes here
    # Return some dummy Python code for this example
    return "# Transpiled Python code goes here"

def execute_transpiler():
    """Executes the PL/I transpiler by selecting the file via file dialog."""
    file_path = select_file()  # This will open the dialog only once
    if not file_path:
        print("No file selected.")
        return None
    
    # Read the PL/I input from the selected file
    pl1_code = read_pli_from_file(file_path)
    # Print or return the PL/I input code
    print("Input PL/I Code:\n")    
    print(pl1_code)
    return pl1_code

pl1_code = execute_transpiler() 

# =============================================================================
# Call the (yacc) parser
# =============================================================================
result = parser.parse(pl1_code)
#result = parser.parse(pl1_code, debug=True)

# print("Tokens:")
# print_tokens(pl1_code)

# =============================================================================
# Print the input PL/I, the generated Python code, as well the execution result
# if possible
# =============================================================================
enablePrint()
if result:
    print("===PL/I input:================================")
    print(pl1_code)
    print("===Python version:============================")
    print(result)
    print("===Execution result:==========================")
    exec(result)
    print("==============================================")
else:
    print("Parsing failed.")
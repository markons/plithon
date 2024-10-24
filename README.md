# plithon
PL/I to Python transpiler to learn PL/I, Python and PLY
Following features are installed in version 1.08:
 1  dcl variable_name <fixed bin(15|31) | char(length)>;
 2  variable = <arithmetic-expression> | <string-expression>;
 3  operators in arithmetic_expression: + - * / ( )
 4  operators in string-expression: builtins: substr index decimal
 5  if relational-expression then statement else statement;
 6  select(expression) when(value) statement; other statement; end; 
 7  put skip list(variable | constant);
 8  exec sql "select  sql-select-field" into variable; - only MySQL connection, sample db sakila
 9  get list(variable-list); - read variables from console per prompt
10  one-dimensional arrays are now supported (only integer indexing is possible)
11  record i/o simple version (open close read write) works

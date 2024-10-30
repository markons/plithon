# plithon
## PL/I to Python transpiler to learn PL/I, Python and PLY
## Following features are installed in version 1.08:
-  dcl variable-name <fixed bin(15|31) | char(length)>;
-  variable = `<arithmetic-expression>` | `<string-expression>`;
-  operators in arithmetic_expression: + - * / ( )
-  operators in string-expression: builtins: substr index decimal
-  if relational-expression then statement else statement;
-  select(expression) when(value) statement; other statement; end; 
-  put skip list(variable | constant);
-  exec sql "select  sql-select-field" into variable; - only MySQL connection, sample db sakila (sorry, actual are my credentials _hardcoded_)
-  get list(variable-list); - read variables from console per prompt
-  one-dimensional arrays are now supported (only integer indexing is possible)
-  record i/o simple version (open close read write) works
## Planned for version 1.09:
- two-dimensional array handling

# plithon 
... is a PL/I to Python transpiler, written in Python <br>
***Target***: anybody who wants learn PL/I, Python and PLY
## Installation
### Components needed
- Python 3.x needed
- mySql connector for SQL access
### How to run
- Tested only under Windows 11
- Simply copy the plithon.py in your (Windows, see also above) directory
- Call the program like this (sample): C:\apps\plithon>python plithon.py
- Select your PL/I input file in the explorer window
- If you want to include SQL statements, store your credentials in the file "c:/temp/creds.txt". 
  I'll make the location of this file later selectable.
  Content of this file is one record (here as sample):
  ***host="localhost", user="root", password="admin", database="sakila"***   
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
- introduce credential file for mySql access
- error corrections

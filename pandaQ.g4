grammar pandaQ;

root: sql_expr(SEMICOLON)?;

sql_expr: selectExpr
| asign 
| plot
| simbol;

plot: PLOT VAR SEMICOLON?;
PLOT: 'PLOT'|'plot';
simbol: VAR SEMICOLON?;
asign: VAR ':=' selectExpr SEMICOLON?;

selectExpr: SELECT MUL FROM tableName (order where | where order | order | where)? inner_join* SEMICOLON?# selectAll
| SELECT columns FROM tableName (order where | where order | order | where)? inner_join* SEMICOLON?# selectColumns;


SELECT: 'SELECT' | 'select';
FROM: 'FROM' | 'from';
SEMICOLON: ';';

tableName: VAR;
columns: column(','column)*;
column: VAR calc AS columnName  # columnCalcAs
| VAR AS columnName  # columnAs
| VAR calc  # columnCalc
| VAR  # onlyColumn;


AS: 'AS'|'as';
columnName: VAR | NUM;

calc: op = (MUL | DIV | SUM | RES) calc_expr;

calc_expr: OP calc_expr CP  # parentesis
| calc_expr MUL calc_expr  # mult
| calc_expr DIV calc_expr  # div
| calc_expr SUM calc_expr  # suma
| calc_expr RES calc_expr  # resta
| NUM  # num;


order: ORDER BY ordexp(','ordexp)*;
ORDER: 'ORDER'|'order';
BY: 'BY'|'by';
ordexp: VAR(','VAR)*
|VAR(','VAR)* (ASC|DESC);

where: WHERE subquerie
| WHERE boolExp(AND boolExp)*;

WHERE: 'WHERE'|'where';
boolExp: NOT? VAR op = (LET | LGT | GT | LT | EQ) NUM;
subquerie: NOT? VAR IN OP selectExpr CP;
IN: 'IN'|'in';

inner_join: INNER JOIN VAR ON VAR EQ VAR;
INNER: 'INNER'|'inner';
JOIN: 'JOIN'|'join';
ON: 'ON'|'on';

AND: 'AND'|'and';
NOT: 'NOT'|'not';
EQ: '=';
LT: '<';
GT: '>';
LET: '<=';
LGT: '>=';

ASC: 'ASC'|'asc';
DESC: 'DESC'|'desc';

OP: '(';
CP: ')';

MUL: '*';
DIV: '/';
SUM: '+';
RES: '-';

VAR: [a-zA-Z_][a-zA-Z0-9_]*;
NUM: [0-9] + ('.'[0-9]+)?;
WS: [ t\r\n] + -> skip;

# Author Héctor Núñez Carpio
import streamlit as st
import pandas as pd

from antlr4 import *
from pandaQLexer import pandaQLexer
from pandaQParser import pandaQParser
from pandaQVisitor import pandaQVisitor

DEBUG = False  # Set to True to get tree
OK_TABLE = 0
OK_PLOT = 1
ERROR = -1


class pandaQVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by pandaQParser#root.
    def visitRoot(self, ctx: pandaQParser.RootContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by pandaQParser#sql_expr.
    def visitSql_expr(self, ctx: pandaQParser.Sql_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by pandaQParser#simbol.
    def visitSimbol(self, ctx: pandaQParser.SimbolContext):
        var = ctx.VAR().getText()
        if var in st.session_state and not st.session_state[var].empty:
            return OK_TABLE, st.session_state[var]
        return ERROR, "Error: Symbol does not exist on symbol table"

    # Visit a parse tree produced by pandaQParser#asign.
    def visitAsign(self, ctx: pandaQParser.AsignContext):
        var = ctx.VAR().getText()

        retval, retbody = self.visit(ctx.selectExpr())
        if (retval == OK_TABLE):
            if var in st.session_state:
                del st.session_state[var]
            st.session_state[var] = retbody
        return (retval, retbody)

    # Visit a parse tree produced by pandaQParser#plot.
    def visitPlot(self, ctx: pandaQParser.PlotContext):
        var = ctx.VAR().getText()
        if var in st.session_state and not st.session_state[var].empty:
            ret = st.session_state[var].select_dtypes(include='number')
            return OK_PLOT, ret
        return ERROR, "Error: Symbol does not exist on symbol table"

    # Visit a parse tree produced by pandaQParser#selectAll.
    def visitSelectAll(self, ctx: pandaQParser.SelectAllContext):
        table = ctx.tableName()

        try:
            table_name = self.visit(table)
            if table_name in st.session_state \
                    and not st.session_state[table_name].empty:
                ret = st.session_state[table_name]
            else:
                ret = pd.read_csv("data/" + self.visit(table) + ".csv")

            if (ctx.inner_join()):
                for inner_join in ctx.inner_join():
                    inner_table, data1, data2 = self.visit(inner_join)
                    tmp_table = pd.read_csv("data/" + inner_table + ".csv")
                    ret = pd.merge(
                        ret,
                        tmp_table,
                        left_on=data1,
                        right_on=data2,
                        how='inner')

        except pd.errors.EmptyDataError:
            ret = "Error: EmptyDataError"
            return ERROR, ret
        except pd.errors.ParserError:
            ret = "Error: ParserError"
            return ERROR, ret
        except FileNotFoundError:
            ret = "Error: FileNotFoundError"
            return ERROR, ret
        except Exception as e:
            ret = f"Exception: {e}"
            return ERROR, ret

        if (ctx.where()):
            where = self.visit(ctx.where())
            for exp in where:
                neg, var, op, val = exp
                if op == '=':
                    if neg:
                        ret = ret[ret[var] != float(val)]
                    else:
                        ret = ret[ret[var] == float(val)]
                elif op == '<':
                    if neg:
                        ret = ret[ret[var] >= float(val)]
                    else:
                        ret = ret[ret[var] < float(val)]
                elif op == '>':
                    if neg:
                        ret = ret[ret[var] <= float(val)]
                    else:
                        ret = ret[ret[var] > float(val)]
                elif op == '<=':
                    if neg:
                        ret = ret[ret[var] > float(val)]
                    else:
                        ret = ret[ret[var] <= float(val)]
                elif op == '>=':
                    if neg:
                        ret = ret[ret[var] < float(val)]
                    else:
                        ret = ret[ret[var] >= float(val)]
                elif op == 'IN':
                    if neg:
                        ret = ret[~ret[var].isin(val)]
                    else:
                        ret = ret[ret[var].isin(val)]

        if (ctx.order()):
            order = self.visit(ctx.order())
            ord_col = [col[0] for col in order]
            ord_type = [col[1] for col in order]
            ret = ret.sort_values(by=ord_col, ascending=ord_type)

        return OK_TABLE, ret

    # Visit a parse tree produced by pandaQParser#selectColumns.
    def visitSelectColumns(self, ctx: pandaQParser.SelectColumnsContext):
        table = ctx.tableName()
        columns = ctx.columns()
        cols = self.visit(columns)

        cols_to_get = [col[0] for col in cols]
        calc_to_do = [col[1] for col in cols]
        name_to_assign = [col[2] for col in cols]

        try:
            table_name = self.visit(table)
            if table_name in st.session_state and \
                    not st.session_state[table_name].empty:
                ret = st.session_state[table_name]
            else:
                ret = pd.read_csv("data/" + self.visit(table) + ".csv")

            if (ctx.inner_join()):
                for inner_join in ctx.inner_join():
                    inner_table, data1, data2 = self.visit(inner_join)
                    tmp_table = pd.read_csv("data/" + inner_table + ".csv")
                    ret = pd.merge(
                        ret,
                        tmp_table,
                        left_on=data1,
                        right_on=data2,
                        how='inner')

            if (ctx.where()):
                where = self.visit(ctx.where())
                for exp in where:
                    neg, var, op, val = exp
                    if op == '=':
                        if neg:
                            ret = ret[ret[var] != float(val)]
                        else:
                            ret = ret[ret[var] == float(val)]
                    elif op == '<':
                        if neg:
                            ret = ret[ret[var] >= float(val)]
                        else:
                            ret = ret[ret[var] < float(val)]
                    elif op == '>':
                        if neg:
                            ret = ret[ret[var] <= float(val)]
                        else:
                            ret = ret[ret[var] > float(val)]
                    elif op == '<=':
                        if neg:
                            ret = ret[ret[var] > float(val)]
                        else:
                            ret = ret[ret[var] <= float(val)]
                    elif op == '>=':
                        if neg:
                            ret = ret[ret[var] < float(val)]
                        else:
                            ret = ret[ret[var] >= float(val)]
                    elif op == 'IN':
                        if neg:
                            ret = ret[~ret[var].isin(val)]
                        else:
                            ret = ret[ret[var].isin(val)]

            ret = ret[list(set(cols_to_get))]
            ret = pd.concat([ret[[col]] for col in cols_to_get], axis=1)
            ret.columns = name_to_assign

        except pd.errors.EmptyDataError:
            ret = "Error: EmptyDataError"
            return ERROR, ret
        except pd.errors.ParserError:
            ret = "Error: ParserError"
            return ERROR, ret
        except FileNotFoundError:
            ret = "Error: FileNotFoundError"
            return ERROR, ret
        except ValueError as e:
            ret = f"Error: {e}"
            return ERROR, ret
        except Exception as e:
            ret = f"Exception: {e}"
            return ERROR, ret

        for i in range(len(calc_to_do)):
            if calc_to_do[i] is not None:
                op, val = calc_to_do[i]
                if op == '*':
                    ret[name_to_assign[i]] = ret[name_to_assign[i]].apply(
                        lambda x: x * float(val))
                if op == '/':
                    ret[name_to_assign[i]] = ret[name_to_assign[i]].apply(
                        lambda x: x / float(val))
                if op == '+':
                    ret[name_to_assign[i]] = ret[name_to_assign[i]].apply(
                        lambda x: x + float(val))
                if op == '-':
                    ret[name_to_assign[i]] = ret[name_to_assign[i]].apply(
                        lambda x: x - float(val))

        if (ctx.order()):
            order = self.visit(ctx.order())
            ord_col = [col[0] for col in order]
            ord_type = [col[1] for col in order]
            ret = ret.sort_values(by=ord_col, ascending=ord_type)

        return OK_TABLE, ret

    # Visit a parse tree produced by pandaQParser#tableName.
    def visitTableName(self, ctx: pandaQParser.TableNameContext):
        [table] = list(ctx.getChildren())
        return table.getText()

    # Visit a parse tree produced by pandaQParser#columns.
    def visitColumns(self, ctx: pandaQParser.ColumnsContext):
        cols = []
        for col in ctx.column():
            cols.append(self.visit(col))
        return cols

    # Visit a parse tree produced by pandaQParser#columnCalcAs.
    def visitColumnCalcAs(self, ctx: pandaQParser.ColumnCalcAsContext):
        [col, calc, _, name] = list(ctx.getChildren())
        return col.getText(), self.visit(calc), self.visit(name)

    # Visit a parse tree produced by pandaQParser#columnAs.
    def visitColumnAs(self, ctx: pandaQParser.ColumnAsContext):
        [col, _, name] = list(ctx.getChildren())
        return col.getText(), None, self.visit(name)

    # Visit a parse tree produced by pandaQParser#columnCalc.
    def visitColumnCalc(self, ctx: pandaQParser.ColumnCalcContext):
        [col, calc] = list(ctx.getChildren())
        return col.getText(), self.visit(calc), col.getText()

    # Visit a parse tree produced by pandaQParser#onlyColumn.
    def visitOnlyColumn(self, ctx: pandaQParser.OnlyColumnContext):
        [col] = list(ctx.getChildren())
        return col.getText(), None, col.getText()

    # Visit a parse tree produced by pandaQParser#columnName.
    def visitColumnName(self, ctx: pandaQParser.ColumnNameContext):
        [name] = list(ctx.getChildren())
        return name.getText()

    # Visit a parse tree produced by pandaQParser#calc.
    def visitCalc(self, ctx: pandaQParser.CalcContext):
        return ctx.op.text, self.visit(ctx.calc_expr())

    # Visit a parse tree produced by pandaQParser#parentesis.
    def visitParentesis(self, ctx: pandaQParser.ParentesisContext):
        [_, num, _] = list(ctx.getChildren())
        return self.visit(num)

    # Visit a parse tree produced by pandaQParser#mult.
    def visitMult(self, ctx: pandaQParser.MultContext):
        [n1, _, n2] = list(ctx.getChildren())
        return str(float(self.visit(n1)) * float(self.visit(n2)))

    # Visit a parse tree produced by pandaQParser#div.
    def visitDiv(self, ctx: pandaQParser.DivContext):
        [n1, _, n2] = list(ctx.getChildren())
        return str(float(self.visit(n1)) / float(self.visit(n2)))

    # Visit a parse tree produced by pandaQParser#suma.
    def visitSuma(self, ctx: pandaQParser.SumaContext):
        [n1, _, n2] = list(ctx.getChildren())
        return str(float(self.visit(n1)) + float(self.visit(n2)))

    # Visit a parse tree produced by pandaQParser#resta.
    def visitResta(self, ctx: pandaQParser.RestaContext):
        [n1, _, n2] = list(ctx.getChildren())
        return str(float(self.visit(n1)) - float(self.visit(n2)))

    # Visit a parse tree produced by pandaQParser#num.
    def visitNum(self, ctx: pandaQParser.NumContext):
        [num] = list(ctx.getChildren())
        return num.getText()

    # Visit a parse tree produced by pandaQParser#order.
    def visitOrder(self, ctx: pandaQParser.OrderContext):
        ordexps = []
        for ordexp in ctx.ordexp():
            list = self.visit(ordexp)
            for obj in list:
                ordexps.append(obj)
        return ordexps

    # Visit a parse tree produced by pandaQParser#ordexp.
    def visitOrdexp(self, ctx: pandaQParser.OrdexpContext):
        ordexps = []
        for var in ctx.VAR()[:-1]:
            tupla = (var.getText(), True)
            ordexps.append(tupla)
        if ctx.VAR():
            tupla = (ctx.VAR()[-1].getText(), False if ctx.DESC() else True)
            ordexps.append(tupla)
        return ordexps

    # Visit a parse tree produced by pandaQParser#where.
    def visitWhere(self, ctx: pandaQParser.WhereContext):
        whereExps = []
        if (ctx.boolExp()):
            for exp in ctx.boolExp():
                whereExps.append(self.visit(exp))
        else:
            whereExps.append(self.visit(ctx.subquerie()))
        return whereExps

    # Visit a parse tree produced by pandaQParser#boolExp.
    def visitBoolExp(self, ctx: pandaQParser.BoolExpContext):
        var = ctx.VAR().getText()
        op = ctx.op.text
        neg = False
        val = ctx.NUM().getText()
        if ctx.NOT():
            neg = True
        return neg, var, op, val

    # Visit a parse tree produced by pandaQParser#subquerie.
    def visitSubquerie(self, ctx: pandaQParser.SubquerieContext):
        var = ctx.VAR().getText()
        op = "IN"
        neg = False
        if ctx.NOT():
            neg = True
        _, table = self.visit(ctx.selectExpr())
        table_ret = table[var].tolist()
        return neg, var, op, table_ret

    # Visit a parse tree produced by pandaQParser#inner_join.
    def visitInner_join(self, ctx: pandaQParser.Inner_joinContext):
        table = ctx.VAR(0).getText()  # Nombre de la tabla para unir
        arg1 = ctx.VAR(1).getText()   # Columna de la primera tabla
        arg2 = ctx.VAR(2).getText()   # Columna de la segunda tabla
        tupla = (table, arg1, arg2)
        return tupla


st.title('pandaQ')
querry = st.text_input('Query:')
submit = st.button('Submit')

if submit:
    palabras = querry.split()

    input_stream = InputStream(querry)
    lexer = pandaQLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = pandaQParser(token_stream)
    tree = parser.root()

    if DEBUG:
        print(tree.toStringTree(recog=parser))
        st.text(tree.toStringTree(recog=parser))

    if parser.getNumberOfSyntaxErrors() != 0:
        st.text("Syntax error")
    else:
        visitor = pandaQVisitor()
        result = visitor.visit(tree)
        retval, retbody = result
        if retval == OK_TABLE:
            df_resultado = pd.DataFrame(retbody)
            st.table(df_resultado)
        elif retval == OK_PLOT:
            df_resultado = pd.DataFrame(retbody)
            st.line_chart(df_resultado)
        else:
            st.text(retbody)

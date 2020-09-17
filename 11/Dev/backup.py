#!/usr/bin/python3.6

import enum
import glob
import os
import sys
import re


def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook

def throw(msg):
    raise Exception(msg)

def int_try_parse(num):
    try:
        out = int(num)
    except ValueError:
        out = None

    return out

class Token(enum.Enum):
    T_COMMENT = 0
    T_KEYWORD = 1
    T_SYMBOL = 2
    T_IDENTIFIER = 3
    T_INT_CONST = 4
    T_STRING_CONST = 5

class K(enum.Enum):
    K_NONE = 0
    K_STATIC = 1
    K_FIELD = 2
    K_ARG = 3
    K_VAR = 4

class JackTokenizer:
    # open input filestream and get ready to tokenize it
    def __init__(self, input_file):
        with open(input_file, "r") as file:
            self.file_list = file.read()

        self.current_token = ""
        self.current_index = 0
        self.key_words = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var',
                          'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let',
                          'do', 'if', 'else', 'while', 'return']
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',',
                        ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
        self.terminals = self.key_words + self.symbols
        self.tokenize()
        return

    # intial tokenization
    def tokenize(self):
        temp_list = []
        out_list = []

        # remove comments

        comment_re = re.compile(
            r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
            re.DOTALL | re.MULTILINE
        )

        def comment_replacer(match):
            start, mid, end = match.group(1, 2, 3)
            if mid is None:
                return ''
            elif start is not None or end is not None:
                return ''
            elif '\n' in mid:
                return '\n'
            else:
                return ' '

        def remove_comments(text):
            return comment_re.sub(comment_replacer, text)

        self.file_list = '\n'.join(
            remove_comments(self.file_list).splitlines())

        # remove whitespace
        self.file_list = self.file_list.split()

        for item in self.file_list:
            if item in self.terminals:
                temp_list.append(item)
            else:
                for symbol in self.symbols:
                    if symbol in item:
                        replacement = " " + symbol + " "
                        item = item.replace(symbol, replacement)

                for temp in item.split():
                    temp_list.append(temp)

        # second pass to rejoin string constants
        in_string = False
        temp_string = ""
        for item in temp_list:
            if item[0] == '"' or in_string:
                if not in_string:
                    temp_string = item
                    in_string = True
                elif '"' in item:
                    temp_string += " " + item
                    out_list.append(temp_string)
                    temp_string = ""
                    in_string = False
                else:
                    temp_string += " " + item
            else:
                out_list.append(item)

        self.file_list = out_list
        return

    # are there any more tokens in the input?
    def hasMoreTokens(self):
        return self.current_index < len(self.file_list)

    # gets next token from input and makes current token
    # only called if hasMoreTokens() is true
    def advance(self):
        self.current_token = self.file_list[self.current_index]
        self.current_index = self.current_index + 1
        return

    # handy macro to make coding a little smoother
    def backtrack(self):
        self.current_index = self.current_index - 1
        self.current_token = self.file_list[self.current_index]

    # returns the type of the current token
    def tokenType(self):
        if self.current_token in self.symbols:
            return Token.T_SYMBOL
        elif self.current_token in self.key_words:
            return Token.T_KEYWORD
        elif self.current_token[0] == '"':
            return Token.T_STRING_CONST
        elif isinstance(int_try_parse(self.current_token), int):
            return Token.T_INT_CONST
        else:
            return Token.T_IDENTIFIER

    # returns the keyword which is the current token
    # only called if tokenType() == T_KEYWORD
    def keyWord(self):
        return self.current_token

    # returns the character which is the current token
    # only called if tokenType() == T_SYMBOL
    def symbol(self):
        return self.current_token

    # returns the identifier which is the current token
    # only called if tokenType() == T_IDENTIFIER
    def identifier(self):
        return self.current_token

    # returns the integer value of the current token
    # only called if tokenType() == T_INT_CONST
    def intVal(self):
        return int_try_parse(self.current_token)

    # returns the string value of the current token
    # only called if tokenType() == T_STRING_CONST
    def stringVal(self):
        return self.current_token[1:-1]

    # helpful macro for making less code in compiler
    def getXml(self):
        token_type = self.tokenType()

        if token_type == Token.T_KEYWORD:
            return "<keyword> {} </keyword>\n".format(self.keyWord())
        elif token_type == Token.T_IDENTIFIER:
            return "<identifier> {} </identifier>\n".format(self.identifier())
        elif token_type == Token.T_INT_CONST:
            return "<integerConstant> {} </integerConstant>\n".format(str(self.intVal()))
        elif token_type == Token.T_STRING_CONST:
            return "<stringConstant> {} </stringConstant>\n".format(self.stringVal())
        elif token_type == Token.T_SYMBOL:
            symbol = self.symbol()
            if symbol == "<":
                symbol = "&lt;"
            elif symbol == ">":
                symbol = "&gt;"
            elif symbol == "&":
                symbol = "&amp;"

            return "<symbol> {} </symbol>\n".format(symbol)

class SymbolTable:
    def __init__(self):
        self.class_scope = []
        self.subroutine_scope = []
        return

    # starts a new subroutine scope
    def startSubroutine(self):
        self.subroutine_scope = []
        return

    # defines a new identifier of a given:
    # name, type and kind and assigns it a
    # running index static and field have class scope
    # arg and var have subroutine scope
    def define(self, name, v_type, kind):
        if kind in [K.K_STATIC, K.K_FIELD]:
            index = len(self.class_scope)
            self.class_scope.append({
                'index': index,
                'name': name,
                'type': v_type,
                'kind': kind
            })
        else:
            index = len(self.class_scope)
            self.subroutine_scope.append({
                'index': index,
                'name': name,
                'type': v_type,
                'kind': kind
            })
        return

    # returns number of variables of the
    # given kind already defined in current
    # scope
    def varcount(self, kind):
        temp = self.subroutine_scope + self.class_scope
        of_kind = list(filter(lambda x: x['kind'] == kind, temp))
        return len(of_kind)

    # returns the kind of the named identifier
    # in the current scope if identifier is
    # unknown, returns NONE
    def kindof(self, name):
        temp = self.subroutine_scope + self.class_scope
        temp = list(filter(lambda x: x['name'] == name, temp))
        if len(temp) > 0:
            return temp[0]['kind']
        else:
            return K.K_NONE

    # returns type of named identifier in
    # current scope
    def typeof(self, name):
        temp = self.subroutine_scope + self.class_scope
        temp = list(filter(lambda x: x['name'] == name, temp))
        if len(temp) > 0:
            return temp[0]['type']
        else:
            return ""

    # returns the index assigned to the
    # named identifier

    def indexof(self, name):
        temp = self.subroutine_scope + self.class_scope
        temp = list(filter(lambda x: x['name'] == name, temp))
        if len(temp) > 0:
            return temp[0]['index']
        else:
            return 0

class VMWriter:
    def __init__(self, file):
        self.file = file
        return
    
    def writePush(self, segment, index):
        return
    
    def writePop(self, segment, index):
        return
    
    def writeArithmetic(self, command):
        return
    
    def writeLabel(self, label):
        return

    def writeGoto(self, label):
        return

    def writeIf(self, label):
        return

    def writeFunction(self, name, nArgs):
        return

    def writeCall(self, name, nLocals):
        return
    
    def close(self):
        self.file.close()
        return

class CompilationEngine:
    def __init__(self):
        return

    def compile(self, tokenizer: JackTokenizer, output_file):
        self.symbolTable = SymbolTable()
        self.tokenizer = tokenizer
        self.file = output_file
        self.compileClass()

    # macros for getting next token with error checking
    # pretty much just to cut down on bloat
    def getNextKeyword(self, location, expected):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_KEYWORD:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_KEYWORD), location))
        keyword = self.tokenizer.keyWord()
        if not keyword == expected and not keyword in expected:
            throw("Syntax Error! Expecting: {} in {}".format(
                str(expected), location))

        self.file.write(self.tokenizer.getXml())

    def getNextSymbol(self, location, expected):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_SYMBOL:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_SYMBOL), location))
        symbol = self.tokenizer.symbol()
        if not symbol == expected and not symbol in expected:
            throw("Syntax Error! Expecting: {} in {}".format(
                str(expected), location))

        self.file.write(self.tokenizer.getXml())

    def getNextIdentifier(self, location, definition=False, k_type=None):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_IDENTIFIER:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_IDENTIFIER), location))

        if definition:
            self.defineVar(k_type)
        
        name = self.tokenizer.identifier()
        kind_of = self.symbolTable.kindof(name)
        kind = kind_of != K.K_NONE
        index = self.symbolTable.indexof(name)

        #determine category
        if kind_of == K.K_ARG:
            category = "arg"
        elif kind_of == K.K_FIELD:
            category = "field"
        elif kind_of == K.K_STATIC:
            category = "static"
        elif kind_of == K.K_VAR:
            category = "var"
        else:
            # peek next token
            token_type = self.doAdvance("getting category")
            if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == "(":
                category = "subroutine"
            else:
                category = "class"
            self.tokenizer.backtrack()

        xml = """<identifier>
        <name>{}</name>
        <category>{}</category>
        <isDefinition>{}</isDefinition>
        <isVar>{}</isVar>
        <index>{}</index>
        </identifier>""".format(name, category, str(definition), str(kind), str(index))
        self.file.write(xml)

    def getNextKeyOrIdentifier(self, location, expected=[], definition=False, k_type=K.K_NONE):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        token_type = self.tokenizer.tokenType()
        if token_type == Token.T_IDENTIFIER:
            self.tokenizer.backtrack()
            self.getNextIdentifier(location, definition, k_type)
        elif token_type == Token.T_KEYWORD:
            keyword = self.tokenizer.keyWord()
            if keyword in expected:
                self.file.write(self.tokenizer.getXml())
            else:
                throw("Syntax Error! Expecting token: {} in {}".format(
                    str(expected), location))
        else:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str([Token.T_IDENTIFIER, Token.T_KEYWORD]), location))

    def getNextInt(self, location):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_INT_CONST:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_INT_CONST), location))

        self.file.write(self.tokenizer.getXml())

    def getNextStr(self, location):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_STRING_CONST:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_STRING_CONST), location))

        self.file.write(self.tokenizer.getXml())

    def defineVar(self, k_type):
        # declare in symbol table, then write to output
        self.tokenizer.backtrack()
        v_type = self.tokenizer.identifier()
        self.doAdvance("symbol table add")
        name = self.tokenizer.identifier()
        self.symbolTable.define(name, v_type, k_type)
        return

    def doAdvance(self, location):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        return self.tokenizer.tokenType()

    def compileClass(self):
        self.file.write("<class>\n")
        self.getNextKeyword("class declaration", "class")
        self.getNextIdentifier("class declaration", True, K.K_NONE)
        self.getNextSymbol("class declaration", "{")

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("class declaration")

            if token_type == Token.T_KEYWORD:
                keyword = self.tokenizer.keyWord()
                if keyword in ["function", "constructor", "method"]:
                    self.tokenizer.backtrack()
                    self.compileSubroutine()
                elif keyword in ["field", "static"]:
                    self.tokenizer.backtrack()
                    self.compileClassVarDesc()
                else:
                    throw("Unexpected keyword: {} in class declaration".format(keyword))
            elif token_type == Token.T_SYMBOL and self.tokenizer.symbol() == "}":
                self.tokenizer.backtrack()
                break
            else:
                throw("Unexpected token type: {} in class declaration".format(
                    str(Token.T_KEYWORD)))

        self.getNextSymbol("class declaration", "}")
        self.file.write("</class>\n")

        return

    def compileClassVarDesc(self):
        self.file.write("<classVarDec>\n")
        self.getNextKeyword("class var declaration", ["field", "static"])

        # get kind
        kind = self.tokenizer.keyWord()

        if kind == "static":
            kind = K.K_STATIC
        else:
            kind = K.K_FIELD

        self.getNextKeyOrIdentifier("class var declaration", [
                                    "int", "void", "boolean", "char"])

        self.getNextIdentifier("class var declaration", True, kind)        

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("class var declaration")

            if not token_type == Token.T_SYMBOL:
                throw("Syntax Error! Unexpected token of type {} in class var declaration".format(
                    str(Token.T_SYMBOL)))
            else:
                symbol = self.tokenizer.symbol()
                if symbol == ";":
                    self.tokenizer.backtrack()
                    break
                elif symbol == ",":
                    self.file.write(self.tokenizer.getXml())
                    self.getNextIdentifier("class var declaration", True, kind)
                    
                else:
                    throw(
                        "Syntax Error! Unexpected symbol: {} in class var declaration".format(symbol))

        self.getNextSymbol("class var declaration", ";")
        self.file.write("</classVarDec>\n")
        return

    def compileSubroutine(self):
        self.symbolTable.startSubroutine()

        self.file.write("<subroutineDec>\n")
        self.getNextKeyword("subroutine declaration", [
                            "function", "method", "constructor"])
        self.getNextKeyOrIdentifier("subroutine declaration", [
                                    "int", "void", "boolean", "char"])
        self.getNextIdentifier("subroutine declaration", True, K.K_NONE)
        self.getNextSymbol("subroutine declaration", "(")
        self.compileParameterList()
        self.getNextSymbol("subroutine declaration", ")")
        self.file.write("<subroutineBody>\n")
        self.getNextSymbol("subroutine declaration", "{")

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("subroutine Body")

            if not token_type == Token.T_KEYWORD:
                throw("Unexpected token type: {} in subroutine body".format(
                    str(token_type)))
            else:
                keyword = self.tokenizer.keyWord()
                if keyword == "var":
                    self.tokenizer.backtrack()
                    self.compileVarDec()
                elif keyword in ["let", "while", "do", "if", "return"]:
                    self.tokenizer.backtrack()
                    break
                else:
                    throw("Unexpected keyword {} in subroutine body".format(
                        str(token_type)))

        self.compileStatements()
        self.getNextSymbol("subroutine body", "}")
        self.file.write("</subroutineBody>\n")
        self.file.write("</subroutineDec>\n")
        return

    def compileParameterList(self):
        self.file.write("<parameterList>\n")
        token_type = self.doAdvance("parameter list")

        if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == ")":
            self.tokenizer.backtrack()
        else:
            self.tokenizer.backtrack()
            self.getNextKeyOrIdentifier(
                "parameter list", ["int", "boolean", "char"])
            self.getNextIdentifier("paramenter list", True, K.K_ARG)

            while self.tokenizer.hasMoreTokens():
                token_type = self.doAdvance("parameter list")

                if not token_type == Token.T_SYMBOL:
                    throw("Unexpected token type: {} in parameter list".format(
                        str(token_type)))
                else:
                    symbol = self.tokenizer.symbol()
                    if symbol == ",":
                        self.file.write(self.tokenizer.getXml())
                        self.getNextKeyOrIdentifier(
                            "parameter list", ["int", "boolean", "char"])

                        self.getNextIdentifier("parameter list", True, K.K_ARG)
                    elif symbol == ")":
                        self.tokenizer.backtrack()
                        break
                    else:
                        throw("Unexpected symbol: {} in parameter list".format(
                            str(symbol)))

        self.file.write("</parameterList>\n")
        return

    def compileVarDec(self):
        self.file.write("<varDec>\n")
        self.getNextKeyword("var declaration", "var")
        self.getNextKeyOrIdentifier(
            "var declaration", ["boolean", "int", "char"])
        self.getNextIdentifier("var declaration", True, K.K_ARG)

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("class var declaration")

            if not token_type == Token.T_SYMBOL:
                throw("Syntax Error! Unexpected token of type {} in class var declaration".format(
                    str(Token.T_SYMBOL)))
            else:
                symbol = self.tokenizer.symbol()
                if symbol == ";":
                    self.tokenizer.backtrack()
                    break
                elif symbol == ",":
                    self.file.write(self.tokenizer.getXml())
                    self.getNextIdentifier("var declaration", True, K.K_ARG)
                else:
                    throw(
                        "Syntax Error! Unexpected symbol: {} in class var declaration".format(symbol))

        self.getNextSymbol("var declaration", ";")
        self.file.write("</varDec>\n")
        return

    def compileStatements(self):
        self.file.write("<statements>\n")

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("statements")

            if token_type == Token.T_KEYWORD:
                keyword = self.tokenizer.keyWord()
                if keyword == "let":
                    self.tokenizer.backtrack()
                    self.compileLet()
                elif keyword == "while":
                    self.tokenizer.backtrack()
                    self.compileWhile()
                elif keyword == "do":
                    self.tokenizer.backtrack()
                    self.compileDo()
                elif keyword == "if":
                    self.tokenizer.backtrack()
                    self.compileIf()
                elif keyword == "return":
                    self.tokenizer.backtrack()
                    self.compileReturn()
                else:
                    throw("Unexpected keyword {} in statements".format(keyword))
            elif token_type == Token.T_SYMBOL and self.tokenizer.symbol() == "}":
                self.tokenizer.backtrack()
                break
            else:
                throw("Unexpected token type: {} in statements".format(
                    str(token_type)))

        self.file.write("</statements>\n")
        return

    def compileLet(self):
        self.file.write("<letStatement>\n")
        self.getNextKeyword("let statement", "let")
        self.getNextIdentifier("let statement")

        # deal with a = x vs a[1] = x
        token_type = self.doAdvance("let statement")
        if token_type == Token.T_SYMBOL:
            symbol = self.tokenizer.symbol()
            if symbol == "[":
                self.file.write(self.tokenizer.getXml())
                self.compileExpression()
                self.getNextSymbol("let statement", "]")
            elif symbol == "=":
                self.tokenizer.backtrack()
            else:
                throw("Unexpected symbol: {} in let statement".format(symbol))
        else:
            throw("Unexepected token type: {}".format(str(token_type)))

        self.getNextSymbol("let statement", "=")
        self.compileExpression()
        self.getNextSymbol("let statement", ";")
        self.file.write("</letStatement>\n")
        return

    def compileIf(self):
        self.file.write("<ifStatement>\n")
        self.getNextKeyword("if statement", "if")
        self.getNextSymbol("if statement", "(")
        self.compileExpression()
        self.getNextSymbol("if statement", ")")
        self.getNextSymbol("if statement", "{")
        self.compileStatements()
        self.getNextSymbol("if statement", "}")

        # check for else statement
        token_type = self.doAdvance("if statement")
        if token_type == Token.T_KEYWORD:
            keyword = self.tokenizer.keyWord()
            if keyword == "else":
                self.tokenizer.backtrack()
                self.getNextKeyword("if statement", "else")
                self.getNextSymbol("if statement", "{")
                self.compileStatements()
                self.getNextSymbol("if statement", "}")
            else:
                self.tokenizer.backtrack()
        else:
            self.tokenizer.backtrack()

        self.file.write("</ifStatement>\n")
        return

    def compileWhile(self):
        self.file.write("<whileStatement>\n")
        self.getNextKeyword("while statement", "while")
        self.getNextSymbol("while statement", "(")
        self.compileExpression()
        self.getNextSymbol("while statement", ")")
        self.getNextSymbol("while statement", "{")
        self.compileStatements()
        self.getNextSymbol("while statement", "}")
        self.file.write("</whileStatement>\n")
        return

    def compileDo(self):
        self.file.write("<doStatement>\n")
        self.getNextKeyword("do statemnt", "do")
        self.getNextIdentifier("do statment")
        token_type = self.doAdvance("do statement")

        # differentiate between a() and a.b()
        if token_type == Token.T_SYMBOL:
            symbol = self.tokenizer.symbol()
            if symbol == "(":
                self.tokenizer.backtrack()
            elif symbol == ".":
                self.file.write(self.tokenizer.getXml())
                self.getNextIdentifier("do statement")
            else:
                throw("Unexpected symbol: {} in do statement".format(symbol))
        else:
            throw("Unexpected token type: {} in do statement".format(str(token_type)))

        self.getNextSymbol("do statement", "(")
        self.compileExpressionList()
        self.getNextSymbol("do statement", ")")
        self.getNextSymbol("do statement", ";")
        self.file.write("</doStatement>\n")
        return

    def compileReturn(self):
        self.file.write("<returnStatement>\n")
        self.getNextKeyword("return statement", "return")

        token_type = self.doAdvance("return")
        if token_type in [Token.T_IDENTIFIER, Token.T_KEYWORD]:
            self.tokenizer.backtrack()
            self.compileExpression()
        else:
            self.tokenizer.backtrack()

        self.getNextSymbol("return statement", ";")
        self.file.write("</returnStatement>\n")
        return

    def compileExpression(self):
        self.file.write("<expression>\n")
        self.compileTerm()

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("expression")
            is_op = self.tokenizer.symbol() in [
                "+", "-", "/", "*", "&", "|", "=", ">", "<"]

            if token_type == Token.T_SYMBOL and is_op:
                self.file.write(self.tokenizer.getXml())
                self.compileTerm()
            else:
                self.tokenizer.backtrack()
                break

        self.file.write("</expression>\n")
        return

    def compileTerm(self):
        self.file.write("<term>\n")
        token_type = self.doAdvance("term")

        if token_type == Token.T_INT_CONST:
            self.tokenizer.backtrack()
            self.getNextInt("term")
        elif token_type == Token.T_STRING_CONST:
            self.tokenizer.backtrack()
            self.getNextStr("term")
        elif token_type == Token.T_KEYWORD:
            self.tokenizer.backtrack()
            self.getNextKeyword("term", ["this", "false", "true", "null"])
        elif token_type == Token.T_IDENTIFIER:
            next_token_type = self.doAdvance("term")
            if next_token_type == Token.T_SYMBOL:
                symbol = self.tokenizer.symbol()
                self.tokenizer.backtrack()
                if symbol == "[":
                    self.tokenizer.backtrack()
                    self.getNextIdentifier("term")
                    self.getNextSymbol("term", "[")
                    self.compileExpression()
                    self.getNextSymbol("term", "]")
                elif symbol == "(":
                    self.tokenizer.backtrack()
                    self.getNextIdentifier("term")
                    self.getNextSymbol("term", "(")
                    self.compileExpressionList()
                    self.getNextSymbol("term", ")")
                elif symbol == ".":
                    self.tokenizer.backtrack()
                    self.getNextIdentifier("term")
                    self.getNextSymbol("term", ".")
                    self.getNextIdentifier("term")
                    self.getNextSymbol("term", "(")
                    self.compileExpressionList()
                    self.getNextSymbol("term", ")")
                else:
                    self.tokenizer.backtrack()
                    self.getNextIdentifier("term")
            else:
                self.tokenizer.backtrack()
                self.getNextIdentifier("term")
        else:
            symbol = self.tokenizer.symbol()
            if symbol == "(":
                # new expression
                self.tokenizer.backtrack()
                self.getNextSymbol("term", "(")
                self.compileExpression()
                self.getNextSymbol("term", ")")
            elif symbol in ["-", "~"]:
                self.file.write(self.tokenizer.getXml())
                self.compileTerm()
            elif symbol in [")", "]", "}"]:
                self.tokenizer.backtrack()
            else:
                throw("Unexpected symbol: {} in term".format(symbol))

        self.file.write("</term>\n")
        return

    def compileExpressionList(self):
        self.file.write("<expressionList>\n")
        token_type = self.doAdvance("expression list")
        if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == ")":
            self.tokenizer.backtrack()
        else:
            self.tokenizer.backtrack()
            self.compileExpression()

            while self.tokenizer.hasMoreTokens():
                token_type = self.doAdvance("expression list")
                if token_type == Token.T_SYMBOL:
                    symbol = self.tokenizer.symbol()
                    if symbol == ")":
                        self.tokenizer.backtrack()
                        break
                    elif symbol == ",":
                        self.file.write(self.tokenizer.getXml())
                        self.compileExpression()
                    else:
                        throw(
                            "Unexpected symbol: {} in expression list".format(symbol))
                else:
                    self.tokenizer.backtrack()
                    self.compileExpression()
        self.file.write("</expressionList>\n")
        return

class JackAnalyzer:
    def __init__(self, input_file):
        self.filename = input_file
        self.compiler = CompilationEngine()
        self.compile()
        return

    def compile(self):
        file_name = self.filename
        if not os.path.exists(file_name):
            print("[+] File not found at {}".format(file_name))
            sys.exit()

        abs_path = os.path.abspath(file_name)
        is_dir = os.path.isdir(abs_path)

        if not is_dir and not abs_path.endswith('.jack'):
            print("[+] Provided file must be a .jack file")

        if is_dir:
            glob_search = abs_path + '/*.jack'
            file_list = glob.glob(glob_search)
            for globbed_filename in file_list:
                output_filename = globbed_filename[0:-5] + "Z.xml"
                tokenizer = JackTokenizer(globbed_filename)
                output_file = open(output_filename, "w")
                self.compiler.compile(tokenizer, output_file)
                output_file.close()
        else:
            output_filename = abs_path[0:-5] + "Z.xml"
            tokenizer = JackTokenizer(abs_path)
            output_file = open(output_filename, "w")
            self.compiler.compile(tokenizer, output_file)
            output_file.close()

class JackCompiler:
    def __init__(self, input_file):
        self.filename = input_file
        self.compiler = CompilationEngine()
        self.compile()
        return

    def compile(self):
        file_name = self.filename
        if not os.path.exists(file_name):
            print("[+] File not found at {}".format(file_name))
            sys.exit()

        abs_path = os.path.abspath(file_name)
        is_dir = os.path.isdir(abs_path)

        if not is_dir and not abs_path.endswith('.jack'):
            print("[+] Provided file must be a .jack file")

        if is_dir:
            glob_search = abs_path + '/*.jack'
            file_list = glob.glob(glob_search)
            for globbed_filename in file_list:
                output_filename = globbed_filename[0:-5] + "Z.xml"
                tokenizer = JackTokenizer(globbed_filename)
                output_file = open(output_filename, "w")
                self.compiler.compile(tokenizer, output_file)
                output_file.close()
        else:
            output_filename = abs_path[0:-5] + "Z.xml"
            tokenizer = JackTokenizer(abs_path)
            output_file = open(output_filename, "w")
            self.compiler.compile(tokenizer, output_file)
            output_file.close()

if len(sys.argv) < 2:
    print("[+] Missing required argument filename")
    print("[+] Please provide either filename or directory")

file_name = sys.argv[1]
JackAnalyzer(file_name)

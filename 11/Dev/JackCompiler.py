#!/usr/bin/python3.6

import enum
import glob
import os
import sys
import re


def excepthook(type, value, traceback):
    print(value)

#sys.excepthook = excepthook


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


class Opp(enum.Enum):
    O_ADD = "add"
    O_SUB = "sub"
    O_NEG = "neg"
    O_EQ = "eq"
    O_GT = "gt"
    O_LT = "lt"
    O_AND = "and"
    O_OR = "or"
    O_NOT = "not"
    O_MUL = "call Math.multiply 2"
    O_DIV = "call Math.divide 2"


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
        index = self.varcount(kind)
        if kind in [K.K_STATIC, K.K_FIELD]:
            self.class_scope.append({
                'index': index,
                'name': name,
                'type': v_type,
                'kind': kind
            })
        else:
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
        output = "push {} {}\n".format(segment, str(index))
        self.file.write(output)
        return

    def writePop(self, segment, index):
        output = "pop {} {}\n".format(segment, str(index))
        self.file.write(output)
        return

    def writeArithmetic(self, command: Opp):
        output = "{}\n".format(command.value)
        self.file.write(output)
        return

    def writeLabel(self, label):
        output = "label {}\n".format(label)
        self.file.write(output)
        return

    def writeGoto(self, label):
        output = "goto {}\n".format(label)
        self.file.write(output)
        return

    def writeIf(self, label):
        output = "if-goto {}\n".format(label)
        self.file.write(output)
        return

    def writeFunction(self, name, nLocals):
        output = "function {} {}\n".format(name, str(nLocals))
        self.file.write(output)
        return

    def writeReturn(self):
        output = "return\n"
        self.file.write(output)
        return

    def writeCall(self, name, nArgs):
        output = "call {} {}\n".format(name, str(nArgs))
        self.file.write(output)
        return

    def close(self):
        self.file.close()
        return


class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.symbolTable = SymbolTable()
        self.tokenizer = JackTokenizer(input_file)
        self.file = open(output_file, "w")
        self.vmWriter = VMWriter(self.file)
        self.class_name = ""
        self.expression_count = 0
        self.local_count = 0
        self.class_var_count = 0
        self.loop_label_count = 0
        self.if_label_count = 0
        self.compileClass()
        #print(self.symbolTable.class_scope + self.symbolTable.subroutine_scope)
        return

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

        # self.file.write(self.tokenizer.getXml())

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

        # self.file.write(self.tokenizer.getXml())

    def getNextIdentifier(self, location, definition=False, k_type=K.K_NONE, v_type=""):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_IDENTIFIER:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_IDENTIFIER), location))

        if definition:
            self.defineVar(k_type, v_type)

        name = self.tokenizer.identifier()
        kind_of = self.symbolTable.kindof(name)
        isVar = kind_of != K.K_NONE
        index = self.symbolTable.indexof(name)
        v_type = self.symbolTable.typeof(name)

        # determine category
        if kind_of == K.K_ARG:
            category = "argument"
        elif kind_of == K.K_FIELD:
            category = "this"
        elif kind_of == K.K_STATIC:
            category = "static"
        elif kind_of == K.K_VAR:
            category = "local"
        else:
            # peek next token
            token_type = self.doAdvance("getting category")
            if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == "(":
                category = "subroutine"
            else:
                category = "class"
            self.tokenizer.backtrack()

        return {'name': name, 'category': category, 'isDefinition': definition,
               'isVar': isVar, 'index': index, 'kind': kind_of, 'type': v_type }

    def getNextKeyOrIdentifier(self, location, expected=[], definition=False, k_type=K.K_NONE, v_type=""):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        token_type = self.tokenizer.tokenType()
        if token_type == Token.T_IDENTIFIER:
            self.tokenizer.backtrack()
            self.getNextIdentifier(location, definition, k_type, v_type)
        elif token_type == Token.T_KEYWORD:
            keyword = self.tokenizer.keyWord()
            if keyword in expected:
                # self.file.write(self.tokenizer.getXml())
                self.tokenizer.getXml()
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

        # self.file.write(self.tokenizer.getXml())

    def getNextStr(self, location):
        if not self.tokenizer.hasMoreTokens():
            throw("Unexpected EOF! Expecting in {}".format(location))
        self.tokenizer.advance()
        if not self.tokenizer.tokenType() == Token.T_STRING_CONST:
            throw("Syntax Error! Expecting type: {} in {}".format(
                str(Token.T_STRING_CONST), location))

        # self.file.write(self.tokenizer.getXml())

    def defineVar(self, k_type, v_type):
        # declare in symbol table, then write to output
        self.tokenizer.backtrack()
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
        self.getNextKeyword("class declaration", "class")
        details = self.getNextIdentifier("class declaration")
        self.class_name = details['name']
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
        return

    def compileClassVarDesc(self):
        self.getNextKeyword("class var declaration", ["field", "static"])
        # hacky fix for getting type :/, didn't wanna fix it
        v_type = self.tokenizer.file_list[self.tokenizer.current_index]
        # get kind
        kind = self.tokenizer.keyWord()

        if kind == "static":
            kind = K.K_STATIC
        else:
            kind = K.K_FIELD

        self.getNextKeyOrIdentifier("class var declaration", ["int", "boolean", "char"])
        self.getNextIdentifier("class var declaration", True, kind, v_type)
        self.class_var_count += 1
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
                    self.getNextIdentifier("class var declaration", True, kind, v_type)
                    self.class_var_count += 1
                else:
                    throw(
                        "Syntax Error! Unexpected symbol: {} in class var declaration".format(symbol))

        self.getNextSymbol("class var declaration", ";")
        return

    def compileSubroutine(self):
        self.loop_label_count = 0
        self.if_label_count = 0
        self.symbolTable.startSubroutine()
        self.local_count = 0
        self.getNextKeyword("subroutine declaration", [
                            "function", "method", "constructor"])
        
        self.function_type = self.tokenizer.keyWord()

        self.getNextKeyOrIdentifier("subroutine declaration", [
                                    "int", "void", "boolean", "char"])

        if self.function_type == "method":
            self.defineVar(K.K_ARG, self.class_name)

        details = self.getNextIdentifier("subroutine declaration")
        self.getNextSymbol("subroutine declaration", "(")
        self.compileParameterList()
        self.getNextSymbol("subroutine declaration", ")")
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

        # declare function
        name = self.class_name + "." + details['name']
        var_count = self.symbolTable.varcount(K.K_VAR)
        self.vmWriter.writeFunction(name, var_count)

        if self.function_type == "constructor":
            count = self.symbolTable.varcount(K.K_FIELD)
            self.vmWriter.writePush("constant", count)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        elif self.function_type == "method":
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)

        self.compileStatements()
        self.getNextSymbol("subroutine body", "}")
        return

    def compileParameterList(self):
        token_type = self.doAdvance("parameter list")

        if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == ")":
            self.tokenizer.backtrack()
        else:
            self.tokenizer.backtrack()
            self.getNextKeyOrIdentifier(
                "parameter list", ["int", "boolean", "char"])

            v_type = self.tokenizer.identifier()
            self.getNextIdentifier("paramenter list", True, K.K_ARG, v_type)

            while self.tokenizer.hasMoreTokens():
                token_type = self.doAdvance("parameter list")

                if not token_type == Token.T_SYMBOL:
                    throw("Unexpected token type: {} in parameter list".format(
                        str(token_type)))
                else:
                    symbol = self.tokenizer.symbol()
                    if symbol == ",":
                        # self.file.write(self.tokenizer.getXml())
                        self.getNextKeyOrIdentifier(
                            "parameter list", ["int", "boolean", "char"])

                        v_type = self.tokenizer.identifier()
                        self.getNextIdentifier("parameter list", True, K.K_ARG, v_type)
                    elif symbol == ")":
                        self.tokenizer.backtrack()
                        break
                    else:
                        throw("Unexpected symbol: {} in parameter list".format(
                            str(symbol)))
        
        return

    def compileVarDec(self):
        self.getNextKeyword("var declaration", "var")
        # hacky fix for getting type :/, didn't wanna fix it
        v_type = self.tokenizer.file_list[self.tokenizer.current_index]
        self.getNextKeyOrIdentifier(
            "var declaration", ["boolean", "int", "char"])
        self.getNextIdentifier("var declaration", True, K.K_VAR, v_type)
        self.local_count += 1

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
                    # self.file.write(self.tokenizer.getXml())
                    self.getNextIdentifier(
                        "var declaration", True, K.K_VAR, v_type)
                    self.local_count += 1
                else:
                    throw(
                        "Syntax Error! Unexpected symbol: {} in class var declaration".format(symbol))

        self.getNextSymbol("var declaration", ";")
        return

    def compileStatements(self):
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
        return

    def compileLet(self):
        self.getNextKeyword("let statement", "let")
        details = self.getNextIdentifier("let statement")
        segment = details['category']
        index = details['index']
        is_array = False

        # deal with a = x vs a[1] = x
        token_type = self.doAdvance("let statement")
        if token_type == Token.T_SYMBOL:
            symbol = self.tokenizer.symbol()
            if symbol == "[":
                self.compileExpression()
                self.vmWriter.writePush(segment, index)
                self.getNextSymbol("let statement", "]")
                self.vmWriter.writeArithmetic(Opp.O_ADD)
                is_array = True
            elif symbol == "=":
                self.tokenizer.backtrack()
            else:
                throw("Unexpected symbol: {} in let statement".format(symbol))
        else:
            throw("Unexepected token type: {}".format(str(token_type)))

        self.getNextSymbol("let statement", "=")
        self.compileExpression()
        self.getNextSymbol("let statement", ";")

        if is_array:
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            self.vmWriter.writePop(segment, index)
        return

    def compileIf(self):
        if_label = "IF_TRUE" + str(self.if_label_count)
        else_label = "IF_FALSE" + str(self.if_label_count)
        end_label = "IF_END" + str(self.if_label_count)
        self.if_label_count += 1
        self.getNextKeyword("if statement", "if")
        self.getNextSymbol("if statement", "(")
        self.compileExpression()
        self.vmWriter.writeIf(if_label)
        self.vmWriter.writeGoto(else_label)
        self.vmWriter.writeLabel(if_label)
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
                self.vmWriter.writeGoto(end_label)
                self.vmWriter.writeLabel(else_label)
                self.getNextKeyword("if statement", "else")
                self.getNextSymbol("if statement", "{")
                self.compileStatements()
                self.getNextSymbol("if statement", "}")
                self.vmWriter.writeLabel(end_label)
            else:
                self.tokenizer.backtrack()
                self.vmWriter.writeLabel(else_label)
        else:
            self.tokenizer.backtrack()
            self.vmWriter.writeLabel(else_label)

        return

    def compileWhile(self):
        label_start = "WHILE_EXP" + str(self.loop_label_count)
        label_end = "WHILE_END" + str(self.loop_label_count)
        self.loop_label_count += 1

        self.getNextKeyword("while statement", "while")
        self.getNextSymbol("while statement", "(")
        self.vmWriter.writeLabel(label_start)
        self.compileExpression()
        self.vmWriter.writeArithmetic(Opp.O_NOT)
        self.vmWriter.writeIf(label_end)
        self.getNextSymbol("while statement", ")")
        self.getNextSymbol("while statement", "{")
        self.compileStatements()
        self.vmWriter.writeGoto(label_start)
        self.vmWriter.writeLabel(label_end)
        self.getNextSymbol("while statement", "}")
        return

    def compileDo(self):
        self.getNextKeyword("do statement", "do")
        details = self.getNextIdentifier("do statment")
        subroutine_name = details['name']
        instance_type = details['type']
        this_index = details['index']
        this_segment = details['category']
        name = self.class_name + "." + subroutine_name
        is_this_class_method = True
        is_instance_method = False
        token_type = self.doAdvance("do statement")

        # differentiate between a() and a.b()
        if token_type == Token.T_SYMBOL:
            symbol = self.tokenizer.symbol()
            if symbol == "(":
                self.tokenizer.backtrack()
            elif symbol == ".":
                details = self.getNextIdentifier("do statement")
                if instance_type == "":
                    instance_type = subroutine_name
                else:
                    is_instance_method = True
                name = instance_type + "." + details['name']
                is_this_class_method = False
            else:
                throw("Unexpected symbol: {} in do statement".format(symbol))
        else:
            throw("Unexpected token type: {} in do statement".format(str(token_type)))

        if is_this_class_method:
            self.vmWriter.writePush("pointer", 0)
            self.expression_count += 1
        elif is_instance_method:
            self.vmWriter.writePush(this_segment, this_index)

        self.getNextSymbol("do statement", "(")
        self.compileExpressionList()
        self.getNextSymbol("do statement", ")")
        self.getNextSymbol("do statement", ";")
        
        if is_this_class_method or is_instance_method:
            self.expression_count += 1
            
        self.vmWriter.writeCall(name, self.expression_count)
        self.vmWriter.writePop("temp", 0)

        return

    def compileReturn(self):
        self.getNextKeyword("return statement", "return")

        token_type = self.doAdvance("return")

        if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == ";":
            self.tokenizer.backtrack()
            self.vmWriter.writePush("constant", 0)
        else:
            self.tokenizer.backtrack()
            self.compileExpression()

        self.getNextSymbol("return statement", ";")
        self.vmWriter.writeReturn()
        return

    def compileExpression(self):
        self.compileTerm()

        while self.tokenizer.hasMoreTokens():
            token_type = self.doAdvance("expression")
            symbol = self.tokenizer.symbol()
            is_op = symbol in [
                "+", "-", "/", "*", "&", "|", "=", ">", "<"]

            mapping = {
                "+": Opp.O_ADD, "-": Opp.O_SUB,
                "/": Opp.O_DIV, "*": Opp.O_MUL,
                "&": Opp.O_AND, "|": Opp.O_OR,
                ">": Opp.O_GT, "<": Opp.O_LT,
                "=": Opp.O_EQ
            }

            if token_type == Token.T_SYMBOL and is_op:
                self.compileTerm()
                op = mapping[symbol]
                self.vmWriter.writeArithmetic(op)
            else:
                self.tokenizer.backtrack()
                break

        # self.file.write("</expression>\n")
        return

    def compileTerm(self):
        token_type = self.doAdvance("term")

        if token_type == Token.T_INT_CONST:
            self.tokenizer.backtrack()
            self.getNextInt("term")
            intval = self.tokenizer.intVal()
            self.vmWriter.writePush("constant", intval)
        elif token_type == Token.T_STRING_CONST:
            self.tokenizer.backtrack()
            self.getNextStr("term")
            strconst = self.tokenizer.stringVal()
            strlen = len(strconst)
            self.vmWriter.writePush("constant", strlen)
            self.vmWriter.writeCall("String.new", 1)
            for char in strconst:
                code = ord(char)
                self.vmWriter.writePush("constant", code)
                self.vmWriter.writeCall("String.appendChar", 2)
        elif token_type == Token.T_KEYWORD:
            self.tokenizer.backtrack()
            self.getNextKeyword("term", ["this", "false", "true", "null"])
            keyword = self.tokenizer.keyWord()
            if keyword == "true":
                self.vmWriter.writePush("constant", 1)
                self.vmWriter.writeArithmetic(Opp.O_NEG)
            elif keyword == "false" or keyword == "null":
                self.vmWriter.writePush("constant", 0)
            elif keyword == "this":
                self.vmWriter.writePush("pointer", 0)
        elif token_type == Token.T_IDENTIFIER:
            next_token_type = self.doAdvance("term")
            if next_token_type == Token.T_SYMBOL:
                symbol = self.tokenizer.symbol()
                self.tokenizer.backtrack()
                if symbol == "[":
                    # handle array accessing
                    self.tokenizer.backtrack()
                    first_var = self.getNextIdentifier("term")
                    self.tokenizer.backtrack()
                    self.getNextIdentifier("term")
                    self.getNextSymbol("term", "[")
                    self.compileExpression()
                    self.getNextSymbol("term", "]")
                    self.vmWriter.writePush(first_var['category'], first_var['index'])
                    self.vmWriter.writeArithmetic(Opp.O_ADD)
                    self.vmWriter.writePop("pointer", 1)
                    self.vmWriter.writePush("that", 0)
                elif symbol == "(":
                    # handle subroutine call
                    self.tokenizer.backtrack()
                    details = self.getNextIdentifier("term")
                    self.vmWriter.writePush("pointer", 0)
                    self.getNextSymbol("term", "(")
                    self.compileExpressionList()
                    self.getNextSymbol("term", ")")
                    name = self.class_name + "." + details['name']  
                    self.vmWriter.writeCall(name, self.expression_count)
                elif symbol == ".":
                    # handle subroutine call
                    self.tokenizer.backtrack()
                    details = self.getNextIdentifier("term")
                    class_name = details['type']
                    this_segment = details['category']
                    this_index = details['index']
                    is_instance_method = False
                    if class_name == "":
                        class_name = details['name']
                    else:
                        is_instance_method = True
                        self.vmWriter.writePush(this_segment, this_index)
                    self.getNextSymbol("term", ".")
                    details = self.getNextIdentifier("term")
                    name = class_name + "." + details['name']
                    self.getNextSymbol("term", "(")
                    self.compileExpressionList()
                    self.getNextSymbol("term", ")")
                    if is_instance_method:
                        self.expression_count += 1
                    self.vmWriter.writeCall(name, self.expression_count)
                else:
                    self.tokenizer.backtrack()
                    details = self.getNextIdentifier("term")
                    segment = details['category']
                    index = details['index']
                    self.vmWriter.writePush(segment, index)
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
                # self.file.write(self.tokenizer.getXml())
                self.compileTerm()
                op = Opp.O_NEG
                if symbol == "~":
                    op = Opp.O_NOT
                self.vmWriter.writeArithmetic(op)
            elif symbol in [")", "]", "}"]:
                self.tokenizer.backtrack()
            else:
                throw("Unexpected symbol: {} in term".format(symbol))

        # self.file.write("</term>\n")
        return

    def compileExpressionList(self):
        self.expression_count = 0
        token_type = self.doAdvance("expression list")
        if token_type == Token.T_SYMBOL and self.tokenizer.symbol() == ")":
            self.tokenizer.backtrack()
        else:
            self.tokenizer.backtrack()
            self.compileExpression()
            self.expression_count += 1

            while self.tokenizer.hasMoreTokens():
                token_type = self.doAdvance("expression list")
                if token_type == Token.T_SYMBOL:
                    symbol = self.tokenizer.symbol()
                    if symbol == ")":
                        self.tokenizer.backtrack()
                        break
                    elif symbol == ",":
                        self.expression_count += 1
                        self.compileExpression()
                    else:
                        throw(
                            "Unexpected symbol: {} in expression list".format(symbol))
                else:
                    self.tokenizer.backtrack()
                    self.compileExpression()
        return


class JackCompiler:
    def __init__(self, input_file):
        self.filename = input_file
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
                output_filename = globbed_filename[0:-5] + ".vm"
                CompilationEngine(globbed_filename, output_filename)
        else:
            output_filename = abs_path[0:-5] + ".vm"
            CompilationEngine(abs_path, output_filename)


if len(sys.argv) < 2:
    print("[+] Missing required argument filename")
    print("[+] Please provide either filename or directory")

file_name = sys.argv[1]
JackCompiler(file_name)

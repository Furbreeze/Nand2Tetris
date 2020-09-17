self.tokenizer.advance()
            token_type = self.tokenizer.tokenType()

            if token_type == Token.T_KEYWORD:
                keyword = self.tokenizer.keyWord()
                if keyword in ["method", "function", "constructor"]:
                    self.compileSubroutine()
                elif keyword in ["field", "static"]:
                    self.compileClassVarDesc()
                else:
                    throw("Unexpected keyword: {} in class declaration".format(keyword))
            elif token_type == Token.T_SYMBOL:
                symbol = self.tokenizer.symbol()
                if symbol == "}":
                    if self.tokenizer.hasMoreTokens():
                        throw("Unexpected } in class declaration")
                    else:
                        self.file.write(self.tokenizer.getXml())
                else:
                    throw("Unexpected symbol: {} in class declaration".format(symbol))
            elif token_type == Token.T_IDENTIFIER:
                identifier = self.tokenizer.identifier()
                throw(
                    "Unexpected identifier: {} in class declaration".format(identifier))
            elif token_type == Token.T_INT_CONST:
                int_const = self.tokenizer.intVal()
                throw("Unexpected intVal: {} in class declaration".format(
                    str(int_const)))
            elif token_type == Token.T_STRING_CONST:
                str_const = self.tokenizer.stringVal()
                throw("Unexpected stringVal: {} in class declaration".format(str_const))
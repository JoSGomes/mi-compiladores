PATH_FILES = "./files"

typesVar = ["int", "real", "boolean", "string"]
typesValue = ["NRO", "CAC"]
valueTrueFalse = ["true", "false"]

class SintaxAnalizer(): 
    def __init__(self, tokens):
        self.tokens = tokens  
        self.lookahead = tokens[0]
        self.tokensCounter = 1
        self.previousTokenLine = self.lookahead["line"]
        self.currentTokenLine = self.lookahead["line"]
        self.errors = []
        self.outputFile = None

    def matchTokenType(self, tokenType: str | list, doubt: bool = False) -> bool:
        if type(tokenType) == list:
            for t in tokenType:
                if t in self.lookahead["type"]:
                    self.nextLookahead()
                    return True
            if not doubt:
                self.saveErrorType(tokenType, self.lookahead["type"], self.lookahead["line"])
                self.nextLookahead()
            return False
            
        if tokenType in self.lookahead["type"]:
            self.nextLookahead()
            return True
        else:
            if not doubt:
                self.saveErrorType(tokenType, self.lookahead["type"], self.lookahead["line"])
                self.nextLookahead()
            return False
        
    def match(self, terminal: str | list, doubt: bool = False) -> bool:
        if type(terminal) == list:
            for t in terminal:
                if t in self.lookahead["value"]:
                    self.nextLookahead()
                    return True
            if not doubt:
                self.saveError(terminal, self.lookahead["value"], self.lookahead["line"])
                self.nextLookahead()
            return False
                
        if terminal in self.lookahead["value"]:
            self.nextLookahead()
            return True
        else:
            if not doubt:
                self.saveError(terminal, self.lookahead["value"], self.lookahead["line"])
                self.nextLookahead()
            return False
        
    def nextLookahead(self):
        if self.tokensCounter < len(self.tokens):
            self.previousTokenLine = self.lookahead["line"]
            self.lookahead = self.tokens[self.tokensCounter]
            self.currentTokenLine = self.lookahead["line"]
            self.tokensCounter += 1
        else:
            print("EOF, Arquivo analisado com sucesso!")

    def saveError(self, expected: str | list, findOut: str, line: int):
        self.errors.append("Na linha %i, esperava %s e encontrou %s." % (line, expected, findOut))
    
    def saveErrorType(self, expected: str | list, findOut: str, line: int):
        self.errors.append("Erro de tipo: Na linha %i, esperava %s e encontrou %s." % (line, expected, findOut))

    def writeTokensAndErrors(self):
        for token in self.tokens:
            self.outputFile.write("%i. <%s, %s>\n" % (token["line"], token["type"], token["value"]))

        if len(self.errors) == 0:
            self.outputFile.write("\n############ Arquivo foi analisado com sucesso! ############")
        else:
            self.outputFile.write("\n############ !!! Erros sintáticos encontrados !!! ############\n\n")
            for error in self.errors:
                self.outputFile.write(error + "\n")
    #----------------------------------------------------------------

    def _type(self):
        self.match(typesVar)
 
    #----------------------------------------------------------------

    def _constsBlock(self):
        self.match("const")
        self.match("{")
        self._consts()

    def _consts(self):
        if not self.match("}", True):
            self._const()
            self._consts()

    def _const(self):
        self._type()
        self._constAttribution()
        self._multipleConsts()

    def _constAttribution(self):
        self.matchTokenType("IDE")
        self.match("=")
        self._attribution()

    def _attribution(self):
        if not self.matchTokenType(typesValue, True):
            if not self.match(valueTrueFalse, True):
                self.saveErrorType(typesValue + valueTrueFalse, self.lookahead["type"] + ": " + self.lookahead["value"], self.lookahead["line"])

    def _multipleConsts(self):
        if not self.match(";", True) and self.previousTokenLine == self.currentTokenLine:
            self.match(",")
            self._constAttribution()
            self._multipleConsts() 

    #----------------------------------------------------------------
    
    def _variablesBlock(self):
        self.match("variables")
        self.match("{")
        self._variables()

    def _variables(self):
        if not self.match("}", True):
            self._variable()
            self._variables()

    def _variable(self):
        self._type()
        self._decVariable()         
        self._multipleVariablesLine()

    def _decVariable(self):
        self.matchTokenType("IDE")
        self._dimensions()

    def _dimensions(self):
        if self.match("[", True):
            self._sizeDimension()
            self.match("]")
            self._dimensions()
    
    def _sizeDimension(self):
        if not self.matchTokenType("IDE", True):
            self.matchTokenType("NRO")

    def _multipleVariablesLine(self):
        result = self.match(";", True)
        if not result and self.previousTokenLine == self.currentTokenLine:
            self.match(",")
            self._decVariable()
            self._multipleVariablesLine()
        elif not result and not self.previousTokenLine == self.currentTokenLine:
            self.saveError(";", "\\n", self.previousTokenLine)

    #----------------------------------------------------------------

    def _objectsBlock(self):
        self.match("objects")
        self.match("{")
        #self._objects()
        self.match("}")

    #----------------------------------------------------------------

    def _main(self):
        self.match("class") #colocar class_block
        self.match("main")
        self.match("{")
        self._initMain()

    def _initMain(self):
        self._bodyBlocks()
        self._mainMethods()
        self.match("}")

    def _bodyBlocks(self):
        self._variablesBlock()
        self._objectsBlock() 

    def _mainMethods(self):
        self.match("methods")
        self.match("{")
        #self._mainMethodsBody()
        self.match("}")

    # def _mainMethodsBody(self):
    #     self._mainType()
    #     self.match("main")
    #     self.match("(")
    #     self.match(")")
    #     self.match("{")
    #     self._methodBody()
    #     self._methods() #TODO: implement this all gram
    
    # def _methodBody(self): 
    #     self._variablesBlock()
    #     self.objectsBlock()
    #     self._commandsMethodBody()
    
    # def _commandsMethodBody(self): #TODO: implement this all gram
    #     self.match("return")
    #     self._return()
    #     self.match(";")
    #     self.match("}")
    
    # def _return(self): #TODO: implement this all gram
    #     self._value()

    # def _value(self): #TODO: implement this all gram
    #     self._type()

    def _mainType(self):
        if not self._type():
            self.match("void")
            
    #----------------------------------------------------------------


    def analize(self):
        self.outputFile = open(PATH_FILES + "/sintatico_saida.txt", "w", encoding="utf8")

        self._constsBlock()
        self._variablesBlock() 
        self._main()

        self.writeTokensAndErrors()
        self.outputFile.close()
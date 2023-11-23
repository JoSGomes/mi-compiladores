from logger import Logger

PATH_FILES = "./files"

typesVar = ["int", "real", "boolean", "string"]
typesValue = ["NRO", "CAC"]
valueTrueFalse = ["true", "false"]

class SintaxAnalizer(): 
    def __init__(self, tokens: dict, outputDir: str):
        self.tokens = tokens  
        self.lookahead = tokens[0]
        self.tokensCounter = 1
        self.previousTokenLine = self.lookahead["line"]
        self.currentTokenLine = self.lookahead["line"]
        self.errors = []
        self.outputFile = None
        self.outputDir = outputDir
        self.logger = Logger("sintax_analizer")

    def matchTokenType(self, tokenType: str | list, doubt: bool = False, _pass: bool = True) -> bool:
        if type(tokenType) == list:
            for t in tokenType:
                if t in self.lookahead["type"]:
                    if _pass:
                        self.nextLookahead()
                    return True
            if not doubt:
                self.saveErrorType(tokenType, self.lookahead["type"], self.lookahead["line"])
                self.nextLookahead()
            return False
            
        if tokenType in self.lookahead["type"]:
            if _pass:
                self.nextLookahead()
            return True
        else:
            if not doubt:
                self.saveErrorType(tokenType, self.lookahead["type"], self.lookahead["line"])
                self.nextLookahead()
            return False
        
    def match(self, terminal: str | list, doubt: bool = False, _pass: bool = True) -> bool:
        if type(terminal) == list:
            for t in terminal:
                if t in self.lookahead["value"]:
                    if _pass: #É pra passar o lookahead? -> se for só uma verificação não é pra passar (viria _pass = False)
                        self.nextLookahead()
                    return True
            if not doubt:
                self.saveError(terminal, self.lookahead["value"], self.lookahead["line"])
                self.nextLookahead()
            return False
                
        if terminal in self.lookahead["value"]:
            if _pass:
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
        self.logger.I("constsBlock")
        self.match("const")
        self.match("{")
        self._consts()

    def _consts(self):
        self.logger.I("consts")
        if not self.match("}", True):
            self._const()
            self._consts()

    def _const(self):
        self.logger.I("const")
        self._type()
        self._constAttribution()
        self._multipleConsts()

    def _constAttribution(self):
        self.logger.I("_constAttribution")
        self.matchTokenType("IDE")
        self.match("=")
        self._attribution()

    def _attribution(self):
        self.logger.I("_attribution")
        if not self.matchTokenType(typesValue, True):
            if not self.match(valueTrueFalse, True):
                self.saveErrorType(typesValue + valueTrueFalse, self.lookahead["type"] + ": " + self.lookahead["value"], self.lookahead["line"])

    def _multipleConsts(self):
        self.logger.I("_multipleConsts")
        if not self.match(";", True):
            self.match(",")
            self._constAttribution()
            self._multipleConsts() 

    #----------------------------------------------------------------
    
    def _variablesBlock(self):
        self.logger.I("_variablesBlock")
        self.match("variables")
        self.match("{")
        self._variables()

    def _variables(self):
        self.logger.I("_variables")
        if not self.match("}", True):
            self._variable()
            self._variables()

    def _variable(self):
        self.logger.I("_variable")
        self._type()
        self._decVariable()         
        self._multipleVariablesLine()

    def _decVariable(self):
        self.logger.I("_decVariable")
        self.matchTokenType("IDE")
        self._dimensions()

    def _dimensions(self):
        self.logger.I("_dimensions")
        if self.match("[", True):
            self._sizeDimension()
            self.match("]")
            self._dimensions()
    
    def _sizeDimension(self):
        self.logger.I("_sizeDimension")
        if not self.matchTokenType("IDE", True):
            self.matchTokenType("NRO")

    def _multipleVariablesLine(self):
        self.logger.I("_multipleVariablesLine")
        result = self.match(";", True)
        if not result:
            self.match(",")
            self._decVariable()
            self._multipleVariablesLine()
        elif not result:
            self.saveError(";", "\\n", self.previousTokenLine)

    #----------------------------------------------------------------

    def _objectsBlock(self):
        self.logger.I("_objectsBlock")
        self.match("objects")
        self.match("{")
        self._objects()

    def _objects(self):
        self.logger.I("_objects")
        if not self.match("}", True):
            self._object()
            self._objects()

    def _object(self):
        self.logger.I("_object")
        self.matchTokenType("IDE")
        self._decVariable()
        self._multipleObjects()
    
    def _multipleObjects(self):
        self.logger.I("_multipleObjects")
        if not self.match(";", True):
            self._decVariable()
            self._multipleObjects()

    #----------------------------------------------------------------

    def _classBlock(self):
        self.logger.I("_classBlock")
        self.match("class")
        self._ideClass()

    def _ideClass(self):
        self.logger.I("_ideClass")
        if self.match("main", True, False):
            self._main()
        elif self.matchTokenType("IDE", True):
            self._extends()
        else:
            self.saveError(['main', 'IDE'], self.lookahead, self.currentTokenLine)
            self.nextLookahead()

    def _extends(self):
        self.logger.I("_extends")
        if self.match("{", True, False):
            self._startClassBlock()
        elif self.match("extends", True):
            self.matchTokenType("IDE")
            self._startClassBlock()
        else:
            self.saveError(['{', 'extends'], self.lookahead, self.currentTokenLine)
            self.nextLookahead()

    def _startClassBlock(self):
        self.logger.I("_startClassBlock")
        self.match("{")
        self._initClass()
    
    def _initClass(self):
        self.logger.I("_initClass")
        self._bodyBlocks()
        self._methodsBlock()
        self._constructor()

    def _constructor(self):
        self.logger.I("_constructor")
        self.match("constructor")
        self.match("(")
        self._decParametersConstructor()#
        self.match(")")
        self.match("{")
        self._variablesBlock()
        self._objectsBlock()
        self._commands()
        self.match("}")
        self._endClass()

    def _endClass(self):
        self.logger.I("_endClass")
        self.match("}")
        self._classBlock()

    #----------------------------------------------------------------
    def _main(self):
        self.logger.I("_main")
        self.match("class") #colocar class_block
        self.match("main")
        self.match("{")
        self._initMain()

    def _initMain(self):
        self.logger.I("_initMain")
        self._bodyBlocks()
        self._mainMethods()
        self.match("}")

    def _bodyBlocks(self):
        self.logger.I("_bodyBlocks")
        self._variablesBlock()
        self._objectsBlock() 

    def _mainMethods(self):
        self.logger.I("_mainMethods")
        self.match("methods")
        self.match("{")
        self._mainMethodsBody()
        self.match("}")

    def _mainMethodsBody(self):
        self.logger.I("_mainMethodsBody")
        self._mainType()
        self.match("main")
        self.match("(")
        self.match(")")
        self.match("{")
        self._methodBody()
        self._methods()
    
    def _methodBody(self): 
        self.logger.I("_methodBody")
        self._variablesBlock()
        self.objectsBlock()
        self._commandsMethodBody()
    
    def _commandsMethodBody(self):
        self.logger.I("_commandsMethodBody")
        self._commands()
        self.match("return")        
        self._return()#
        self.match(";")
        self.match("}")
        
    
    def _commands(self):
        self.logger.I("_commands")
        if self.match(['print', 'read', 'if', 'for', 'IDE'], True, False):        
            self._command()
            self._commands()

    def _command(self):
        self.logger.I("_command")
        if self.match('print', True, False):
            self._printBegin()
        elif self.match('read', True, False):
            self._readBegin()
        elif self.match('if', True, False):
            self._if()
        elif self.match('for', True, False):
            self._for()
        elif self.matchTokenType('IDE', True, False):
            self._objectAccessOrAssignment()
            self.match(';')
     #----------------------------------------------------------------
    def _printBegin(self):
        self.logger.I("_printBegin")
        self.match('print')
        self.match('(')
        self._printEnd()

    def _printEnd(self):
        self.logger.I("_printEnd")
        self._printParameter()
        self.match(')')
        self.match(';')

    def _printParameter(self):
        self.logger.I("_printParameter")
        if self.matchTokenType('IDE', True, False):
            self._decObjectAttributeAccess() 
        elif self.matchTokenType('CAC', True):
            return
        elif self.matchTokenType('NRO', True):
            return
        self.saveError(['IDE', 'CAC', 'NRO'], self.lookahead, self.currentTokenLine)
        self.nextLookahead()
    #----------------------------------------------------------------
    def _decObjectAttributeAccess(self):
        self.logger.I("_decObjectAttributeAccess")
        self.matchTokenType('IDE')
        self._dimensions()
        self._endObjectAttributeAccess()

    def _endObjectAttributeAccess(self):
        self.logger.I("_endObjectAttributeAccess")
        if self.match('.', True):
            self._multipleObjectAttributeAccess()

    def _multipleObjectAttributeAccess(self):
        self.logger.I("_multipleObjectAttributeAccess")
        self._decVariable()
        self._endObjectAttributeAccess()

    def _objectMethodOrObjectAccess(self):
        self.logger.I("_objectMethodOrObjectAccess")
        self.objectMethodOrObjectAccessOrPart()
    
    def _objectMethodOrObjectAccessOrPart(self):
        self.logger.I("_objectMethodOrObjectAccessOrPart")
        self._decObjectAttributeAccess()
        self._optionalObjectMethodAccess()
    
    def _optionalObjectMethodAccess(self):
        self.logger.I("_optionalObjectMethodAccess")
        if self.match('->', True):
            self._objectMethodAccessEnd()            

    def _objectMethodAccessEnd(self):
        self.logger.I("_objectMethodAccessEnd")
        self.match('->')
        self._ideOrConstructor()
        self.match('(')
        self._parameters()
        self.match(')')
    
    def _ideOrConstructor(self):
        self.logger.I("_ideOrConstructor")
        if self.match('constructor', True):
            return
        elif self.matchTokenType('IDE', True):
            return
        self.saveError(['constructor', 'IDE'], self.lookahead, self.currentTokenLine)
        self.nextLookahead()
    #----------------------------------------------------------------
    def _parameters(self):
        self.logger.I("_parameters")
        self._value()#
        self._multParameters()#

    #----------------------------------------------------------------
    # def _return(self): #TODO: implement this all gram
    #     self._value()

    # def _value(self): #TODO: implement this all gram
    #     self._type()

    def _mainType(self):
        if not self._type():
            self.match("void")
            return
        
        self.saveError(['void', typesVar], self.lookahead, self.currentTokenLine)
    #----------------------------------------------------------------


    def analize(self):
        self.outputFile = open(self.outputDir, "w", encoding="utf8")

        self._constsBlock()
        self._variablesBlock() 
        self._main()

        self.writeTokensAndErrors()
        self.logger.closeLogs()
        self.outputFile.close()
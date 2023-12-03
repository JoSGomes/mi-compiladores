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
        self.initLineOfIgnoredTokens = None
        self.logger = Logger("sintax_analizer")

    def matchTokenType(self, tokenType: str | list, doubt: bool = False, _pass: bool = True) -> bool:
        if type(tokenType) == list:
            for t in tokenType:
                if t in self.lookahead["type"]:
                    if _pass:
                        self.nextLookahead()
                    return True
            if not doubt:
                self.saveError(tokenType, self.lookahead["value"], self.currentTokenLine)
                self.nextLookahead()
            return False
            
        if tokenType in self.lookahead["type"]:
            if _pass:
                self.nextLookahead()
            return True
        else:
            if not doubt:
                self.saveError(tokenType, self.lookahead["value"], self.currentTokenLine)
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
    
    def _program(self):
        self.logger.I("_program")
        self._constsBlock()
        self._variablesBlock()
        self._classBlock()

    #----------------------------------------------------------------

    def _type(self):
        self.match(typesVar, True)
 
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
                self.saveError(typesValue + valueTrueFalse, self.lookahead["value"], self.currentTokenLine)

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
            self.saveError(['main', 'IDE'], self.lookahead["value"], self.currentTokenLine)
            self.nextLookahead()

    def _extends(self):
        self.logger.I("_extends")
        if self.match("{", True, False):
            self._startClassBlock()
        elif self.match("extends", True):
            self.matchTokenType("IDE")
            self._startClassBlock()
        else:
            self.saveError(['{', 'extends'], self.lookahead["value"], self.currentTokenLine)
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
        self._decParametersConstructor()
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

    def _decParametersConstructor(self):
        self.logger.I("_decParametersConstructor")
        if self.match(typesVar, True, False) or self.matchTokenType('IDE', True, False):
            self._multParamConstructor()
            self._multDecParametersConstructor()#
            return
        
    def _multParamConstructor(self):
        self.logger.I("_multParamConstructor")
        if self.match(typesVar, True, False):
            self._variableParam()
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectParam()
            return

        self.saveError(typesVar + 'IDE', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _multDecParametersConstructor(self):
        self.logger.I("_multDecParametersConstructor")
        if self.match(',', True, True):
            self._multParamConstructor()
            self._multDecParametersConstructor()
            return
        
    def _variableParam(self):
        self.logger.I("_variableParam")
        self.match(typesVar)
        self.matchTokenType('IDE')

    def _objectParam(self):
        self.logger.I("_objectParam")
        self.matchTokenType('IDE')
        self.matchTokenType('IDE')

    #----------------------------------------------------------------

    def _methodsBlock(self):
        self.logger.I("_methodsBlock")
        self.match('methods')
        self.match('{')
        self._methods()
        self.match('}')

    def _methods(self):
        self.logger.I("_methods")
        if self.match(['void','IDE'] + typesVar, True, False):
            self._method()
            self._methods()
            return
        
    def _method(self):
        self.logger.I("_method")
        self._types()
        self.matchTokenType('IDE')
        self.match('(')
        self._decParameters()

    def _types(self):
        self.logger.I("types")
        if self.match('void', True, True):
            return
        elif self.match(typesVar + ['IDE'], True, False):
            self._typesVariables()
            return
        
        self.saveError(typesVar + 'IDE' + 'void', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _typesVariables(self):
        self.logger.I("_typesVariables")
        if self.match(typesVar, True, True):
            return
        elif self.matchTokenType('IDE', True, True):
            return
        
        self.saveError(typesVar + 'IDE', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _decParameters(self):
        self.logger.I("_decParameters")
        if self.match(typesVar, True, False):
            self._variableParam()
            self._multDecParameters()#
        elif self.matchTokenType('IDE', True, False):
            self._objectParam()
            self._multDecParameters()
        elif self.match(')', True, False):
            self._endDecParameters()#

    def _multDecParameters(self):
        self.logger.I("_multDecParameters")
        if self.match(',', True, True):
            self._typesVariables()
            self.matchTokenType('IDE')
            self._multDecParameters()
            return
        elif self.match(')', True, False):
            self._endDecParameters()
            return

        self.saveError([',', ')'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _endDecParameters(self):
        self.logger.I("_endDecParameters")
        self.match(')')
        self.match('{')
        self._methodBody()

    #----------------------------------------------------------------
    def _main(self):
        self.logger.I("_main")
        self.match("main")
        self.match("{")
        self._initMain()

    def _initMain(self):
        self.logger.I("_initMain")
        self._bodyBlocks()
        self._mainMethods()

        numberBeforeLastMatch = self.lookahead["line"]
        self.match("}")
        numberAfterLastMatch = self.lookahead["line"]
        if numberBeforeLastMatch != numberAfterLastMatch:
            self.initLineOfIgnoredTokens = self.lookahead

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
        self._objectsBlock()
        self._commandsMethodBody()
    
    def _commandsMethodBody(self):
        self.logger.I("_commandsMethodBody")
        self._commands()
        self.match("return")        
        self._return()
        self.match(";")
        self.match("}")
        
    
    def _commands(self):
        self.logger.I("_commands")
        if self.match(['print', 'read', 'if', 'for', 'this'], True, False) or self.matchTokenType('IDE', True, False):        
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
            self._forBlock()
        elif self.matchTokenType('IDE', True, False) or self.match('this', True, False):
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
            return
        elif self.matchTokenType('CAC', True):
            return
        elif self.matchTokenType('NRO', True):
            return
        
        self.saveError(['IDE', 'CAC', 'NRO'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    #----------------------------------------------------------------

    def _readBegin(self):
        self.logger.I("_readBegin")
        self.match('read')
        self.match('(')
        self._readEnd()

    def _readEnd(self):
        self.logger.I("_readEnd")
        self._decObjectAttributeAccess()
        self.match(')')
        self.match(';')
    #----------------------------------------------------------------

    def _if(self):
        self.logger.I("_if")
        self.match('if')
        self.match('(')
        self._condition()
        self.match(')')
        self.match('then')
        self.match('{')
        self._commands()
        self.match('}')
        self._ifElse()

    def _ifElse(self):
        self.logger.I("_ifElse")
        if self.match('else', True, True):
            self.match('{')
            self._commands()
            self.match('}')
            return
    
    def _condition(self):
        self.logger.I("_condition")
        self._logicalExpression()

    #----------------------------------------------------------------
       
    def _forBlock(self):
        self.logger.I("_forBlock")
        self._beginFor()
        self._forIncrement()
        self._endFor()
        
    def _assignment(self):
        if self.match('=', True, True):
            self._value()
            return
        elif self.match(['++', '--'], True, True):
            return

        self.saveError(['=', '++', '--'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _forIncrement(self):
        self.logger.I("_forIncrement")
        self._decObjectAttributeAccess()
        self._assignment()

    def _beginFor(self):
        self.logger.I("_beginFor")
        self.match('for')
        self.match('(')
        self._objectAccessOrAssignment()
        self.match(';')
        self._conditionalExpression()
        self.match(';')

    def _endFor(self):
        self.logger.I("_endFor")
        self.match(')')
        self.match('{')
        self._commands()
        self.match('}')

    def _conditionalExpression(self):
        self.logger.I("_conditionalExpression")
        if self.match('(', True, True):
            self._relationalExpression()
            self.match(')')
        else:
            self._relationalExpression()

    def _relationalExpression(self):
        self.logger.I("_relationalExpression")
        self._relationalExpressionValue()
        self.matchTokenType('REL')
        self._relationalExpressionValue()

    #----------------------------------------------------------------

    def _objectAccessOrAssignment(self):
        self.logger.I("_objectAccessOrAssignment")
        self._decObjectAttributeAccess()
        self._objectAccessOrAssigmentEnd()

    def _objectAccessOrAssigmentEnd(self):
        self.logger.I("_objectAccessOrAssigmentEnd")
        if self.match('->', True, False):
            self._objectMethodAccessEnd()
            return
        elif self.match('=', True, True):
            self._value()
            return
        elif self.match('ART', True, True):
            return
        
        self.saveError(['ART', '=', '->'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    #----------------------------------------------------------------
    def _decObjectAttributeAccess(self):
        self.logger.I("_decObjectAttributeAccess")
        if self.matchTokenType('IDE', True, True) or self.match('this', True, True):
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
        self._objectMethodOrObjectAccessOrPart()
    
    def _objectMethodOrObjectAccessOrPart(self):
        self.logger.I("_objectMethodOrObjectAccessOrPart")
        self._decObjectAttributeAccess()
        self._optionalObjectMethodAccess()
    
    def _optionalObjectMethodAccess(self):
        self.logger.I("_optionalObjectMethodAccess")
        if self.match('->', True, False):
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
        self.saveError(['constructor', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
    #----------------------------------------------------------------
    def _parameters(self):
        self.logger.I("_parameters")
        if self.match(['[', '!', '('], True, False) or self.matchTokenType(['NRO', 'CAC', 'IDE'], True, False):
            self._value()
            self._multParameters()
    
    def _value(self):
        self.logger.I("_value")
        if self.matchTokenType('NRO', True, True):
            self._simpleOrDoubleArithimeticExpressionOptional()
            return
        elif self.matchTokenType('CAC', True, True):
            return
        elif self.match('[', True, False):
            self._vectorAssignBlock()
            return
        elif self.matchTokenType('IDE', True, False):
            self._initExpression()
            return
        elif self.match('!', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
            return
        elif self.match('(', True, False):
            self._arithimeticOrLogicalExpressionWithParentheses()
            return
        elif self.match(valueTrueFalse, True, True):
            return
        
        self.saveError(['NRO', 'CAC', 'IDE', '[', '!', '('], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
    
    def _simpleOrDoubleArithimeticExpressionOptional(self):
        self.logger.I("_simpleOrDoubleArithimeticExpressionOptional")
        if self.matchTokenType('ART', True, False):
            self._simpleOrDoubleArithimeticExpression()
            return

    def _vectorAssignBlock(self):
        self.logger.I("_vectorAssignBlock")
        self.match('[')
        self._elementsAssign()
        self.match(']')

    def _initExpression(self):
        self.logger.I("_initExpression")
        self._decObjectAttributeAccess()
        self._arithimeticOrlogicalExpression()

    def _arithimeticOrLogicalExpressionWithParentheses(self):
        self.logger.I("_arithimeticOrLogicalExpressionWithParentheses")
        self._parenthesesBegin()

    def _parenthesesBegin(self):
        self.logger.I("_parenthesesBegin")
        self.match('(')
        self._expressions()
        self._parenthesesEnd()
    
    def _parenthesesEnd(self):
        self.logger.I("_parenthesesEnd")
        self.match(')')
        self._expressionsWithoutParenthesesEnd()

    def _expressionsWithoutParenthesesEnd(self):
        self.logger.I("_expressionsWithoutParenthesesEnd")
        if self.matchTokenType('ART', True, False):
            self._endExpression()
            return
        elif self.matchTokenType('LOG', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
        
    def _expressions(self):
        self.logger.I("_expressions")
        if self.match('(', True, False):
            self._parenthesesBegin()
            return
        elif self.matchTokenType('NRO', True, False):
            self._simpleExpressionWithoutParentheses()
            return
        elif self.match(valueTrueFalse + ['!'], True, False):
            self._logicalExpressionWithoutParentheses()
            return
        elif self.matchTokenType('IDE', True, False):
            self._simpleOrLogicalIDEBegin()
            return

        self.saveError(['NRO', 'IDE', '(', 'true', 'false', '!'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _simpleExpressionWithoutParentheses(self):
        self.logger.I("_simpleExpressionWithoutParentheses")
        self.matchTokenType('NRO')
        self._endExpression()

    def _logicalExpressionWithoutParentheses(self):
        self.logger.I("_logicalExpressionWithoutParentheses")
        if self.match(valueTrueFalse, True, True):
            self._logicalExpressionEnd()
            return
        elif self.match('!', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
            return

        self.saveError(['true', 'false', '!'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _simpleOrLogicalIDEBegin(self):
        self.logger.I("_simpleOrLogicalIDEBegin")
        self._decObjectAttributeAccess()
        self._simpleOrLogicalIDEEnd()
    
    def _simpleOrLogicalIDEEnd(self):
        self.logger.I("_simpleOrLogicalIDEEnd")
        if self.matchTokenType('ART', True, False):
            self._endExpression()
            return
        elif self.match('->', True, False):
            self._optionalObjectMethodAccess()
            self._logRelOptional()
            self._logicalExpressionEnd()
            return
        
        self.saveError(['ART', '->'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _arithimeticOrlogicalExpression(self):
        self.logger.I("_arithimeticOrlogicalExpression")
        if self.matchTokenType('ART', True, False):
            self._simpleOrDoubleArithimeticExpression()
            return
        
        self._optionalObjectMethodAccess()
        self._logRelOptional()
        self._logicalExpressionEnd()
        
    def _logRelOptional(self):
        self.logger.I("_logRelOptional")
        if self.matchTokenType('REL', True, True):
            self._relationalExpressionValue()
            return
        
    def _logicalExpressionEnd(self):
        self.logger.I("_logicalExpressionEnd")
        if self.matchTokenType('LOG', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
            return
        
    def _logicalExpressionBegin(self):
        self.logger.I("_logicalExpressionBegin")
        if self.match('!', True, True):
            self._logicalExpressionBegin()
            return
        elif self.match('(', True, True):
            self._logicalExpression()
            self.match(')')
            return
        elif self.match(valueTrueFalse + ['this'], True, False) or self.matchTokenType('IDE', True, False):
            self._logicalExpressionValue()
            return

        self.saveError(['!', '(', 'true', 'false', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _logicalExpression(self):
        self.logger.I("_logicaExpression")
        self._logicalExpressionBegin()
        self._logicalExpressionEnd()

    def _logicalExpressionValue(self):
        if self.match(valueTrueFalse, True, True):
            return
        elif self.matchTokenType('IDE', True, False) or self.match('this', True, False):
            self._objectMethodOrObjectAccess()
            self._logRelOptional()
            return

        self.saveError(['true', 'false', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _relationalExpressionValue(self):
        if self.matchTokenType('NRO', True, True):
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectMethodOrObjectAccess()
            return
        elif self.matchTokenType('CAC', True, True):
            return
        
        self.saveError(['NRO', 'IDE', 'CAC'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _elementsAssign(self):
        self.logger.I("_elementsAssign")
        self._elementAssign()
        self._multipleElementsAssign()

    def _multipleElementsAssign(self):
        self.logger.I("_multipleElementsASsign")
        if self.match(',', True):
            self._elementAssign()
            self._multipleElementsAssign()
            return

    def _elementAssign(self):
        self.logger.I("_elementAssign")
        if self.matchTokenType(['IDE', 'CAC', 'NRO'], True, True):
            return
        elif self.match('[', True, False):
            self._nDimensionsAssign()
            return
        
        self.saveError(['IDE', 'CAC', 'NRO', '['], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _nDimensionsAssign(self):
        self.logger.I("_nDimensionsAssign")
        if self.match('[', True):
            self._elementsAssign()
            self.match(']')
            return

    def _simpleOrDoubleArithimeticExpression(self):
        self.logger.I("_simpleOrDoubleArithimeticExpression")
        if self.match(['+', '-', '*', '/'], True, False):
            self._endExpression()
            return
        elif self.match(['++', '--'], True, True):
            return

    def _endExpression(self):
        self.logger.I("_endExpression")
        self.matchTokenType('ART')
        self._partLoop()    

    def _partLoop(self):
        self.logger.I("_partLoop")
        if self.matchTokenType('NRO', True, False):
            self._part()
            self._endExpressionOptional()
            return
        elif self.match('(', True, False):
            self._parenthesisExpression()
            return
        
        self.saveError(['NRO', '('], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _part(self):
        self.logger.I("_part")
        if self.matchTokenType('NRO', True, True):
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectMethodOrObjectAccessOrPart()
            return
        
        self.saveError(['NRO', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
    
    def _endExpressionOptional(self):
       self.logger.I("_endExpressionOptional")
       if self.matchTokenType('ART', True, False):
           self._endExpression()
           return
       
    def _parenthesisExpression(self):
        self.logger.I("_parenthesisExpression")
        self.match('(')
        self._simpleExpression()
        self.match(')')
        self._endExpressionOptional()

    def _simpleExpression(self):
        self.logger.I("_simpleExpression")
        if self.matchTokenType(['NRO', 'IDE'], True, False):
            self._part()
            self._endExpression() 
            return
        elif self.match('(', True, False):
            self._parenthesisExpression()
            return

        self.saveError(['NRO', 'IDE', '('], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()

    def _multParameters(self):
        self.logger.I("_multParameters")
        if self.match(',', True):
            self._value()
            self._multParameters()
            return


    def _return(self):      
        if self.match(['[', '!', '('], True, False) or self.matchTokenType(['NRO', 'CAC', 'IDE'], True, False):
            self._value()
            return

    def _mainType(self):
        if not self._type():
            self.match("void")
            return
        
        self.saveError(['void', typesVar], self.lookahead["value"], self.currentTokenLine)
    #----------------------------------------------------------------


    def analize(self):
        self.outputFile = open(self.outputDir, "w", encoding="utf8")

        self._program()

        self.writeTokensAndErrors()
        self.logger.closeLogs()
        self.outputFile.close()
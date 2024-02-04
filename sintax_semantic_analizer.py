from logger import Logger

PATH_FILES = "./files"

typesVar = ["int", "real", "boolean", "string"]
typesValue = ["NRO", "CAC"]
valueTrueFalse = ["true", "false"]
incompatible = "Tipo recebido incompatível:"
duplicated = "Variável duplicada:"
nonDeclared = "Não declarado:"
invalidAtribution = "Atribuição inválida para constantes:"

class SintaxSemanticAnalizer(): 
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
        
        self.tempVar = None
        self.globalScope = []
        self.scopeControl = []
        self.currentSearchedElement = None
        self.currentClassDefinition = None
        self.currentAttribuition = None
        self.loggerSintax = Logger("sintax_analizer")
        self.loggerSemantic = Logger("semantic_analizer")

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
                self.loggerSintax.E(self.errors[-1])
            return False
            
        if tokenType in self.lookahead["type"]:
            if _pass:
                self.nextLookahead()
            return True
        else:
            if not doubt:
                self.saveError(tokenType, self.lookahead["value"], self.currentTokenLine)
                self.nextLookahead()
                self.loggerSintax.E(self.errors[-1])
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
                self.loggerSintax.E(self.errors[-1])
            return False
                
        if terminal in self.lookahead["value"]:
            if _pass:
                self.nextLookahead()
            return True
        else:
            if not doubt:
                self.saveError(terminal, self.lookahead["value"], self.lookahead["line"])
                self.nextLookahead()
                self.loggerSintax.E(self.errors[-1])
            return False
        
    def nextLookahead(self):
        if self.tokensCounter < len(self.tokens):
            self.previousTokenLine = self.lookahead["line"]
            self.lookahead = self.tokens[self.tokensCounter]
            self.currentTokenLine = self.lookahead["line"]
            self.tokensCounter += 1

    def scopeIDEVerification(self, scope: list, ide: str, idx: int = 0) -> dict:
        if len(scope) >= idx + 1 and ide in scope[idx].keys():
            self.currentSearchedElement = scope[idx][ide]
            return self.currentSearchedElement
        return None
    
    def appendToScope(self, scope: list, ide: str, idx: int = 0, typeIDE: str = None, parameters: list[dict] = None, constant: bool = False, instantiated: str = None, isClass: bool = False, inheritance: str = None) -> None: 
        if len(scope) == 0: # Criando o primeiro escopo.
            artifact = {}
            artifact[ide] = {
                "class": isClass,               # É classe?
                "type": typeIDE,                # Tipo da variável (int ou real)
                "parameters": parameters,       # Lista de parâmetros, cada index é um parâmetro, que é um dicionário com o seu nome e tipo.
                "instantiated": instantiated,   # Nome da classe que instanciou.
                "constant": constant,           # É constante?
                "inheritance": inheritance,     # Nome da classe que está herdando.
                "variables": list,              # Lista de nomes das variáveis.
                "objects": list,                # Lista de nomes dos objetos.
                "methods": list                 # Lista de nomes dos metodos.
            }
            scope.append(artifact)
        else: # Colocando em um escopo específico
            scope[idx][ide] = {
                "class": isClass,               # É classe?
                "type": typeIDE,                # Tipo da variável (int ou real)
                "parameters": parameters,       # Lista de parâmetros, cada index é um parâmetro, que é um dicionário com o seu nome e tipo.
                "instantiated": instantiated,   # Nome da classe que instanciou.
                "constant": constant,           # É constante?
                "inheritance": inheritance,     # Nome da classe que está herdando.
                "variables": list,              # Lista de nomes das variáveis.
                "objects": list,                # Lista de nomes dos objetos.
                "methods": list                 # Lista de nomes dos metodos.
            }

    
    def saveError(self, expected: str | list, findOut: str, line: int):
        self.errors.append("Na linha %i, esperava %s e encontrou %s." % (line, expected, findOut))

    def saveSemanticError(self, msg: str,  findOut: str, line: int):
        self.errors.append("%d. %s %s" % (line, msg, findOut))

    def writeTokensAndErrors(self):
        
        for token in self.tokens:
            self.outputFile.write("%i. <%s, %s>\n" % (token["line"], token["type"], token["value"]))

        if len(self.errors) == 0:
            self.outputFile.write("\n############ Arquivo foi analisado com sucesso! ############")
            print("EOF, Arquivo analisado com sucesso!")
        else:
            print("EOF, Arquivo analisado, mas com erros!")
            self.outputFile.write("\n############ !!! Erros encontrados !!! ############\n\n")
            for error in self.errors:
                self.outputFile.write(error + "\n")
    
    def semanticErrorsHandler(self, errorCase: str) -> None:
        match errorCase:
            case "INCOMPATIBLE": #Incompatível
                self.saveSemanticError(incompatible, self.lookahead["value"], self.currentTokenLine)
            case "NONDECLARED": #Não declarado
                self.saveSemanticError(nonDeclared, self.lookahead["value"], self.currentTokenLine)
            case "DUPLICATED": #Duplicado
                self.saveSemanticError(duplicated, self.lookahead["value"], self.currentTokenLine)
            case "INVALIDATTRIBUITON": #Atribuição inválida constante
                self.saveSemanticError(invalidAtribution, self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSemantic.E(self.errors[-1])

    #----------------------------------------------------------------
    #TODO: Inserir os identificadores locais;
    #TODO: Realizar busca de identificadores globais na tabela;
    #TODO: Realizar a busca de identificadores locais;
    #TODO: Verificar a questão se os métodos já estão certos;
    #TODO: Parei em dimensions, testar se o escopo local está funcionando para o que está feito 31/01 21:55 
    def _program(self):
        self.loggerSintax.I("_program")
        self._constsBlock()
        self._variablesBlock(self.globalScope)
        self._classBlock()

    #----------------------------------------------------------------

    def _type(self):
        if self.match(typesVar, True, False):
            self.tempVar = self.lookahead["value"]
            self.match(typesVar)
 
    #----------------------------------------------------------------

    def _constsBlock(self):
        self.loggerSintax.I("constsBlock")
        self.match("const")
        self.match("{")
        self._consts(self.globalScope)

    def _consts(self, scope: list):
        self.loggerSintax.I("consts")
        if not self.match("}", True):
            self._const(scope)
            self._consts(scope)

    def _const(self, scope: list):
        self.loggerSintax.I("const")
        # TODO: Preciso salvar esse tipo sempre
        self._type()
        self._constAttribution(scope)
        self._multipleConsts(scope)

    def _constAttribution(self, scope: list):
        self.loggerSintax.I("_constAttribution")
        if self.matchTokenType("IDE", True, False):
            if self.scopeIDEVerification(scope, self.lookahead["value"]):
                self.semanticErrorsHandler("DUPLICATED")
            else:
                self.appendToScope(scope=scope, ide=self.lookahead["value"], typeIDE=self.tempVar, constant=True)
                self.currentAttribuition = self.lookahead["value"]
                self.matchTokenType("IDE")

        self.match("=")
        # TODO: Em todos os lugares que tiver uma atribuição é necessário repassar onde ela está sendo feita.
        self._attribution(self.globalScope, 0)

    def _attribution(self, scope: list, indexScope: str):
        # TODO: Guardar a atribuição no index do scopo enviado.
        self.loggerSintax.I("_attribution")
        if not self.matchTokenType(typesValue + valueTrueFalse, True, False):
            self.saveError(typesValue + valueTrueFalse, self.lookahead["value"], self.currentTokenLine)
            self.nextLookahead()
            self.loggerSintax.E(self.errors[-1])
        else:
            typeOfVar = scope[indexScope][self.currentAttribuition]["type"]
            if self.lookahead["type"] == 'NRO':
                if len(self.lookahead["value"].split(".")) == 1:
                    if typeOfVar == 'int':
                        scope[indexScope][self.currentAttribuition]["instantiated"] = self.lookahead["value"]
                        self.nextLookahead()
                    else:
                        self.semanticErrorsHandler("INCOMPATIBLE")
                else:
                    if typeOfVar == 'real':
                        scope[indexScope][self.currentAttribuition]["instantiated"] = self.lookahead["value"]
                        self.nextLookahead()
                    else:
                        self.semanticErrorsHandler("INCOMPATIBLE")
            elif self.lookahead["type"] == 'CAC':
                if typeOfVar == 'string':
                    scope[indexScope][self.currentAttribuition]["instantiated"] = self.lookahead["value"]
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            elif self.lookahead["value"] in valueTrueFalse:
                scope[indexScope][self.currentAttribuition]["instantiated"] = self.lookahead["value"]
                self.nextLookahead()
            else:
                self.semanticErrorsHandler("INCOMPATIBLE")

    def _multipleConsts(self, scope: list):
        self.loggerSintax.I("_multipleConsts")
        if not self.match(";", True):
            self.match(",")
            self._constAttribution(scope)
            self._multipleConsts(scope) 

    #----------------------------------------------------------------
    
    def _variablesBlock(self, idx: int = 0, scope: list = [], ):
        self.loggerSintax.I("_variablesBlock")
        if len(scope) == 0: 
            scope = self.scopeControl
        self.match("variables")
        self.match("{")
        self._variables(scope, idx)

    def _variables(self, scope: list, idx: int):
        self.loggerSintax.I("_variables")
        if not self.match("}", True):
            self._variable(scope, idx)
            self._variables(scope, idx)
        

    def _variable(self, scope: list, idx: int):
        self.loggerSintax.I("_variable")
        self._type()
        self._decVariable(scope, idx)         
        self._multipleVariablesLine(scope)

    def _decVariable(self, scope: list, idx: int):
        # TODO: AQUI É NECESSÁRIO VERIFICAR O ESCOPO LOCAL ANTES DE CONSUMIR A IDE
        self.loggerSintax.I("_decVariable")
        if self.scopeIDEVerification(self.globalScope, self.lookahead["value"]) or self.scopeIDEVerification(self.scopeControl, self.lookahead["value"]):
            self.semanticErrorsHandler("DUPLICATED")
        else:
            self.appendToScope(scope=scope, idx=idx, ide=self.lookahead["value"], typeIDE=self.tempVar)
            self.matchTokenType("IDE")
        self._dimensions()

    def _dimensions(self):
        self.loggerSintax.I("_dimensions")
        if self.match("[", True):
            self._sizeDimension()
            self.match("]")
            self._dimensions()
    
    def _sizeDimension(self):
        self.loggerSintax.I("_sizeDimension")
        if not self.matchTokenType("IDE", True, False):
            if self.lookahead["type"] == 'NRO':
                if len(self.lookahead["value"].split(".")) == 1:
                        self.matchTokenType("NRO")
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                self.semanticErrorsHandler("INCOMPATIBLE")
        else:
            if not self.scopeIDEVerification(self.scopeControl, self.lookahead["value"]):    
                if not self.scopeIDEVerification(self.globalScope, self.lookahead["value"]):
                    self.semanticErrorsHandler("NONDECLARED")
                    return
            
            if not self.currentSearchedElement["type"] == 'int':
                self.semanticErrorsHandler("INCOMPATIBLE")
                return
            self.matchTokenType("IDE")

    def _multipleVariablesLine(self, scope: list):
        self.loggerSintax.I("_multipleVariablesLine")
        if self.match(";", True):
            return
        elif self.match(",", True):
            self._decVariable(scope)
            self._multipleVariablesLine(scope)
            return
        
        self.saveError([";", ","], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])
    #----------------------------------------------------------------

    def _objectsBlock(self, scope: list, idx: int):
        self.loggerSintax.I("_objectsBlock")
        self.match("objects")
        self.match("{")
        self._objects(scope, idx)

    def _objects(self, scope: list, idx: int):
        self.loggerSintax.I("_objects")
        if not self.match("}", True):
            self._object(scope, idx)
            self._objects(scope, idx)

    def _object(self, scope: list, idx: int):
        self.loggerSintax.I("_object")
        self.matchTokenType("IDE")
        self._decVariable(scope, idx)
        self._multipleObjects(scope, idx)
    
    def _multipleObjects(self, scope: list, idx: int):
        self.loggerSintax.I("_multipleObjects")
        if not self.match(";", True):
            self._decVariable(scope, idx)
            self._multipleObjects(scope, idx)

    #----------------------------------------------------------------

    def _classBlock(self):
        self.loggerSintax.I("_classBlock")
        self.match("class")
        self._ideClass()
        self.currentClassDefinition = None

    def _ideClass(self):
        self.loggerSintax.I("_ideClass")
        if self.match("main", True, False):
            self.currentClassDefinition = self.lookahead["value"]
            self._main()
        elif self.matchTokenType("IDE", True, False):
            self.currentClassDefinition = self.lookahead["value"]
            searchedClass = self.scopeIDEVerification(self.globalScope, self.lookahead["value"])
            if searchedClass:
                searchedClass["variables"] = list
                searchedClass["objects"] = list
                searchedClass["methods"] = list
                searchedClass["inheritance"] = str
                self.semanticErrorsHandler("DUPLICATED")           
            else:             
                self.appendToScope(self.globalScope, self.lookahead["value"], isClass=True)
                self.matchTokenType("IDE")          
            self._extends()
        else:
            self.saveError(['main', 'IDE'], self.lookahead["value"], self.currentTokenLine)
            self.nextLookahead()
            self.loggerSintax.E(self.errors[-1])

    def _extends(self):
        self.loggerSintax.I("_extends")
        if self.match("{", True, False):
            self._startClassBlock()
        elif self.match("extends", True):
            searchedClass = self.scopeIDEVerification(self.globalScope, self.lookahead["value"])
            if searchedClass:
                self.globalScope[0][self.currentClassDefinition]["inheritance"] = self.lookahead["value"]
                self.matchTokenType("IDE")
            else:
                self.semanticErrorsHandler("NONDECLARED")
            self._startClassBlock()
        else:
            self.saveError(['{', 'extends'], self.lookahead["value"], self.currentTokenLine)
            self.nextLookahead()
            self.loggerSintax.E(self.errors[-1])

    def _startClassBlock(self):
        self.loggerSintax.I("_startClassBlock")
        self.match("{")
        self._initClass()
    
    def _initClass(self):
        self.loggerSintax.I("_initClass")
        self._bodyBlocks()
        self._methodsBlock()
        self._constructor()

    def _constructor(self):
        self.loggerSintax.I("_constructor")
        self.match("constructor")
        self.match("(")
        self._decParametersConstructor()
        self.match(")")
        self.match("{")
        self._variablesBlock(scope=self.scopeControl, idx=0)
        self._objectsBlock(scope=self.scopeControl, idx=0)
        self._commands()
        self.match("}")
        self._endClass()
        self.scopeControl = list

    def _endClass(self):
        self.loggerSintax.I("_endClass")
        self.match("}")
        self._classBlock()

    def _decParametersConstructor(self):
        self.loggerSintax.I("_decParametersConstructor")
        if self.match(typesVar, True, False) or self.matchTokenType('IDE', True, False):
            self._multParamConstructor()
            self._multDecParametersConstructor()#
            return
        
    def _multParamConstructor(self):
        self.loggerSintax.I("_multParamConstructor")
        if self.match(typesVar, True, False):
            self._variableParam()
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectParam()
            return

        self.saveError(typesVar + 'IDE', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _multDecParametersConstructor(self):
        self.loggerSintax.I("_multDecParametersConstructor")
        if self.match(',', True, True):
            self._multParamConstructor()
            self._multDecParametersConstructor()
            return
        
    def _variableParam(self):
        self.loggerSintax.I("_variableParam")
        self.match(typesVar)
        self.matchTokenType('IDE')

    def _objectParam(self):
        self.loggerSintax.I("_objectParam")
        self.matchTokenType('IDE')
        self.matchTokenType('IDE')

    #----------------------------------------------------------------

    def _methodsBlock(self):
        self.loggerSintax.I("_methodsBlock")
        self.match('methods')
        self.match('{')
        self._methods()
        self.match('}')

    def _methods(self):
        self.loggerSintax.I("_methods")
        if self.match(['void','IDE'] + typesVar, True, False):
            self._method()
            self._methods()
            return
        
    def _method(self):
        self.loggerSintax.I("_method")
        self._types()
        self.matchTokenType('IDE')
        self.match('(')
        self._decParameters()

    def _types(self):
        self.loggerSintax.I("types")
        if self.match('void', True, True):
            return
        elif self.match(typesVar + ['IDE'], True, False):
            self._typesVariables()
            return
        
        self.saveError(typesVar + 'IDE' + 'void', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _typesVariables(self):
        self.loggerSintax.I("_typesVariables")
        if self.match(typesVar, True, True):
            return
        elif self.matchTokenType('IDE', True, True):
            return
        
        self.saveError(typesVar + 'IDE', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _decParameters(self):
        self.loggerSintax.I("_decParameters")
        if self.match(typesVar, True, False):
            self._variableParam()
            self._multDecParameters()#
        elif self.matchTokenType('IDE', True, False):
            self._objectParam()
            self._multDecParameters()
        elif self.match(')', True, False):
            self._endDecParameters()#

    def _multDecParameters(self):
        self.loggerSintax.I("_multDecParameters")
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
        self.loggerSintax.E(self.errors[-1])

    def _endDecParameters(self):
        self.loggerSintax.I("_endDecParameters")
        self.match(')')
        self.match('{')
        self._methodBody()

    #----------------------------------------------------------------
    def _main(self):
        self.loggerSintax.I("_main")
        self.match("main")
        self.match("{")
        self._initMain()

    def _initMain(self):
        self.loggerSintax.I("_initMain")
        self._bodyBlocks()
        self._mainMethods()

        numberBeforeLastMatch = self.lookahead["line"]
        self.match("}")
        numberAfterLastMatch = self.lookahead["line"]
        if numberBeforeLastMatch != numberAfterLastMatch:
            self.initLineOfIgnoredTokens = self.lookahead

    def _bodyBlocks(self):
        self.loggerSintax.I("_bodyBlocks")
        self._variablesBlock(0, self.scopeControl)
        self._objectsBlock(0, self.scopeControl) 

    def _mainMethods(self):
        self.loggerSintax.I("_mainMethods")
        self.match("methods")
        self.match("{")
        self._mainMethodsBody()
        self.match("}")

    def _mainMethodsBody(self):
        self.loggerSintax.I("_mainMethodsBody")
        self._mainType()
        self.match("main")
        self.match("(")
        self.match(")")
        self.match("{")
        self._methodBody()
        self._methods()
    
    def _methodBody(self): 
        self.loggerSintax.I("_methodBody")
        self._variablesBlock(1, self.scopeControl)
        self._objectsBlock(1, self.scopeControl)
        self._commandsMethodBody()
        if len(self.scopeControl) == 2:
            self.scopeControl[1] = dict

    
    def _commandsMethodBody(self):
        self.loggerSintax.I("_commandsMethodBody")
        self._commands()
        self.match("return")        
        self._return()
        self.match(";")
        self.match("}")
        
    
    def _commands(self):
        self.loggerSintax.I("_commands")
        if self.match(['print', 'read', 'if', 'for', 'this'], True, False) or self.matchTokenType('IDE', True, False):        
            self._command()
            self._commands()

    def _command(self):
        self.loggerSintax.I("_command")
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
        self.loggerSintax.I("_printBegin")
        self.match('print')
        self.match('(')
        self._printEnd()

    def _printEnd(self):
        self.loggerSintax.I("_printEnd")
        self._printParameter()
        self.match(')')
        self.match(';')

    def _printParameter(self):
        self.loggerSintax.I("_printParameter")
        if self.matchTokenType('IDE', True, False):
            self._decObjectAttributeAccess() 
            return
        elif self.matchTokenType('CAC', True):
            return
        elif self.matchTokenType('NRO', True):
            return
        
        self.saveError(['IDE', 'CAC', 'NRO'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    #----------------------------------------------------------------

    def _readBegin(self):
        self.loggerSintax.I("_readBegin")
        self.match('read')
        self.match('(')
        self._readEnd()

    def _readEnd(self):
        self.loggerSintax.I("_readEnd")
        self._decObjectAttributeAccess()
        self.match(')')
        self.match(';')
    #----------------------------------------------------------------

    def _if(self):
        self.loggerSintax.I("_if")
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
        self.loggerSintax.I("_ifElse")
        if self.match('else', True, True):
            self.match('{')
            self._commands()
            self.match('}')
            return
    
    def _condition(self):
        self.loggerSintax.I("_condition")
        self._logicalExpression()

    #----------------------------------------------------------------
       
    def _forBlock(self):
        self.loggerSintax.I("_forBlock")
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
        self.loggerSintax.E(self.errors[-1])

    def _forIncrement(self):
        self.loggerSintax.I("_forIncrement")
        self._decObjectAttributeAccess()
        self._assignment()

    def _beginFor(self):
        self.loggerSintax.I("_beginFor")
        self.match('for')
        self.match('(')
        self._objectAccessOrAssignment()
        self.match(';')
        self._conditionalExpression()
        self.match(';')

    def _endFor(self):
        self.loggerSintax.I("_endFor")
        self.match(')')
        self.match('{')
        self._commands()
        self.match('}')

    def _conditionalExpression(self):
        self.loggerSintax.I("_conditionalExpression")
        if self.match('(', True, True):
            self._relationalExpression()
            self.match(')')
        else:
            self._relationalExpression()

    def _relationalExpression(self):
        self.loggerSintax.I("_relationalExpression")
        self._relationalExpressionValue()
        self.matchTokenType('REL')
        self._relationalExpressionValue()

    #----------------------------------------------------------------

    def _objectAccessOrAssignment(self):
        self.loggerSintax.I("_objectAccessOrAssignment")
        self._decObjectAttributeAccess()
        self._objectAccessOrAssigmentEnd()

    def _objectAccessOrAssigmentEnd(self):
        self.loggerSintax.I("_objectAccessOrAssigmentEnd")
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
        self.loggerSintax.E(self.errors[-1])

    #----------------------------------------------------------------
    def _decObjectAttributeAccess(self):
        self.loggerSintax.I("_decObjectAttributeAccess")
        if self.matchTokenType('IDE', True, True) or self.match('this', True, True):
            self._dimensions()
            self._endObjectAttributeAccess()

    def _endObjectAttributeAccess(self):
        self.loggerSintax.I("_endObjectAttributeAccess")
        if self.match('.', True):
            self._multipleObjectAttributeAccess()

    def _multipleObjectAttributeAccess(self):
        self.loggerSintax.I("_multipleObjectAttributeAccess")
        self._decVariable()
        self._endObjectAttributeAccess()

    def _objectMethodOrObjectAccess(self):
        self.loggerSintax.I("_objectMethodOrObjectAccess")
        self._objectMethodOrObjectAccessOrPart()
    
    def _objectMethodOrObjectAccessOrPart(self):
        self.loggerSintax.I("_objectMethodOrObjectAccessOrPart")
        self._decObjectAttributeAccess()
        self._optionalObjectMethodAccess()
    
    def _optionalObjectMethodAccess(self):
        self.loggerSintax.I("_optionalObjectMethodAccess")
        if self.match('->', True, False):
            self._objectMethodAccessEnd()            

    def _objectMethodAccessEnd(self):
        self.loggerSintax.I("_objectMethodAccessEnd")
        self.match('->')
        self._ideOrConstructor()
        self.match('(')
        self._parameters()
        self.match(')')
    
    def _ideOrConstructor(self):
        self.loggerSintax.I("_ideOrConstructor")
        if self.match('constructor', True):
            return
        elif self.matchTokenType('IDE', True):
            return
        self.saveError(['constructor', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])
    #----------------------------------------------------------------
    def _parameters(self):
        self.loggerSintax.I("_parameters")
        if self.match(['[', '!', '('], True, False) or self.matchTokenType(['NRO', 'CAC', 'IDE'], True, False):
            self._value()
            self._multParameters()
    
    def _value(self):
        self.loggerSintax.I("_value")
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
        self.loggerSintax.E(self.errors[-1])
    
    def _simpleOrDoubleArithimeticExpressionOptional(self):
        self.loggerSintax.I("_simpleOrDoubleArithimeticExpressionOptional")
        if self.matchTokenType('ART', True, False):
            self._simpleOrDoubleArithimeticExpression()
            return

    def _vectorAssignBlock(self):
        self.loggerSintax.I("_vectorAssignBlock")
        self.match('[')
        self._elementsAssign()
        self.match(']')

    def _initExpression(self):
        self.loggerSintax.I("_initExpression")
        self._decObjectAttributeAccess()
        self._arithimeticOrlogicalExpression()

    def _arithimeticOrLogicalExpressionWithParentheses(self):
        self.loggerSintax.I("_arithimeticOrLogicalExpressionWithParentheses")
        self._parenthesesBegin()

    def _parenthesesBegin(self):
        self.loggerSintax.I("_parenthesesBegin")
        self.match('(')
        self._expressions()
        self._parenthesesEnd()
    
    def _parenthesesEnd(self):
        self.loggerSintax.I("_parenthesesEnd")
        self.match(')')
        self._expressionsWithoutParenthesesEnd()

    def _expressionsWithoutParenthesesEnd(self):
        self.loggerSintax.I("_expressionsWithoutParenthesesEnd")
        if self.matchTokenType('ART', True, False):
            self._endExpression()
            return
        elif self.matchTokenType('LOG', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
        
    def _expressions(self):
        self.loggerSintax.I("_expressions")
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
        self.loggerSintax.E(self.errors[-1])

    def _simpleExpressionWithoutParentheses(self):
        self.loggerSintax.I("_simpleExpressionWithoutParentheses")
        self.matchTokenType('NRO')
        self._endExpression()

    def _logicalExpressionWithoutParentheses(self):
        self.loggerSintax.I("_logicalExpressionWithoutParentheses")
        if self.match(valueTrueFalse, True, True):
            self._logicalExpressionEnd()
            return
        elif self.match('!', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
            return

        self.saveError(['true', 'false', '!'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _simpleOrLogicalIDEBegin(self):
        self.loggerSintax.I("_simpleOrLogicalIDEBegin")
        self._decObjectAttributeAccess()
        self._simpleOrLogicalIDEEnd()
    
    def _simpleOrLogicalIDEEnd(self):
        self.loggerSintax.I("_simpleOrLogicalIDEEnd")
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
        self.loggerSintax.E(self.errors[-1])

    def _arithimeticOrlogicalExpression(self):
        self.loggerSintax.I("_arithimeticOrlogicalExpression")
        if self.matchTokenType('ART', True, False):
            self._simpleOrDoubleArithimeticExpression()
            return
        
        self._optionalObjectMethodAccess()
        self._logRelOptional()
        self._logicalExpressionEnd()
        
    def _logRelOptional(self):
        self.loggerSintax.I("_logRelOptional")
        if self.matchTokenType('REL', True, True):
            self._relationalExpressionValue()
            return
        
    def _logicalExpressionEnd(self):
        self.loggerSintax.I("_logicalExpressionEnd")
        if self.matchTokenType('LOG', True, True):
            self._logicalExpressionBegin()
            self._logicalExpressionEnd()
            return
        
    def _logicalExpressionBegin(self):
        self.loggerSintax.I("_logicalExpressionBegin")
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
        self.loggerSintax.E(self.errors[-1])

    def _logicalExpression(self):
        self.loggerSintax.I("_logicaExpression")
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
        self.loggerSintax.E(self.errors[-1])

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
        self.loggerSintax.E(self.errors[-1])

    def _elementsAssign(self):
        self.loggerSintax.I("_elementsAssign")
        self._elementAssign()
        self._multipleElementsAssign()

    def _multipleElementsAssign(self):
        self.loggerSintax.I("_multipleElementsASsign")
        if self.match(',', True):
            self._elementAssign()
            self._multipleElementsAssign()
            return

    def _elementAssign(self):
        self.loggerSintax.I("_elementAssign")
        if self.matchTokenType(['IDE', 'CAC', 'NRO'], True, True):
            return
        elif self.match('[', True, False):
            self._nDimensionsAssign()
            return
        
        self.saveError(['IDE', 'CAC', 'NRO', '['], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _nDimensionsAssign(self):
        self.loggerSintax.I("_nDimensionsAssign")
        if self.match('[', True):
            self._elementsAssign()
            self.match(']')
            return

    def _simpleOrDoubleArithimeticExpression(self):
        self.loggerSintax.I("_simpleOrDoubleArithimeticExpression")
        if self.match(['+', '-', '*', '/'], True, False):
            self._endExpression()
            return
        elif self.match(['++', '--'], True, True):
            return

    def _endExpression(self):
        self.loggerSintax.I("_endExpression")
        self.matchTokenType('ART')
        self._partLoop()    

    def _partLoop(self):
        self.loggerSintax.I("_partLoop")
        if self.matchTokenType('NRO', True, False):
            self._part()
            self._endExpressionOptional()
            return
        elif self.match('(', True, False):
            self._parenthesisExpression()
            return
        
        self.saveError(['NRO', '('], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _part(self):
        self.loggerSintax.I("_part")
        if self.matchTokenType('NRO', True, True):
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectMethodOrObjectAccessOrPart()
            return
        
        self.saveError(['NRO', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])
    
    def _endExpressionOptional(self):
       self.loggerSintax.I("_endExpressionOptional")
       if self.matchTokenType('ART', True, False):
           self._endExpression()
           return
       
    def _parenthesisExpression(self):
        self.loggerSintax.I("_parenthesisExpression")
        self.match('(')
        self._simpleExpression()
        self.match(')')
        self._endExpressionOptional()

    def _simpleExpression(self):
        self.loggerSintax.I("_simpleExpression")
        if self.matchTokenType(['NRO', 'IDE'], True, False):
            self._part()
            self._endExpression() 
            return
        elif self.match('(', True, False):
            self._parenthesisExpression()
            return

        self.saveError(['NRO', 'IDE', '('], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _multParameters(self):
        self.loggerSintax.I("_multParameters")
        if self.match(',', True):
            self._value()
            self._multParameters()
            return


    def _return(self):      
        if self.match(['[', '!', '('], True, False) or self.matchTokenType(['NRO', 'CAC', 'IDE'], True, False):
            self._value()
            return

    def _mainType(self):
        if self.match(typesVar, True):
            return
        elif self.match("void", True):
            return
        
        self.saveError(['void', typesVar], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])
    #----------------------------------------------------------------


    def analize(self):
        self.outputFile = open(self.outputDir, "w", encoding="utf8")

        self._program()

        self.writeTokensAndErrors()
        self.loggerSintax.closeLogs()
        self.outputFile.close()#
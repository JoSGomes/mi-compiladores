from logger import Logger
import copy
import re

PATH_FILES = "./files"

typesVar = ["int", "real", "boolean", "string"]
typesValue = ["NRO", "CAC"]
valueTrueFalse = ["true", "false"]
incompatible = "Tipo recebido incompatível:"
duplicated = "Variável duplicada:"
nonDeclared = "Não declarado:"
invalidAtribution = "Atribuição inválida para constantes:"
pattern = r'^[-+]?[0-9]*\.?[0-9]+$'

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
        self.currentClassAttributeDefinition = False
        self.currentMethodDefinition = None
        self.currentAttributeAccess = None
        self.currentParametersMethodAccess = None
        self.currentAttribuition = None
        self.indexScopeSeeing = 0
        self.ifConditionFlag = False
        self.currentPathAttributeAccess = list()
        
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
    
    def removeVarsAndMethodsFromLocalScope(self):
        keysToRemove = []
        for key in self.scopeControl[0].keys():
            if self.scopeControl[0][key]["belongsTo"] == self.currentClassDefinition:
                keysToRemove.append(key)
        
        for key in keysToRemove:
            self.scopeControl[0].pop(key, None)

    def getGlobalVars(self) -> dict:
        globalVars = {}
        for key in self.globalScope[0].keys():
            if self.globalScope[0][key]["class"] == False:
                globalVars[key] = self.globalScope[0][key]
        return globalVars
    
    def getPrimaryTypeFromAllScopes(self, ide: str) -> str:
        if len(self.scopeControl) > 0 and self.currentMethodDefinition != None:
            if ide in self.scopeControl[0][self.currentMethodDefinition]["parameters"]:
                return self.scopeControl[0][self.currentMethodDefinition]["parameters"][ide]
            elif ide in self.scopeControl[0][self.currentMethodDefinition]["variables"]:
                return self.scopeControl[0][self.currentMethodDefinition]["variables"][ide]
            elif ide in self.scopeControl[0][self.currentMethodDefinition]["objects"]:
                return self.scopeControl[0][self.currentMethodDefinition]["objects"][ide]
        if len(self.globalScope) > 0 and self.currentClassDefinition != None:
            if ide in self.globalScope[0][self.currentClassDefinition]["variables"]:
                return self.globalScope[0][self.currentClassDefinition]["variables"][ide]
            elif ide in self.globalScope[0][self.currentClassDefinition]["objects"]:
                return self.globalScope[0][self.currentClassDefinition]["objects"][ide]
            elif ide in self.globalScope[0]:
                return self.globalScope[0][ide]["type"]
        elif len(self.globalScope) > 0:
            if ide in self.globalScope[0]:
                return self.globalScope[0][ide]["type"]
            elif ide in self.globalScope[0]:
                return self.globalScope[0][ide]["type"]
            elif ide in self.globalScope[0]:
                return self.globalScope[0][ide]["type"]
        return None

    def getPrimaryTypeFromAllScopesFromPath(self, attribute: str, path: str) -> str:
        primaryType = None
        objectType = None
        i = 0
        if attribute == "this":
            if "this" in path:
                path.remove("this")
            for artifact in path:   
                if i == 0:
                    if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                        primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                    elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                        objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                    elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                        inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                        if artifact in self.globalScope[0][inheritance]["variables"].keys():
                            primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                        elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                            objectType = self.globalScope[0][inheritance]["objects"][artifact]
                elif objectType:
                    if artifact in self.globalScope[0][objectType]["variables"].keys():
                        primaryType = self.globalScope[0][objectType]["variables"][artifact]
                    elif artifact in self.globalScope[0][objectType]["objects"].keys():
                        objectType = self.globalScope[0][objectType]["objects"][artifact]

                if primaryType:
                    if len(path) > i + 1:
                        self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário

                i += 1
        else:
            primaryType = None
            objectType = None
            for artifact in path:
                if i == 0:
                    if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                        primaryType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                    elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                        objectType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                    elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                        if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                            primaryType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                        else:
                            objectType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                    elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                        primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                    elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                        objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                    elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                        inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                        if artifact in self.globalScope[0][inheritance]["variables"].keys():
                            primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                        elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                            objectType = self.globalScope[0][inheritance]["objects"][artifact] 
                elif objectType:
                    if artifact in self.globalScope[0][objectType]["variables"].keys():
                        primaryType = self.globalScope[0][objectType]["variables"][artifact]
                    elif artifact in self.globalScope[0][objectType]["objects"].key():
                        objectType = self.globalScope[0][objectType]["objects"][artifact]
        return primaryType
    def appendToScope(self, scope: list, ide: str, idx: int = 0, typeIDE: str = None, parameters: dict = dict(), constant: bool = False, isClass: bool = False, inheritance: str = None, belongsTo: str = None) -> None: 
        parameters = dict()
        if len(scope) < idx+1: # Criando o primeiro escopo.
            artifact = {}
            artifact[ide] = {
                "class": isClass,               # É classe?
                "belongsTo": belongsTo,         # Nome da classe/metodo que o método pertence.
                "type": typeIDE,                # Tipo da variável (int ou real)
                "parameters": parameters,       # Lista de parâmetros, cada index é um parâmetro, que é um dicionário com o seu nome e tipo.
                "constant": constant,           # É constante?
                "inheritance": inheritance,     # Nome da classe que está herdando.
                "variables": dict(),              # Lista de nomes das variáveis.
                "objects": dict(),                # Lista de nomes dos objetos.
                "methods": dict()                 # Lista de nomes dos metodos.
            }
            scope.append(artifact)
        else: # Colocando em um escopo específico
            scope[idx][ide] = {
                "class": isClass,               # É classe?
                "belongsTo": belongsTo,         # Nome da classe que o método pertence.
                "type": typeIDE,                # Tipo da variável (int ou real)
                "parameters": parameters,       # Lista de parâmetros, cada index é um parâmetro, que é um dicionário com o seu nome e tipo.
                "constant": constant,           # É constante?
                "inheritance": inheritance,     # Nome da classe que está herdando.
                "variables": dict(),              # Lista de nomes das variáveis.
                "objects": dict(),                # Lista de nomes dos objetos.
                "methods": dict()                 # Lista de nomes dos metodos.
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
    # TODO: Definir como construtor será salvo
    # TODO: Verificar a atribuição dentro do método 

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
        self._type()
        self._constAttribution(scope)
        self._multipleConsts(scope)

    def _constAttribution(self, scope: list):
        self.loggerSintax.I("_constAttribution")
        if self.matchTokenType("IDE", True, False):
            if self.scopeIDEVerification(scope, self.lookahead["value"]):
                self.semanticErrorsHandler("DUPLICATED")
            else:
                self.appendToScope(scope=scope, ide=self.lookahead["value"],  belongsTo=self.currentClassDefinition, typeIDE=self.tempVar, constant=True)
                self.currentAttribuition = self.lookahead["value"]
                self.matchTokenType("IDE")

        self.match("=")
        self._attribution(self.globalScope, 0)

    def _attribution(self, scope: list, indexScope: int):
        # TODO: Guardar a atribuição no index do scopo enviado.
        self.loggerSintax.I("_attribution")
        if not self.matchTokenType(typesValue, True, False):
            if not self.match(valueTrueFalse, True, False):
                self.saveError(typesValue + valueTrueFalse, self.lookahead["value"], self.currentTokenLine)
                self.nextLookahead()
                self.loggerSintax.E(self.errors[-1])
                return
            
        typeOfVar = scope[indexScope][self.currentAttribuition]["type"]
        if self.lookahead["type"] == 'NRO':
            if len(self.lookahead["value"].split(".")) == 1:
                if typeOfVar == 'int':
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                if typeOfVar == 'real':
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
        elif self.lookahead["type"] == 'CAC':
            if typeOfVar == 'string':
                self.nextLookahead()
            else:
                self.semanticErrorsHandler("INCOMPATIBLE")
        elif self.lookahead["value"] in valueTrueFalse:
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
    
    def _variablesBlock(self, scope: list = [], idx: int = 0, belongsTo: str = None):
        self.loggerSintax.I("_variablesBlock")
        self.match("variables")
        self.match("{")
        self._variables(scope, idx, belongsTo)

    def _variables(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_variables")
        if not self.match("}", True):
            self._variable(scope, idx, belongsTo)
            self._variables(scope, idx, belongsTo)
        

    def _variable(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_variable")
        self._type()
        self._decVariable(scope, idx, belongsTo)         
        self._multipleVariablesLine(scope, idx, belongsTo)

    def _decVariable(self, scope: list, idx: int, belongsTo: str, logicalExpression: bool = False):
        # TODO: AQUI É NECESSÁRIO VERIFICAR O ESCOPO LOCAL ANTES DE CONSUMIR A IDE
        self.loggerSintax.I("_decVariable")
        if not self.currentAttributeAccess:
            if self.scopeIDEVerification(self.globalScope, self.lookahead["value"]):
                self.semanticErrorsHandler("DUPLICATED")
            else:
                if self.currentMethodDefinition:
                    if self.tempVar not in typesVar:
                        scope[idx][self.currentMethodDefinition]["objects"][self.lookahead["value"]] = self.tempVar
                    else:
                        scope[idx][self.currentMethodDefinition]["variables"][self.lookahead["value"]] = self.tempVar
                else:
                    self.appendToScope(scope=scope, idx=idx, ide=self.lookahead["value"], belongsTo=self.currentClassDefinition, typeIDE=self.tempVar)
                    if self.currentClassDefinition:
                        if self.tempVar not in typesVar:
                            self.globalScope[0][self.currentClassDefinition]["objects"][self.lookahead["value"]] = self.tempVar
                        else:
                            self.globalScope[0][self.currentClassDefinition]["variables"][self.lookahead["value"]] = self.tempVar

                self.matchTokenType("IDE")
        else:
            self.currentPathAttributeAccess.append(self.lookahead["value"])
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
            primaryType = self.getPrimaryTypeFromAllScopes(self.lookahead["value"])
            if not primaryType:    
                self.semanticErrorsHandler("NONDECLARED")
                return          
            elif not primaryType == 'int':
                self.semanticErrorsHandler("INCOMPATIBLE")
                return
            self.matchTokenType("IDE")

    def _multipleVariablesLine(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_multipleVariablesLine")
        if self.match(";", True):
            return
        elif self.match(",", True):
            self._decVariable(scope, idx, belongsTo)
            self._multipleVariablesLine(scope, idx, belongsTo)
            return
        
        self.saveError([";", ","], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])
    #----------------------------------------------------------------

    def _objectsBlock(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_objectsBlock")
        self.match("objects")
        self.match("{")
        self._objects(scope, idx, belongsTo)

    def _objects(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_objects")
        if not self.match("}", True):
            self._object(scope, idx, belongsTo)
            self._objects(scope, idx, belongsTo)

    def _object(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_object")
        self.tempVar = self.lookahead["value"]
        self.matchTokenType("IDE")
        self._decVariable(scope, idx, belongsTo)
        self._multipleObjects(scope, idx, belongsTo)
    
    def _multipleObjects(self, scope: list, idx: int, belongsTo: str):
        self.loggerSintax.I("_multipleObjects")
        if not self.match(";", True):
            self._decVariable(scope, idx, belongsTo)
            self._multipleObjects(scope, idx, belongsTo)

    #----------------------------------------------------------------

    def _classBlock(self):
        self.loggerSintax.I("_classBlock")
        self.match("class")
        self._ideClass()
        self.currentClassDefinition = None

    def _ideClass(self):
        self.loggerSintax.I("_ideClass")
        if self.match("main", True, False):            
            self._main()
        elif self.matchTokenType("IDE", True, False):
            self.currentClassDefinition = self.lookahead["value"]
            if self.scopeIDEVerification(self.globalScope, self.lookahead["value"]):
                self.removeVarsAndMethodsFromLocalScope()
                self.semanticErrorsHandler("DUPLICATED")
            else:
                self.matchTokenType("IDE")

            self.appendToScope(self.globalScope, self.currentClassDefinition, isClass=True)       
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
        self.currentMethodDefinition = "constructor" 
        if self.currentMethodDefinition in self.globalScope[0][self.currentClassDefinition]["methods"]:
            self.semanticErrorsHandler("DUPLICATED")  
        else:
            self.match("constructor")
        self.appendToScope(scope=self.scopeControl, idx=0, ide=self.currentMethodDefinition, belongsTo=self.currentClassDefinition)       
        self.globalScope[0][self.currentClassDefinition]["methods"][self.currentMethodDefinition] = self.scopeControl[0][self.currentMethodDefinition] 
        self.match("(")
        self._decParametersConstructor(self.scopeControl, idx=0, ide="constructor")
        self.match(")")
        self.match("{")
        self._variablesBlock(scope=self.scopeControl, idx=0, belongsTo="constructor")
        self._objectsBlock(scope=self.scopeControl, idx=0, belongsTo="constructor")
        self._commands()
        self.match("}")
        self._endClass()       

    def _endClass(self):
        self.loggerSintax.I("_endClass")
        self.match("}")
        self.currentMethodDefinition = None
        self._classBlock()

    def _decParametersConstructor(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_decParametersConstructor")
        if self.match(typesVar, True, False) or self.matchTokenType('IDE', True, False):
            self._multParamConstructor(scope, idx, ide)
            self._multDecParametersConstructor(scope, idx, ide)
            return
        
    def _multParamConstructor(self,  scope: list, idx: int, ide: str):
        self.loggerSintax.I("_multParamConstructor")
        if self.match(typesVar, True, False):
            self._variableParam(scope, idx, ide)
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectParam(scope, idx, ide)
            return

        self.saveError(typesVar + 'IDE', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _multDecParametersConstructor(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_multDecParametersConstructor")
        if self.match(',', True, True):
            self._multParamConstructor(scope, idx, ide)
            self._multDecParametersConstructor(scope, idx, ide)
            return
        
    def _variableParam(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_variableParam")
        self.tempVar = self.lookahead["value"]
        self.match(typesVar)
        scope[idx][ide]["parameters"][self.lookahead["value"]] = self.tempVar
        self.matchTokenType('IDE')

    def _objectParam(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_objectParam")
        self.tempVar = self.lookahead["value"]
        self.matchTokenType('IDE')
        scope[idx][ide]["parameters"][self.lookahead["value"]] = self.tempVar
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
            self.currentMethodDefinition = None
            self._methods()
            return
        
    def _method(self):
        self.loggerSintax.I("_method")
        self._types()
        self.currentMethodDefinition = self.lookahead["value"]     
        if self.currentMethodDefinition in self.globalScope[0][self.currentClassDefinition]["methods"]:
            self.semanticErrorsHandler("DUPLICATED")  
        else:
            self.matchTokenType('IDE')
        self.appendToScope(scope=self.scopeControl, idx=0, ide=self.currentMethodDefinition, typeIDE=self.tempVar, belongsTo=self.currentClassDefinition)   
        self.globalScope[0][self.currentClassDefinition]["methods"][self.currentMethodDefinition] = self.scopeControl[0][self.currentMethodDefinition]           
        self.match('(')
        self._decParameters(self.scopeControl, 0, self.currentMethodDefinition)

    def _types(self):
        self.loggerSintax.I("types")
        if self.match('void', True, False):
            self.tempVar = self.lookahead["value"]
            self.match('void')
            return
        elif self.match(typesVar + ['IDE'], True, False):
            self._typesVariables()
            return
        
        self.saveError(typesVar + 'IDE' + 'void', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _typesVariables(self):
        self.loggerSintax.I("_typesVariables")
        if self.match(typesVar, True, False):
            self.tempVar = self.lookahead["value"]
            self.match(typesVar)
            return
        elif self.matchTokenType('IDE', True, False):  
            self.tempVar = self.lookahead["value"]
            self.matchTokenType('IDE')
            return
        
        self.saveError(typesVar + 'IDE', self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _decParameters(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_decParameters")
        if self.match(typesVar, True, False):
            self._variableParam(scope, idx, ide)
            self._multDecParameters(scope, idx, ide)
        elif self.matchTokenType('IDE', True, False):
            self._objectParam(scope, idx, ide)
            self._multDecParameters(scope, idx, ide)
        elif self.match(')', True, False):
            self._endDecParameters(scope, idx, ide)

    def _multDecParameters(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_multDecParameters")
        if self.match(',', True, True):
            self._typesVariables()
            scope[idx][ide]["parameters"][self.lookahead["value"]] = self.tempVar
            self.matchTokenType('IDE')
            self._multDecParameters(scope, idx, ide)
            return
        elif self.match(')', True, False):
            self._endDecParameters(scope, idx, ide)
            return

        self.saveError([',', ')'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _endDecParameters(self, scope: list, idx: int, ide: str):
        self.loggerSintax.I("_endDecParameters")
        self.match(')')
        self.match('{')
        self._methodBody()

    #----------------------------------------------------------------
    def _main(self):
        self.loggerSintax.I("_main")
        self.currentClassDefinition = self.lookahead["value"]
        self.appendToScope(self.globalScope, self.currentClassDefinition, isClass=True)
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
        self._variablesBlock(idx=0, scope=self.scopeControl, belongsTo=self.currentClassDefinition)
        self._objectsBlock(idx=0, scope=self.scopeControl, belongsTo=self.currentClassDefinition) 

    def _mainMethods(self):
        self.loggerSintax.I("_mainMethods")
        self.match("methods")
        self.match("{")
        self._mainMethodsBody()
        self.match("}")

    def _mainMethodsBody(self):
        self.loggerSintax.I("_mainMethodsBody")
        self._mainType()
        self.currentMethodDefinition = self.lookahead["value"]    
        self.appendToScope(scope=self.scopeControl, idx=0, ide=self.currentMethodDefinition, typeIDE=self.tempVar, belongsTo=self.currentClassDefinition)   
        self.globalScope[0][self.currentClassDefinition]["methods"][self.currentMethodDefinition] = self.scopeControl[0][self.currentMethodDefinition]
        self.match("main")
        self.match("(")
        self.match(")")
        self.match("{")
        self._methodBody()
        self._methods()
    
    def _methodBody(self): 
        self.loggerSintax.I("_methodBody")
        self._variablesBlock(scope=self.scopeControl, idx=0, belongsTo=self.currentMethodDefinition)
        self._objectsBlock(scope=self.scopeControl, idx=0, belongsTo=self.currentMethodDefinition)
        self._commandsMethodBody()

    
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
            self.currentAttributeAccess = None
            self.currentPathAttributeAccess = list()
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
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()
        self.match(')')
        self.match(';')
    #----------------------------------------------------------------

    def _if(self):
        self.loggerSintax.I("_if")
        self.match('if')
        self.match('(')
        self.ifConditionFlag = True
        self._condition()
        self.ifConditionFlag = False
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
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()
        self._decObjectAttributeAccess()
        self._assignment()
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()

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
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()
        self._decObjectAttributeAccess()
        self._objectAccessOrAssigmentEnd()
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()

    def _objectAccessOrAssigmentEnd(self):
        self.loggerSintax.I("_objectAccessOrAssigmentEnd")
        if self.match('->', True, False):
            self._objectMethodAccessEnd()
            return
        elif self.match('=', True, True):
            self._value()
            return
        elif self.match(['++', '--'], True, False):
            i = 0
            if self.currentAttributeAccess == "this":
                self.currentPathAttributeAccess.remove("this")
                primaryType = None
                objectType = None
                for artifact in self.currentPathAttributeAccess:   
                    if i == 0:
                        if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                            primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                            elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectType = self.globalScope[0][inheritance]["objects"][artifact]
                    elif objectType:
                        if artifact in self.globalScope[0][objectType]["variables"].keys():
                            primaryType = self.globalScope[0][objectType]["variables"][artifact]
                        elif artifact in self.globalScope[0][objectType]["objects"].keys():
                            objectType = self.globalScope[0][objectType]["objects"][artifact]

                    if primaryType:
                        if len(self.currentPathAttributeAccess) > i + 1:
                            self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                        else:
                            self._simpleOrDoubleArithimeticExpressionOptional(primaryType)
                    i += 1
            else:
                primaryType = None
                objectType = None
                for artifact in self.currentPathAttributeAccess:
                    if i == 0:
                        if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                            primaryType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                        elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                            objectType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                        elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                            if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                primaryType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                            else:
                                objectType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                            primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                            elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectType = self.globalScope[0][inheritance]["objects"][artifact]
                    elif objectType:
                        if artifact in self.globalScope[0][objectType]["variables"].keys():
                            primaryType = self.globalScope[0][objectType]["variables"][artifact]
                        elif artifact in self.globalScope[0][objectType]["objects"].key():
                            objectType = self.globalScope[0][objectType]["objects"][artifact]
                    
                    if primaryType:
                        if len(self.currentPathAttributeAccess) > i + 1:
                            self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            
                    i += 1

            if not primaryType:
                self.semanticErrorsHandler("NONDECLARED")
            else:
                if len(self.lookahead["value"].split(".")) == 1:
                    if primaryType == 'int':
                        self.nextLookahead()
                    else:
                        self.semanticErrorsHandler("INCOMPATIBLE")
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            return
        
        self.saveError(['++', '--', '=', '->'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    #----------------------------------------------------------------
    def _decObjectAttributeAccess(self, primaryType: str = None, returnValue: bool = False): 
        self.loggerSintax.I("_decObjectAttributeAccess")
        if self.matchTokenType('IDE', True, False) or self.match('this', True, False):
            if self.matchTokenType('IDE', True, False):
                if self.lookahead["value"] not in ( list(self.scopeControl[0][self.currentMethodDefinition]["variables"].keys()) + \
                        list(self.scopeControl[0][self.currentMethodDefinition]["objects"].keys()) + \
                        list(self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys()) + \
                        list(self.globalScope[0][self.currentClassDefinition]["variables"].keys()) + \
                        list(self.globalScope[0][self.currentClassDefinition]["objects"].keys()) + \
                        list(self.getGlobalVars().keys())):
                    self.semanticErrorsHandler("NONDECLARED")
                else:
                    self.currentAttributeAccess = self.lookahead["value"]
                    self.currentPathAttributeAccess.append(self.currentAttributeAccess)
                    if not returnValue:
                        self.matchTokenType('IDE')
            else:
                self.currentAttributeAccess = "this"
                self.currentPathAttributeAccess.append(self.currentAttributeAccess)
                self.match('this')

            self._dimensions()
            self._endObjectAttributeAccess(primaryType)

        if returnValue:
            if not primaryType == self.scopeControl[0][self.currentMethodDefinition]["type"] and len(self.currentPathAttributeAccess) == 0:
                self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                if self.currentAttributeAccess == "this":
                    self.currentPathAttributeAccess.remove("this")
                    primaryReturnType = None
                    objectReturnType = None
                    for artifact in self.currentPathAttributeAccess:   
                        if i == 0:
                            if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryReturnType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectReturnType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryReturnType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectReturnType = self.globalScope[0][inheritance]["objects"][artifact]
                        elif objectReturnType:
                            if artifact in self.globalScope[0][objectReturnType]["variables"].keys():
                                primaryReturnType = self.globalScope[0][objectReturnType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectReturnType]["objects"].keys():
                                objectReturnType = self.globalScope[0][objectReturnType]["objects"][artifact]

                        if primaryReturnType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                self._simpleOrDoubleArithimeticExpressionOptional(primaryReturnType)
                        i += 1
                else:
                    i = 0
                    primaryReturnType = None
                    objectReturnType = None
                    for artifact in self.currentPathAttributeAccess:
                        if i == 0:
                            if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                                primaryReturnType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                                objectReturnType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                                if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                    primaryReturnType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                                else:
                                    objectReturnType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryReturnType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectReturnType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryReturnType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectReturnType = self.globalScope[0][inheritance]["objects"][artifact] 
                        elif objectReturnType:
                            if artifact in self.globalScope[0][objectReturnType]["variables"].keys():
                                primaryReturnType = self.globalScope[0][objectReturnType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectReturnType]["objects"].keys():
                                objectReturnType = self.globalScope[0][objectReturnType]["objects"][artifact]
                        
                        if primaryReturnType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                self._simpleOrDoubleArithimeticExpressionOptional(primaryReturnType)
                                
                        i += 1

                if not primaryReturnType:
                    self.semanticErrorsHandler("NONDECLARED")
                else:
                    if not primaryReturnType == self.scopeControl[0][self.currentMethodDefinition]["type"]:
                        self.semanticErrorsHandler("INCOMPATIBLE")
                    else:
                        self.nextLookahead()
                       
        if self.currentParametersMethodAccess:
            for key in self.currentParametersMethodAccess.keys():
                if key in self.currentParametersMethodAccess:
                    if not self.currentParametersMethodAccess[key] == primaryType and primaryType != None:
                        self.saveSemanticError("Excesso de Parâmetros, quantidade esperada: ", len(self.currentParametersMethodAccess.keys()), self.currentTokenLine)
                        self.loggerSemantic.E(self.errors[-1])
                        return
                    elif primaryType == None:
                        self.saveSemanticError("Excesso de Parâmetros, quantidade esperada: ", len(self.currentParametersMethodAccess.keys()), self.currentTokenLine)
                        self.loggerSemantic.E(self.errors[-1])
                else:
                    self.semanticErrorsHandler("NONDECLARED")
                    return




    def _endObjectAttributeAccess(self, primaryType: str = None):
        self.loggerSintax.I("_endObjectAttributeAccess")
        if self.match('.', True):
            self._multipleObjectAttributeAccess(primaryType)

    def _multipleObjectAttributeAccess(self, primaryType: str = None):
        self.loggerSintax.I("_multipleObjectAttributeAccess")
        self._decVariable(scope=self.scopeControl, idx=0, belongsTo=self.currentClassDefinition)
        self._endObjectAttributeAccess(primaryType)

    def _objectMethodOrObjectAccess(self):
        self.loggerSintax.I("_objectMethodOrObjectAccess")
        self._objectMethodOrObjectAccessOrPart()
    
    def _objectMethodOrObjectAccessOrPart(self, primaryType: str = None):
        self.loggerSintax.I("_objectMethodOrObjectAccessOrPart")
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()
        self._decObjectAttributeAccess(primaryType)
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
        self.currentParametersMethodAccess = None

    def _ideOrConstructor(self):
        self.loggerSintax.I("_ideOrConstructor")
        objectReturnType = None
        method = None
        if self.match('constructor', True, False):
            if self.currentAttributeAccess == "this":
                self.currentPathAttributeAccess.remove("this")
                i = 0
                for artifact in self.currentPathAttributeAccess:
                    if i == 0:
                        if artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectReturnType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectReturnType = self.globalScope[0][inheritance]["objects"][artifact]
                    elif objectReturnType:
                        if artifact in self.globalScope[0][objectReturnType]["objects"].keys():
                            objectReturnType = self.globalScope[0][objectReturnType]["objects"][artifact]                  

                    i += 1
            else:
                i = 0
                for artifact in self.currentPathAttributeAccess:
                    if i == 0:  
                        if artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                            objectReturnType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                        elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                            if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                self.semanticErrorsHandler("INCOMPATIBLE")
                                return
                            else:
                                objectReturnType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectReturnType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]  
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectReturnType = self.globalScope[0][inheritance]["objects"][artifact]       
                    elif objectReturnType:
                        if artifact in self.globalScope[0][objectReturnType]["objects"].keys():
                            objectReturnType = self.globalScope[0][objectReturnType]["objects"][artifact]
                                
                        i += 1
            if objectReturnType:
                method = self.globalScope[0][objectReturnType]["methods"][self.lookahead["value"]]                   
            if not method:
                self.semanticErrorsHandler("NONDECLARED")
            else:
                self.currentParametersMethodAccess = method["parameters"]
                self.nextLookahead()
            return
        elif self.matchTokenType('IDE', True, False):
            if self.currentAttributeAccess == "this":
                self.currentPathAttributeAccess.remove("this")
                i = 0
                for artifact in self.currentPathAttributeAccess:
                    if i == 0:
                        if artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectReturnType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectReturnType = self.globalScope[0][inheritance]["objects"][artifact]
                    elif objectReturnType:
                        if artifact in self.globalScope[0][objectReturnType]["objects"].keys():
                            objectReturnType = self.globalScope[0][objectReturnType]["objects"][artifact]                  

                    i += 1
            else:
                i = 0
                for artifact in self.currentPathAttributeAccess:
                    if i == 0:  
                        if artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                            objectReturnType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                        elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                            if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                self.semanticErrorsHandler("INCOMPATIBLE")
                                return
                            else:
                                objectReturnType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectReturnType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectReturnType = self.globalScope[0][inheritance]["objects"][artifact]         
                    elif objectReturnType:
                        if artifact in self.globalScope[0][objectReturnType]["objects"].keys():
                            objectReturnType = self.globalScope[0][objectReturnType]["objects"][artifact]
                                
                        i += 1

            if objectReturnType:
                method = self.globalScope[0][objectReturnType]["methods"][self.lookahead["value"]]                   
            if not method:
                self.semanticErrorsHandler("NONDECLARED")
            else:
                self.currentParametersMethodAccess = method["parameters"]
                self.nextLookahead()
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
        elif len(self.currentParametersMethodAccess.keys()) > 0:
            self.saveSemanticError("Falta de Parâmetros, quantidade esperada: ", len(self.currentParametersMethodAccess.keys()), self.currentTokenLine)
            self.loggerSemantic.E(self.errors[-1])
    
    def _value(self, returnDeFlag=False, returnFunction = False):
        self.loggerSintax.I("_value")
        arithmeticExpression = False
        if self.matchTokenType('NRO', True, False):
            if not re.match(pattern, self.lookahead["value"]) and not returnFunction:
                i = 0
                if self.currentAttributeAccess == "this":
                    self.currentPathAttributeAccess.remove("this")
                    primaryType = None
                    objectType = None
                    for artifact in self.currentPathAttributeAccess:   
                        if i == 0:
                            if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectType = self.globalScope[0][inheritance]["objects"][artifact]
                        elif objectType:
                            if artifact in self.globalScope[0][objectType]["variables"].keys():
                                primaryType = self.globalScope[0][objectType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectType]["objects"].keys():
                                objectType = self.globalScope[0][objectType]["objects"][artifact]

                        if primaryType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                self._simpleOrDoubleArithimeticExpressionOptional(primaryType)
                        i += 1
                else:
                    primaryType = None
                    objectType = None
                    for artifact in self.currentPathAttributeAccess:
                        if i == 0:
                            if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                                primaryType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                                objectType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                                if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                    primaryType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                                else:
                                    objectType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectType = self.globalScope[0][inheritance]["objects"][artifact] 
                        elif objectType:
                            if artifact in self.globalScope[0][objectType]["variables"].keys():
                                primaryType = self.globalScope[0][objectType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectType]["objects"].key():
                                objectType = self.globalScope[0][objectType]["objects"][artifact]
                        
                        if primaryType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                self.nextLookahead()
                                self._simpleOrDoubleArithimeticExpressionOptional(primaryType)
                                arithmeticExpression = True
                                
                        i += 1

                if not primaryType:
                    self.semanticErrorsHandler("NONDECLARED")
                else:
                    if not arithmeticExpression:
                        if len(self.lookahead["value"].split(".")) == 1:
                            if primaryType == 'int':
                                self.nextLookahead()
                            else:
                                self.semanticErrorsHandler("INCOMPATIBLE")
                        else:
                            if primaryType == 'real':
                                self.nextLookahead()
                            else:
                                self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                self.matchTokenType('NRO')
                primaryType = self.getPrimaryTypeFromAllScopesFromPath(self.currentAttributeAccess, copy.deepcopy(self.currentPathAttributeAccess))
                self._simpleOrDoubleArithimeticExpressionOptional(primaryType)

            return
        elif self.matchTokenType('CAC', True, False):
            if self.currentAttributeAccess:
                if self.currentAttributeAccess == "this":
                    self.currentPathAttributeAccess.remove("this")
                    primaryType = None
                    objectType = None
                    i = 0
                    for artifact in self.currentPathAttributeAccess:   
                        if i == 0:
                            if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectType = self.globalScope[0][inheritance]["objects"][artifact]
                        elif objectType:
                            if artifact in self.globalScope[0][objectType]["variables"].keys():
                                primaryType = self.globalScope[0][objectType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectType]["objects"].keys():
                                objectType = self.globalScope[0][objectType]["objects"][artifact]

                        if primaryType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                if not primaryType == "string":
                                    self.semanticErrorsHandler("INCOMPATIBLE")
                                else:
                                    self.nextLookahead()
                                    return
                        i += 1
                else:
                    i = 0
                    primaryType = None
                    objectType = None
                    for artifact in self.currentPathAttributeAccess:
                        if i == 0:
                            if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                                primaryType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                                objectType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                                if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                    primaryType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                                else:
                                    objectType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectType = self.globalScope[0][inheritance]["objects"][artifact] 
                        elif objectType:
                            if artifact in self.globalScope[0][objectType]["variables"].keys():
                                primaryType = self.globalScope[0][objectType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectType]["objects"].key():
                                objectType = self.globalScope[0][objectType]["objects"][artifact]
                        
                        if primaryType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                if not primaryType == "string":
                                    self.semanticErrorsHandler("INCOMPATIBLE")
                                else:
                                    self.nextLookahead()
                                    return
                                
                                
                        i += 1
            else:
                if not self.scopeControl[0][self.currentMethodDefinition]["type"] == "string":
                    self.semanticErrorsHandler("INCOMPATIBLE")
                else:
                    self.nextLookahead()
        elif self.match('[', True, False):
            self._vectorAssignBlock()
            return
        elif self.matchTokenType('IDE', True, False) or self.match('this', True, False):
            primaryType = self.getPrimaryTypeFromAllScopesFromPath(self.currentAttributeAccess, copy.deepcopy(self.currentPathAttributeAccess))
            if not self.ifConditionFlag:
                self._initExpression(primaryType, returnDeFlag=returnDeFlag)
            else:
                self._initExpression(primaryType, returnDeFlag=True)

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
    
    def _simpleOrDoubleArithimeticExpressionOptional(self, primaryType: str):
        self.loggerSintax.I("_simpleOrDoubleArithimeticExpressionOptional")
        if self.matchTokenType('ART', True, False):
            self._simpleOrDoubleArithimeticExpression(primaryType)
            return

    def _vectorAssignBlock(self):
        self.loggerSintax.I("_vectorAssignBlock")
        self.match('[')
        self._elementsAssign()
        self.match(']')

    def _initExpression(self, primaryType: str, returnDeFlag: bool = False):
        self.loggerSintax.I("_initExpression")
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()
        if not returnDeFlag:
            self._decObjectAttributeAccess(primaryType, returnValue=False)
        else:
            self._decObjectAttributeAccess(primaryType, returnValue=returnDeFlag)
        self._arithimeticOrlogicalExpression(primaryType)

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
        primaryType = self.getPrimaryTypeFromAllScopes(self.lookahead["value"])
        self.matchTokenType('NRO')
        self._endExpression(primaryType)

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
        self.currentAttributeAccess = None
        self.currentPathAttributeAccess = list()
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

    def _arithimeticOrlogicalExpression(self, primaryType):
        self.loggerSintax.I("_arithimeticOrlogicalExpression")
        if self.matchTokenType('ART', True, False):
            self._simpleOrDoubleArithimeticExpression(primaryType)
            return
        
        self._optionalObjectMethodAccess()
        self._logRelOptional()
        self._logicalExpressionEnd()
        
    def _logRelOptional(self):
        self.loggerSintax.I("_logRelOptional")
        if self.matchTokenType('REL', True, True):
            self.relationExpression = True
            self._relationalExpressionValue()
            self.relationExpression = False
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

        self.saveError(['!', '(', 'true', 'false', 'this', 'IDE'], self.lookahead["value"], self.currentTokenLine)
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
            self.currentAttributeAccess = None
            self.currentPathAttributeAccess = list()
            self._objectMethodOrObjectAccess()
            self._logRelOptional()
            self.currentAttributeAccess = None
            self.currentPathAttributeAccess = list()
            return

        self.saveError(['true', 'false', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _relationalExpressionValue(self):
        if len(self.currentPathAttributeAccess) > 0:
            i = 0
            if self.currentAttributeAccess == "this":
                self.currentPathAttributeAccess.remove("this")
                primaryType = None
                objectType = None
                for artifact in self.currentPathAttributeAccess:   
                    if i == 0:
                        if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                            primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                    elif objectType:
                        if artifact in self.globalScope[0][objectType]["variables"].keys():
                            primaryType = self.globalScope[0][objectType]["variables"][artifact]
                        elif artifact in self.globalScope[0][objectType]["objects"].keys():
                            objectType = self.globalScope[0][objectType]["objects"][artifact]

                    if primaryType:
                        if len(self.currentPathAttributeAccess) > i + 1:
                            self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                        else:
                            self._simpleOrDoubleArithimeticExpressionOptional(primaryType)
                    i += 1
            else:
                primaryType = None
                objectType = None
                for artifact in self.currentPathAttributeAccess:
                    if i == 0:
                        if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                            primaryType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                        elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                            objectType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                        elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                            if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                primaryType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                            else:
                                objectType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                            primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                        elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                            objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                        elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                            inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                            if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                            elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                objectType = self.globalScope[0][inheritance]["objects"][artifact]
                    elif objectType:
                        if artifact in self.globalScope[0][objectType]["variables"].keys():
                            primaryType = self.globalScope[0][objectType]["variables"][artifact]
                        elif artifact in self.globalScope[0][objectType]["objects"].key():
                            objectType = self.globalScope[0][objectType]["objects"][artifact]
                    
                    if primaryType:
                        if len(self.currentPathAttributeAccess) > i + 1: #Já encontrou um tipo primário, mas a path ainda tem elementos
                            self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário                  
                    i += 1

        if self.matchTokenType('NRO', True, False):
            if len(self.lookahead["value"].split(".")) == 1:
                if primaryType == 'int':
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                if primaryType == 'real':
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            return
        elif self.matchTokenType('IDE', True, False) or self.match('this', True, False):
            if self.relationExpression:
                primaryTypeMustToBe = primaryType
                self.currentAttributeAccess = None
                self.currentPathAttributeAccess = list()
            self._objectMethodOrObjectAccess()
            if self.relationExpression:
                i = 0
                if self.currentAttributeAccess == "this":
                    self.currentPathAttributeAccess.remove("this")
                    primaryType = None
                    objectType = None
                    for artifact in self.currentPathAttributeAccess:   
                        if i == 0:
                            if artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectType = self.globalScope[0][inheritance]["objects"][artifact]
                        elif objectType:
                            if artifact in self.globalScope[0][objectType]["variables"].keys():
                                primaryType = self.globalScope[0][objectType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectType]["objects"].keys():
                                objectType = self.globalScope[0][objectType]["objects"][artifact]

                        if primaryType:
                            if len(self.currentPathAttributeAccess) > i + 1:
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário
                            else:
                                self._simpleOrDoubleArithimeticExpressionOptional(primaryType)
                        i += 1
                else:
                    primaryType = None
                    objectType = None
                    for artifact in self.currentPathAttributeAccess:
                        if i == 0:
                            if artifact in self.scopeControl[0][self.currentMethodDefinition]["variables"].keys():
                                primaryType = self.scopeControl[0][self.currentMethodDefinition]["variables"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["objects"].keys():
                                objectType = self.scopeControl[0][self.currentMethodDefinition]["objects"][artifact]
                            elif artifact in self.scopeControl[0][self.currentMethodDefinition]["parameters"].keys():
                                if self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact] in typesVar:
                                    primaryType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                                else:
                                    objectType = self.scopeControl[0][self.currentMethodDefinition]["parameters"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["variables"].keys():
                                primaryType = self.globalScope[0][self.currentClassDefinition]["variables"][artifact]
                            elif artifact in self.globalScope[0][self.currentClassDefinition]["objects"].keys():
                                objectType = self.globalScope[0][self.currentClassDefinition]["objects"][artifact]
                            elif self.globalScope[0][self.currentClassDefinition]["inheritance"]:
                                inheritance = self.globalScope[0][self.currentClassDefinition]["inheritance"]
                                if artifact in self.globalScope[0][inheritance]["variables"].keys():
                                    primaryType = self.globalScope[0][inheritance]["variables"][artifact]
                                elif artifact in self.globalScope[0][inheritance]["objects"].keys():
                                    objectType = self.globalScope[0][inheritance]["objects"][artifact]
                        elif objectType:
                            if artifact in self.globalScope[0][objectType]["variables"].keys():
                                primaryType = self.globalScope[0][objectType]["variables"][artifact]
                            elif artifact in self.globalScope[0][objectType]["objects"].keys():
                                objectType = self.globalScope[0][objectType]["objects"][artifact]
                        
                        if primaryType:
                            if len(self.currentPathAttributeAccess) > i + 1: #Já encontrou um tipo primário, mas a path ainda tem elementos
                                self.semanticErrorsHandler("INCOMPATIBLE") # O proximo seria uma tentativa de acessar um tipo primário através de um tipo primário                  
                        i += 1

                if not primaryTypeMustToBe == primaryType:
                    self.saveSemanticError(incompatible, self.lookahead["value"], self.currentTokenLine)
                    self.loggerSemantic.E(self.errors[-1])

            return
        elif self.matchTokenType('CAC', True, False):
            if not primaryType == "string":
                self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                self.nextLookahead()
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
        if self.matchTokenType('NRO', True, False):
            if len(self.lookahead["value"].split(".")) == 1:
                if self.scopeControl[0][self.currentMethodDefinition]["type"] == "int":
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                if self.scopeControl[0][self.currentMethodDefinition]["type"] == "real":
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
        elif self.matchTokenType('CAC', True, False): 
            if not self.scopeControl[0][self.currentMethodDefinition]["type"] == "string":
                self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                self.nextLookahead()         
            return   
        elif self.matchTokenType('IDE', True, False): 
            primaryType = self.getPrimaryTypeFromAllScopes(self.lookahead["value"])
            if not primaryType == self.scopeControl[0][self.currentMethodDefinition]["type"]:
                self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                self.nextLookahead()         
            return
        elif self.match('[', True, False):
            self._nDimensionsAssign()
            return
        else:
            self.saveError(['IDE', 'CAC', 'NRO', '['], self.lookahead["value"], self.currentTokenLine)
            self.nextLookahead()
            self.loggerSintax.E(self.errors[-1])

    def _nDimensionsAssign(self):
        self.loggerSintax.I("_nDimensionsAssign")
        if self.match('[', True):
            self._elementsAssign()
            self.match(']')
            return

    def _simpleOrDoubleArithimeticExpression(self, primaryType: str):
        self.loggerSintax.I("_simpleOrDoubleArithimeticExpression")
        if self.match(['+', '-', '*', '/'], True, False):
            self._endExpression(primaryType)
            return
        elif self.match(['++', '--'], True, False):
            if not primaryType == "int":
                self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                self.match(['++', '--'])
            return

    def _endExpression(self, primaryType: str = None):
        self.loggerSintax.I("_endExpression")
        self.matchTokenType('ART')
        self._partLoop(primaryType)    

    def _partLoop(self, primaryType: str):
        self.loggerSintax.I("_partLoop")
        if self.matchTokenType(['NRO', 'IDE'], True, False):
            self._part(primaryType)
            self._endExpressionOptional(primaryType)
            return
        elif self.match('(', True, False):
            self._parenthesisExpression(primaryType)
            return
        
        self.saveError(['NRO', '('], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])

    def _part(self, primaryType: str):
        self.loggerSintax.I("_part")
        if self.matchTokenType('NRO', True, False):
            if len(self.lookahead["value"].split(".")) == 1:
                if primaryType == 'int':
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            else:
                if primaryType == 'real':
                    self.nextLookahead()
                else:
                    self.semanticErrorsHandler("INCOMPATIBLE")
            return
        elif self.matchTokenType('IDE', True, False):
            self._objectMethodOrObjectAccessOrPart(primaryType)
            return
        
        self.saveError(['NRO', 'IDE'], self.lookahead["value"], self.currentTokenLine)
        self.nextLookahead()
        self.loggerSintax.E(self.errors[-1])
    
    def _endExpressionOptional(self, primaryType: str):
       self.loggerSintax.I("_endExpressionOptional")
       if self.matchTokenType('ART', True, False):
           self._endExpression(primaryType)
           return
       
    def _parenthesisExpression(self, primaryType: str = ""):
        self.loggerSintax.I("_parenthesisExpression")
        self.match('(')
        self._simpleExpression(primaryType)
        self.match(')')
        self._endExpressionOptional()

    def _simpleExpression(self, primaryType: str = ""):
        self.loggerSintax.I("_simpleExpression")
        if self.matchTokenType(['NRO', 'IDE'], True, False):
            self._part(primaryType)
            self._endExpression(primaryType) 
            return
        elif self.match('(', True, False):
            self._parenthesisExpression(primaryType)
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
        if self.match(['[', '!', '(', 'this'], True, False) or self.matchTokenType(['NRO', 'CAC', 'IDE'], True, False):
            returnFunction = False
            if re.match(pattern, self.lookahead["value"]):
                returnFunction = True
            self._value(returnFunction)
            return

    def _mainType(self):
        if self.match(typesVar, True, False):
            self.tempVar = self.lookahead["value"]
            self.nextLookahead()
            return
        elif self.match("void", True, False):
            self.tempVar = self.lookahead["value"]
            self.nextLookahead()
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
        self.outputFile.close()
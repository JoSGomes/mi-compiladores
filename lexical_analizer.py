import os 
import re
from enum import Enum
from token_1 import Token

PATH_FILES = "./files"
preList = [
        "variables", 
        "const", 
        "class", 
        "methods", 
        "objects", 
        "main", 
        "return", 
        "if", 
        "else", 
        "then", 
        "for", 
        "read", 
        "print", 
        "void", 
        "int", 
        "real", 
        "boolean", 
        "string", 
        "true", 
        "false",
        "this",
        "constructor",
        "extends"
    ]

artList = ["+", "-", "*", "/", "++", "--"] # Feito
relList = ["!=", "==", "<", ">", "<=", ">=", "="] #Feito
logList = ["!", "&", "|"] #Feito
comList = ["/*", "*/"] #Feito

delList = [";", ".", ",", "(", ")", "[", "]", "{", "}", " "] #Feito
digRegex = re.compile('[0-9]') #Feito
wordRegex = re.compile('[a-z]|[A-Z]') #Feito
cadCaracRegex = re.compile(r'\w*[\u0020-\u0021]*[\u0023-\u0080]*', re.ASCII) #Feito
quote = ['"']
others = ["\n", '\t']

separatorForNumbers = [";", ",", "(", ")", "[", "]", "{", "}", " "] + logList + relList + artList + quote + others
separatorForTMFIDELOG = delList + logList + relList + artList + quote + others

tokensOutput = []
class Acronym(Enum):
    PRE  = "PRE"    #palavra reservada
    IDE  = "IDE"    #identificador
    CAC  = "CAC"    #cadeia de caracteres
    NRO  = "NRO"    #numero
    DEL  = "DEL"    #delimitador
    REL  = "REL"    #operador relacional
    LOG  = "LOG"    #operador logico
    ART  = "ART"    #operador aritmetico
    CMF  = "CMF"    #cadeia mal formada
    COMF = "COMF"   #comentário mal formado
    NMF  = "NMF"    #numero mal formado
    IMF  = "IMF"    #identificador mal formado
    TMF  = "TMF"    #token mal formado

class LexicalAnalizer():

    def __init__(self,  directory: str):
        self.filesPath = directory
        self.inputFile = None
        self.outputFile = None
        #Estados
        self.q0 = False #Identifica uma letra, então pode ser PRE ou IDE
        self.q01 = False #Estado de erro quando um símbolo fora do ASCII delimitado é encontrado
        self.q1 = False #Identifica um digito, então pode ser um NRO, com resalva de que se for identificado um ".", deve ter um
                        # número em seguida, se não tiver então determina um NRO e depois um DEL.
        self.q11 = False #Identificado um digito com . NRO
        self.q111 = False #Estado de erro de digito com .
        self.q112 = False #Estado para quando se encontra " após o .
        self.q113 = False #Estado para quando se encontra / após o .
        self.q114 = False #Estado para quando se encontra qualquer REL, LOG, DEL ou ART após o .
        self.q12 = False #Estado de erro de digito que não foi seguido de qualquer delimitador ou .
        self.q13 = False #Estado para CDC após Digito (2"ABC" ou 2" etc)


        self.q2 = False #Se for [+, -, *, /, ++, --]
        self.q21 = False #Se for [+, *], então é verificado se no próximo símbolo há um +, senão é +. Se for * ele já é classificado como ART.
        self.q211 = False #Se for +, então é ++ e é ART.

        self.q22 = False #Se for [-], é verificado se no próximo símbolo há um -, se não se há um >.
        self.q221 = False #Se for -, então é -- e é ART.
        self.q222 = False # se for >, então é -> e é DEL.

        self.q23 = False # Se for /, então é verificado se no próximo é / ou *.
        self.q231 = False # Se for /, então é comentário de linha, ESTADO qCommentLine anula todos o estados atuais.
        self.q232 = False # Se for *, então é comentário de bloco, ESTADO qCommentBlock anula todos o estados atuais.

        self.q3 = False # Se for [!, &, |]
        self.q31 = False # Se for !, então é verificador se no próximo é um =, se não for então é ! que é LOG.
        self.q311 = False # Se for =, então é != que é REL.
        self.q32 = False # Se for &, então é um && que é LOG.
        self.q321 = False # Estado de erro se existir somente um & ou | no lexema

        self.q4 = False # Se for = é verificado o próximo símbolo se há um =, se não for então é = que é REL.
        self.q41 = False # Se for  um =, então é == que é um REL.

        self.q5 = False # Se for >, então é verificado se o próximo símbolo é um =, se não for então é > que é REL.
        self.q51= False # Se for =, então é >= que é REL.

        self.q6= False # Se for <, é verificado se no próximo símbolo é =, se não é um < que é REL
        self.q61= False # Se for =, então é <= que é REL.

        self.q7 = False # Se for [; . ( ) [ ] { } ' '] é instantaneamente delimitador DEL

        self.q8 = False # Se for ", então é início de uma cadeia de caracteres e é verificado se o próximo é ", letra, digito ou simbolo (ASCII 32 a 126 exceto 34).
        self.q81 = False #Estado de erro de que o símbolo não está no alfabeto

        self.q9 = False #Estado de erro para símbolos fora do alfabeto TMF.

        self.commentLine = False
        self.commentBlock = False

        self.errors = [] #Vetor de erros
        
        self.tokens = {}
        
        self.dirsOutput = []

    def analize(self):
        dirs = os.listdir(self.filesPath)
        for dir in dirs:  
            if not dir.endswith("_saida.txt"):             
                self.inputFile = open(self.filesPath + "/" + dir, "r", encoding="utf8")
                self.tokens = {
                    "output": self.filesPath + "/" + dir.split(".")[0] + "_saida.txt",
                    "tokens": []
                }
                
                lineCount = 1
                buffer = ""
                for line in self.inputFile.readlines():                    
                    symbolCount = 0
                    for symbol in line:
                        if not self.commentLine and not self.commentBlock:
                            #Existe algum estado ativo? se não, começar a determinar o estado atual
                            if not (self.q0 or self.q1 or self.q2 or self.q3 or self.q4 or self.q5 or self.q6 or self.q7 or self.q8 or self.q9) :
                                if re.search(wordRegex, symbol):
                                    self.q0 = True
                                elif re.search(digRegex, symbol):
                                    self.q1 = True
                                elif symbol in artList:
                                    self.q2 = True
                                elif symbol in logList:
                                    self.q3 = True
                                elif symbol == "=":
                                    self.q4 = True
                                elif symbol == ">":
                                    self.q5 = True
                                elif symbol == "<":
                                    self.q6 = True
                                elif symbol in delList:
                                    self.q7 = True
                                elif symbol == "\"":
                                    self.q8 = True
                                elif re.search(cadCaracRegex, symbol).group(0) and not symbol == "\n":
                                    self.q9 = True

                            if self.q0:
                                if (re.search(wordRegex, symbol) or re.search(digRegex, symbol) or symbol == "_") and not self.q01:                                  
                                    if symbol != "\n":
                                        buffer =  buffer + symbol
                                    if len(line) == symbolCount+1:
                                        if buffer in preList:
                                            buffer = self.writeIdentifiedToken(Token(Acronym.PRE.value, buffer, lineCount))
                                            
                                        else:
                                            buffer = self.writeIdentifiedToken(Token(Acronym.IDE.value, buffer, lineCount))
                                        self.q0 = False
                                    elif len(line) > symbolCount+1:
                                        if line[symbolCount+1] in separatorForTMFIDELOG:
                                            if buffer in preList:
                                                buffer = self.writeIdentifiedToken(Token(Acronym.PRE.value, buffer, lineCount))
                                                
                                            else:
                                                buffer = self.writeIdentifiedToken(Token(Acronym.IDE.value, buffer, lineCount))
                                            self.q0 = False
                                else:
                                    self.q01 = True
                                
                                if self.q01:
                                    buffer = buffer + symbol
                                    if len(line) > symbolCount+1:
                                        if line[symbolCount+1] in separatorForTMFIDELOG:
                                            self.errors.append(Token(Acronym.IMF.value, buffer, lineCount))
                                            buffer = ""
                                            self.q0 = False
                                            self.q01 = False
                                    elif len(line) == symbolCount+1:
                                        self.errors.append(Token(Acronym.IMF.value, buffer, lineCount))
                                        buffer = ""

                                        self.q0 = False
                                        self.q01 = False
                                                        

                            if self.q1:
                                if symbol == "." and not self.q13 and not self.q11 and not self.q12: #Estado de número com .
                                    self.q11 = True       

                                elif symbol == quote[0] and not self.q11 and not self.q12 and not self.q13:
                                    self.q13 =  True
                                    
                                elif not re.search(digRegex, symbol) and not self.q13 and not self.q11 and not self.q12:  #Próximo não é número, então ativa estado de erro
                                    self.q12 = True

                                elif not self.q13 and not self.q11 and not self.q12: 
                                    if len(line) == symbolCount+1:
                                        if symbol != "\n":
                                            buffer = buffer + symbol

                                        buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                        self.q1 = False
                                    elif len(line) > symbolCount+1:
                                        buffer = buffer + symbol
                                        if line[symbolCount+1] in separatorForNumbers:
                                            if line[symbolCount+1] in ('&', '|'):
                                                if len(line) > symbolCount+2:
                                                    if line[symbolCount+1] == '&':
                                                        if line[symbolCount+2] == '&':
                                                            buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                                            self.q1 = False

                                                    else:
                                                        if line[symbolCount+2] == '|':
                                                            buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                                            self.q1 = False
                                                else:
                                                    continue #Estado de erro será ativado na próxima iteração
                                            else:
                                                buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                                self.q1 = False
                                        
                                if self.q11:
                                    if len(line) > symbolCount+1 and not self.q111 and not self.q112 and not self.q113 and not self.q114 and self.q11:
                                        if line[symbolCount+1] == quote[0]:
                                            self.q112 = True
                                        if line[symbolCount+1] == "/":
                                            if len(line) > symbolCount+2:  
                                                if not line[symbolCount+2] == "/" and not line[symbolCount+2] == "*":
                                                    self.q113 = True
                                            else:
                                                self.q113 = True
    
                                        if line[symbolCount+1] in separatorForNumbers or (not re.search(digRegex, symbol) and not symbol == ".") and not self.q112 and not self.q113 and not self.q114 and self.q11:
                                            if re.search(digRegex, symbol):
                                                buffer = buffer + symbol
                                                buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                                self.q1 = False
                                                self.q11 = False
                                            else:
                                                self.q114 = True

                                        if re.search(digRegex, symbol) or (symbol == "." and "." not in buffer) and not self.q111 and not self.q112 and not self.q113 and not self.q114 and self.q11:
                                            buffer = buffer + symbol
                                        elif not self.q112 and not self.q113 and not self.q114:
                                            self.q111 = True


                                        if line[symbolCount+1] in separatorForNumbers and not self.q111 and not self.q112 and not self.q113 and not self.q114 and self.q11:
                                            if buffer.endswith(".") or len(buffer.split(".")) > 2:
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                            else:
                                                buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                            self.q11 = False
                                            self.q1 = False

                                    elif len(line) == symbolCount+1 and not self.q111 and not self.q112 and not self.q113 and not self.q114 and self.q11:
                                        buffer = buffer + symbol
                                        if buffer.endswith(".") or len(buffer.split(".")) > 2 or re.search(wordRegex, buffer) or not re.search(cadCaracRegex, buffer):
                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                            buffer = ""
                                        else:
                                            buffer = self.writeIdentifiedToken(Token(Acronym.NRO.value, buffer, lineCount))
                                        self.q11 = False
                                        self.q1 = False

                                    if self.q111: 
                                        if len(line) > symbolCount+1:
                                            if line[symbolCount+1] in separatorForNumbers:
                                                buffer = buffer + symbol
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q111 = False
                                                self.q11 = False
                                                self.q1 = False
                                            else:
                                                buffer = buffer + symbol

                                        elif re.search(wordRegex, buffer) or re.search(cadCaracRegex, buffer):
                                            buffer = buffer + symbol
                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                            buffer = ''                                          
                                            self.q111 = False
                                            self.q11 = False
                                            self.q1 = False

                                    if self.q112:
                                        if len(line) > symbolCount+1:
                                            if line[symbolCount+1] in separatorForNumbers and (len(buffer.split(".")) == 2 and not buffer.split(".")[1] == '') or len(buffer.split(".")) > 2:
                                                buffer = buffer + symbol
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q112 = False
                                                self.q11 = False
                                                self.q1 = False
                                                if symbol == quote[0]:
                                                    self.q8 = True
                                            else:
                                                buffer = buffer + symbol
                                        else:
                                            buffer = buffer + symbol
                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                            buffer = ""
                                            self.q112 = False
                                            self.q11 = False
                                            self.q1 = False
                                        
                                    
                                    if self.q113:
                                        buffer = buffer + symbol
                                        if len(line) > symbolCount+1:
                                            if line[symbolCount+1] in separatorForNumbers and (len(buffer.split(".")) == 2 and not buffer.split(".")[1] == '') or len(buffer.split(".")) > 2:
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q113 = False
                                                self.q11 = False
                                                self.q1 = False
                                        else:
                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                            buffer = ""
                                            self.q113 = False
                                            self.q11 = False
                                            self.q1 = False

                                    if self.q114:
                                        buffer = buffer + symbol
                                        if len(line) > symbolCount+1:
                                            if len(line) > symbolCount+2:
                                                if line[symbolCount+1] == "/":
                                                    if line[symbolCount+2] == "/" or line[symbolCount+2] == "*":
                                                        self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                        buffer = ""
                                                        self.q114 = False
                                                        self.q11 = False
                                                        self.q1 = False
                                                elif line[symbolCount+1] == quote[0]:
                                                    self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                    buffer = ""
                                                    self.q114 = False
                                                    self.q11 = False
                                                    self.q1 = False

                                            if line[symbolCount+1] in separatorForNumbers and (len(buffer.split(".")) == 2 and not buffer.split(".")[1] == '') or (len(buffer.split(".")) > 2 and line[symbolCount+1] in separatorForNumbers):
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q114 = False
                                                self.q11 = False
                                                self.q1 = False
                                                
                                            elif line[symbolCount+1] == " ":
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q114 = False
                                                self.q11 = False
                                                self.q1 = False
                                        else:
                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                            buffer = ""
                                            self.q114 = False
                                            self.q11 = False
                                            self.q1 = False

                                if self.q12:
                                    if len(line) > symbolCount+1:
                                        if line[symbolCount+1] in separatorForNumbers:
                                            if line[symbolCount+1] in ('&', '|'):
                                                if len(line) > symbolCount+2:
                                                    if line[symbolCount+1] == '&':
                                                        if line[symbolCount+2] == '&':
                                                            buffer = buffer + symbol
                                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                            buffer = ""
                                                            self.q12 = False
                                                            self.q1 = False
                                                    else:
                                                        if line[symbolCount+2] == '|':
                                                            buffer = buffer + symbol
                                                            self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                            buffer = ""
                                                            self.q12 = False
                                                            self.q1 = False
                                                else:
                                                    buffer = buffer + symbol
                                            else:
                                                buffer = buffer + symbol
                                                self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q12 = False
                                                self.q1 = False
                                        else:
                                            buffer = buffer + symbol
                                    else:
                                        buffer = buffer + symbol
                                        self.errors.append(Token(Acronym.NMF.value, buffer, lineCount))
                                        buffer = ""
                                        self.q12 = False
                                        self.q1 = False

                                if self.q13:
                                    buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                    self.q13 = False
                                    self.q1 = False
                                    
                                    self.q8 = True
                            
                            if self.q2:
                                if symbol in ("+", "*") and not self.q22 and not self.q23:
                                    self.q21 = True
                                if symbol == "-" and not self.q21 and not self.q23:
                                    self.q22 = True
                                if symbol == "/" and not self.q22 and not self.q21:
                                    self.q23 = True
                                
                                if self.q21:
                                    if len(line) == symbolCount+1: 
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                        self.q21 = False
                                        self.q2 = False

                                    elif line[symbolCount+1] != "+" and not self.q221:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                        self.q21 = False
                                        self.q2 = False
                                    else:
                                        self.q221 = True

                                    if self.q221:
                                        buffer = buffer + symbol
                                        if (buffer == "++"):
                                            buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                            self.q221 = False
                                            self.q21 = False
                                            self.q2 = False

                                if self.q22:
                                    if not len(line) == symbolCount+1:
                                        if line[symbolCount+1] == "-" and not self.q222 and not self.q221:
                                            self.q221 = True
                                        elif line[symbolCount+1] == ">" and not self.q221 and not self.q222:
                                            self.q222 = True
                                    if (not self.q222 and not self.q221) and (len(line) == symbolCount+1 or symbol == "-"):
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                        self.q22 = False
                                        self.q2 = False

                                    if self.q221:
                                        buffer = buffer + symbol
                                        if buffer == "--":
                                            buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                            self.q221 = False
                                            self.q22 = False
                                            self.q2 = False

                                    if self.q222:
                                        buffer = buffer + symbol
                                        if(buffer == "->"):
                                            buffer = self.writeIdentifiedToken(Token(Acronym.DEL.value, buffer, lineCount))
                                            self.q222 = False
                                            self.q22 = False
                                            self.q2 = False

                                if self.q23:
                                    if len(line) > symbolCount+1 and not self.q232:
                                        if line[symbolCount+1] == "/":
                                            self.q231 = True
                                        elif line[symbolCount+1] == "*":
                                            self.q232 = True
                                        else:
                                            buffer = buffer + symbol
                                            buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                        self.q23 = False
                                        self.q2 = False
                                    elif len(line) == symbolCount+1 and not self.q232:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.ART.value, buffer, lineCount))
                                        self.q23 = False
                                        self.q2 = False                                   

                                    if self.q231:
                                        buffer = buffer + symbol
                                        self.commentLine = True
                                        self.q231 = False
                                        self.q23 = False
                                        self.q2 = False

                                    if self.q232:
                                        self.commentBlock = True
                                        self.q232 = False
                                        self.q23 = False
                                        self.q2 = False
                                
                            if self.q3:
                                if len(line) == symbolCount+1 and not self.q31 and not self.q32: 
                                    if symbol == "!":
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.LOG.value, buffer, lineCount))
                                        self.q3 = False                      
                                    elif (symbol == "&" or symbol == "|"):
                                        self.q32 = True                  
                                elif len(line) > symbolCount+1 and not self.q31 and not self.q32:
                                    if line[symbolCount+1] == "=":
                                        self.q31 = True
                                    elif (symbol == "&" or symbol == "|"):
                                        self.q32 = True 
                                    elif not self.q31 and not self.q32:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.LOG.value, buffer, lineCount))
                                        self.q3 = False
                                elif not self.q32 and not self.q31:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.LOG.value, buffer, lineCount))
                                    self.q3 = False

                                if self.q31:
                                    buffer = buffer + symbol
                                    if buffer == "!=":
                                        buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                        self.q31 = False
                                        self.q3 = False

                                if self.q32:
                                    buffer = buffer + symbol
                                    if (buffer == "&&" or buffer == "||") and not self.q321:
                                        buffer = self.writeIdentifiedToken(Token(Acronym.LOG.value, buffer, lineCount))
                                        self.q32 = False
                                        self.q3 = False

                                    if symbol == "&" and not self.q321 and self.q32:
                                        if len(line) > symbolCount+1:
                                            if line[symbolCount+1] != "&":
                                                self.q321 = True
                                        elif len(line) == symbolCount+1:
                                            self.q321 = True
                                    elif symbol == "|" and not self.q321 and self.q32:
                                        if len(line) > symbolCount+1:
                                            if line[symbolCount+1] != "|":
                                                self.q321 = True
                                        elif len(line) == symbolCount+1:
                                            self.q321 = True
                  
                                    if self.q321:
                                        if len(line) > symbolCount+1:
                                            if line[symbolCount+1] in separatorForTMFIDELOG:
                                                self.errors.append(Token(Acronym.TMF.value, buffer, lineCount))
                                                buffer = ""
                                                self.q321 = False
                                                self.q32 = False
                                                self.q3 = False
                                        elif len(line) == symbolCount+1:
                                            self.errors.append(Token(Acronym.TMF.value, buffer, lineCount))
                                            buffer = ""
                                            self.q321 = False
                                            self.q32 = False
                                            self.q3 = False
                            
                            if self.q4:
                                if not len(line) == symbolCount+1 and not self.q41:
                                    if line[symbolCount+1] == "=":
                                        self.q41 = True
                                    else:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                    self.q4 = False
                                elif not self.q41:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                    self.q4 = False
                                
                                if self.q41:                                  
                                    buffer = buffer + symbol
                                    if buffer == "==":
                                        buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                        self.q41 = False
                                        self.q4 = False

                            if self.q5:
                                if line[symbolCount+1] == "=":
                                    self.q51 = True
                                elif not self.q51:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                    self.q5 = False
                                
                                if self.q51:
                                    buffer = buffer + symbol
                                    if buffer == ">=":
                                        buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                        self.q51 = False
                                        self.q5 = False

                            if self.q6:
                                if line[symbolCount+1] == "=":
                                    self.q61 = True
                                else:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                    self.q6 = False
                                
                                if self.q61:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.REL.value, buffer, lineCount))
                                    self.q61 = False
                                    self.q6 = False 

                            if self.q7:
                                if symbol != ' ' and symbol != '\n':
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.DEL.value, buffer, lineCount))
                                    self.q7 = False

                                if symbol == ' ':
                                    self.q7 = False

                            if self.q8:
                                if buffer == "" and not self.q81:
                                    buffer = buffer + symbol
                                elif buffer.startswith(quote[0]) and symbol == quote[0] and buffer != quote[0] and not self.q81:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(Token(Acronym.CAC.value, buffer, lineCount))
                                    self.q8 = False
                                
                                elif re.search(cadCaracRegex, symbol).group(0) and symbol != quote[0] and not self.q81:
                                    buffer = buffer + symbol
                                elif not re.search(cadCaracRegex, symbol).group(0) and not self.q81:
                                    self.q81 = True
                                elif buffer == "\n" and not self.q81:
                                    self.errors.append(Token(Acronym.CMF.value, buffer, lineCount))
                                    buffer = ""
                                    self.q8 = False

                                if self.q81:
                                    if symbol == quote[0]:
                                        buffer = buffer + symbol
                                        self.errors.append(Token(Acronym.CMF.value, buffer, lineCount))
                                        buffer = ""
                                        self.q81 = False
                                        self.q8 = False
                                    elif symbol == "\n":
                                        self.errors.append(Token(Acronym.CMF.value, buffer, lineCount))
                                        buffer = ""
                                        self.q81 = False
                                        self.q8 = False
                                    else:
                                        buffer = buffer + symbol

                            if self.q9:
                                buffer = buffer + symbol
                                if len(line) > symbolCount+1:
                                    if line[symbolCount+1] in separatorForTMFIDELOG:
                                        self.errors.append(Token(Acronym.TMF.value, buffer, lineCount))
                                        buffer = ""
                                        self.q9 = False
                                elif len(line) == symbolCount+1:
                                    self.errors.append(Token(Acronym.TMF.value, buffer, lineCount))
                                    buffer = ""
                                    self.q9 = False

                        if self.commentLine:
                            if symbol == "\n":
                                self.commentLine = False
                                buffer = ""

                        if self.commentBlock: 
                            buffer = buffer + symbol
                                
                            if buffer.endswith("*/"):
                                self.commentBlock = False
                                buffer = ""

                        if self.q8 or self.q81:
                            if len(line) > symbolCount+1:
                                if line[symbolCount+1] == "\n":
                                    self.errors.append(Token(Acronym.CMF.value, buffer, lineCount))
                                    buffer = ""
                                    self.q81 = False
                                    self.q8 = False
                            if  len(line) == symbolCount+1:
                                self.errors.append(Token(Acronym.CMF.value, buffer, lineCount))
                                buffer = ""
                                self.q81 = False
                                self.q8 = False

                        symbolCount += 1
                    lineCount += 1
                if self.commentBlock:
                    self.errors.append(Token(Acronym.COMF.value, buffer.replace("\n", " "), lineCount))
                    buffer = ""
                    self.commentBlock = False

                if len(self.errors) == 0:
                    pass
                    #print("############ Arquivo foi analisado com sucesso! ############")
                else:
                    #print("\n############ Erros léxicos encontrados ############")
                    for error in self.errors:
                        self.writeIdentifiedToken(error)
                    
                    self.errors = []

                tokensOutput.append(self.tokens)
                self.inputFile.close()

        return tokensOutput

    def writeIdentifiedToken(self, token: Token):
        self.tokens["tokens"].append(
                {
                    "type": token.getName(),
                    "value": token.getValue(),
                    "line": token.getLine()
                },
            )
        return ""
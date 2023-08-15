from io import TextIOWrapper
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
        "false"
    ]

artList = ["+", "-", "*", "/", "++", "--"] # Feito
relList = ["!=", "==", "<", ">", "<=", "=>", "="] #Feito
logList = ["!", "&", "|"] #Feito
comList = ["/*", "*/"] #Feito

delList = [";", ".", ",", "(", ")", "[", "]", "{", "}", " "] #Feito
digRegx = re.compile('[0-9]') #Feito
wordRegx = re.compile('[a-z]|[A-Z]') #Feito
cadCaracRegx = re.compile('\w*[\u0020-\u0021]*[\u0023-\u0080]*', re.ASCII) #Feito
quote = '"'



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
        self.q1 = False #Identifica um digito, então pode ser um NRO, com resalva de que se for identificado um ".", deve ter um
                        # número em seguida, se não tiver então determina um NRO e depois um DEL.
        self.q11 = False #Identificado um digito com . NRO

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
        self.q32 = False # Se for |, então é um || que é LOG.

        self.q4 = False # Se for = é verificado o próximo símbolo se há um =, se não for então é = que é REL.
        self.q41 = False # Se for  um =, então é == que é um REL.

        self.q5 = False # Se for >, então é verificado se o próximo símbolo é um =, se não for então é > que é REL.
        self.q51= False # Se for =, então é >= que é REL.

        self.q6= False # Se for <, é verificado se no próximo símbolo é =, se não é um < que é REL
        self.q61= False # Se for =, então é <= que é REL.

        self.q7 = False # Se for [; . ( ) [ ] { } ' '] é instantaneamente delimitador DEL

        self.q8 = False # Se for ", então é início de uma cadeia de caracteres e é verificado se o próximo é ", letra, digito ou simbolo (ASCII 32 a 126 exceto 34).
        #self.q81 = False # Se for ", então é fechada.
        #self.q82 = False #Se for letra, digito ou simbolo então é incremetado, se não é ignorado.

        #self.q9 = False #Se for * e o próximo simbolo for /, então terminou o comentario de bloco.

        self.commentLine = False
        self.commentBlock = False

    def analize(self):
        dirs = os.listdir(self.filesPath)
        for dir in dirs:
            if not dir.endswith("_output.txt"):
                self.inputFile = open(self.filesPath + "/" + dir, "r")
                self.outputFile = open(self.filesPath + "/" + dir.split(".")[0] + "_output.txt", "w")
                lineCount = 1
                print(dir)
                for line in self.inputFile.readlines():
                    buffer = ""
                    symbolCount = 0
                    for symbol in line:
                        if not self.commentLine and not self.commentBlock:
                            #Existe algum estado ativo? se não, começar a determinar o estado atual
                            if not (self.q0 or self.q1 or self.q2 or self.q3 or self.q4 or self.q5 or self.q6 or self.q7 or self.q8) :
                                if re.search(wordRegx, symbol):
                                    self.q0 = True
                                elif re.search(digRegx, symbol):
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

                            if self.q0:
                                if symbol != "\n":
                                    buffer =  buffer + symbol
                                if len(line) == symbolCount+1:
                                    if buffer in preList:
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.PRE.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        
                                    else:
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.IDE.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                    self.q0 = False
                                elif line[symbolCount+1] in delList or line[symbolCount+1] in logList or line[symbolCount+1] in artList or line[symbolCount+1] in relList or line[symbolCount+1] in "\"":
                                    if buffer in preList:
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.PRE.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        
                                    else:
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.IDE.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                    self.q0 = False

                            if self.q1:
                                if symbol == "." and not self.q11:
                                    if re.search(digRegx, line[symbolCount+1]):
                                        buffer = buffer + symbol
                                        self.q11 = True               
                                    else:  
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.NRO.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q11 = False
                                        self.q1 = False
                                elif not symbol == "\n":
                                    buffer = buffer + symbol

                                if symbol == "\n":
                                    buffer = self.writeIdentifiedToken(
                                                Token(Acronym.NRO.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )
                                    self.q11 = False
                                    self.q1 = False
                                elif line[symbolCount+1] != ".":
                                    if line[symbolCount+1] in delList or line[symbolCount+1] in logList or line[symbolCount+1] in artList or line[symbolCount+1] in relList or line[symbolCount+1] in "\"":                                       
                                        buffer = self.writeIdentifiedToken(
                                                Token(Acronym.NRO.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )
                                        self.q11 = False
                                        self.q1 = False
                                else:
                                    if len(line) >= symbolCount + 2:
                                        if not re.search(digRegx, line[symbolCount+2]):
                                            buffer = self.writeIdentifiedToken(
                                                Token(Acronym.NRO.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )  
                                            self.q11 = False
                                            self.q1 = False                                       
                                    else:
                                        buffer = self.writeIdentifiedToken(
                                                Token(Acronym.NRO.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )
                                        self.q11 = False
                                        self.q1 = False
                            
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
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.ART.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q21 = False
                                        self.q2 = False

                                    elif line[symbolCount+1] != "+" and not self.q221:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.ART.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q21 = False
                                        self.q2 = False
                                    else:
                                        self.q221 = True

                                    if self.q221:
                                        buffer = buffer + symbol
                                        if (buffer == "++"):
                                            buffer = self.writeIdentifiedToken(
                                                Token(Acronym.ART.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )
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
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.ART.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q22 = False
                                        self.q2 = False

                                    if self.q221:
                                        buffer = buffer + symbol
                                        if buffer == "--":
                                            buffer = self.writeIdentifiedToken(
                                                Token(Acronym.ART.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )
                                            self.q221 = False
                                            self.q22 = False
                                            self.q2 = False

                                    if self.q222:
                                        buffer = buffer + symbol
                                        if(buffer == "->"):
                                            buffer = self.writeIdentifiedToken(
                                                Token(Acronym.DEL.value, buffer, lineCount),
                                                buffer,
                                                symbol
                                            )
                                            self.q222 = False
                                            self.q22 = False
                                            self.q2 = False

                                if self.q23:
                                    if line[symbolCount+1] == "/" and not self.q232:
                                        self.q231 = True
                                    elif line[symbolCount+1] == "*" and not self.q231:
                                        self.q232 = True
                                    else:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.ART.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
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
                                if not len(line) == symbolCount+1:
                                    if line[symbolCount+1] == "=" and not self.q32 and not self.q31:
                                        self.q31 = True
                                    elif (symbol == "&" or symbol == "|") and not self.q31 and not self.q32:
                                        self.q32 = True
                                    elif not self.q31 and not self.q32:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.LOG.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q3 = False
                                elif not self.q32 and not self.q31:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.LOG.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q3 = False

                                if self.q31:
                                    buffer = buffer + symbol
                                    if buffer == "!=":
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.REL.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q31 = False
                                        self.q3 = False

                                if self.q32:
                                    buffer = buffer + symbol
                                    if buffer == "&&" or buffer == "||":
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.LOG.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q32 = False
                                        self.q3 = False
                            
                            if self.q4:
                                if not len(line) == symbolCount+1 and not self.q41:
                                    if line[symbolCount+1] == "=":
                                        self.q41 = True
                                    else:
                                        buffer = buffer + symbol
                                        buffer = self.writeIdentifiedToken(
                                        Token(Acronym.REL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q4 = False
                                elif not self.q41:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.REL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q4 = False
                                
                                if self.q41:                                  
                                    buffer = buffer + symbol
                                    if buffer == "==":
                                        buffer = self.writeIdentifiedToken(
                                            Token(Acronym.REL.value, buffer, lineCount),
                                            buffer,
                                            symbol
                                        )
                                        self.q41 = False
                                        self.q4 = False

                            if self.q5:
                                if line[symbolCount+1] == "=":
                                    self.q51 = True
                                else:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.REL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q5 = False
                                
                                if self.q51:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.REL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q51 = False
                                    self.q5 = False

                            if self.q6:
                                if line[symbolCount+1] == "=":
                                    self.q61 = True
                                else:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.REL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q6 = False
                                
                                if self.q61:
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.REL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q61 = False
                                    self.q6 = False 

                            if self.q7:
                                if symbol != ' ' and symbol != '\n':
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.DEL.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q7 = False

                                if symbol == ' ':
                                    self.q7 = False

                            if self.q8:
                                if buffer == "":
                                    buffer = buffer + symbol
                                elif buffer.startswith("\"") and symbol == "\"" and buffer != "\"":
                                    buffer = buffer + symbol
                                    buffer = self.writeIdentifiedToken(
                                        Token(Acronym.CAC.value, buffer, lineCount),
                                        buffer,
                                        symbol
                                    )
                                    self.q8 = False

                                elif re.search(cadCaracRegx, symbol) and symbol != "\"":
                                    buffer = buffer + symbol


                        if self.commentLine:
                            if symbol == "\n":
                                self.commentLine = False

                        if self.commentBlock: 
                            buffer = buffer + symbol
                            if buffer.endswith("*/"):
                                self.commentBlock = False
                                
                        symbolCount += 1
                    lineCount += 1
                self.outputFile.close()
                self.inputFile.close()

    def writeIdentifiedToken(self, token: Token, buffer: str, symbol: str):
        self.outputFile.write(token.formatedValue() + "\n")
        return ""

lexicalAnalizer = LexicalAnalizer(PATH_FILES)
lexicalAnalizer.analize()
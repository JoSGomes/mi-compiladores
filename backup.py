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

artList = ["+", "-", "*", "/", "++", "--"]
relList = ["!=", "==", "<", ">", "<=", "=>", "="]
logList = ["!", "&&", "||"]
coList = ["/*", "*/"]

delRegx = r'[\-]|[\,]|[\.]|[\(]|[\)]|[\[]|[\{]|[\}]|[->]|[\]]|[ ]'
digRegx = r'[0-9]'
wordRegx = r'[a-z] | [A-Z]'
cadCaracRegx = r'"'



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

    def analize(self):
        dirs = os.listdir(self.filesPath)
        for dir in dirs:
            if not dir.endswith("_output.txt"):
                inputFile = open(self.filesPath + "/" + dir, "r")
                outputFile = open(self.filesPath + "/" + dir.split(".")[0] + "_output.txt", "w")
                lineCount = 1
                for line in inputFile.readlines():
                    buffer = ""
                    symbolCount = 0
                    isIdentifying = False
                    for symbol in line:
                        if not (re.search(delRegx, buffer)) or (re.search(relList, buffer)) or (re.search(artList, buffer)) or (re.search(logList, buffer)) or (re.search(delRegx, buffer)) or (re.search(coList, buffer)):#o buffer atual é ->, !=, ==, >=, <=, ||, &&, ++, --?
                            if re.search(delRegx, symbol) :#o simbolo é algum delimitador (art, rel, log, del)?
                                    if preList.__contains__(buffer):
                                        token = Token(Acronym.PRE.value, buffer, lineCount)
                                        outputFile.write(token.formatedValue() + "\n")
                                        buffer = "" + symbol
                                        
                                    elif artList.__contains__(buffer):
                                            token = Token(Acronym.ART.value, buffer, lineCount)
                                            outputFile.write(token.formatedValue() + "\n")
                                            buffer = "" + symbol
                                    elif relList.__contains__(buffer):
                                            token = Token(Acronym.REL.value, buffer, lineCount)
                                            outputFile.write(token.formatedValue() + "\n")
                                            buffer = "" + symbol    
                        else:
                            token = Token(Acronym.DEL.value, buffer, lineCount)
                            outputFile.write(token.formatedValue() + "\n")
                            buffer = "" + symbol 

                        
                        buffer = buffer + symbol
                        symbolCount += 1                                     
                    lineCount += 1
                outputFile.close()
                inputFile.close()

lexicalAnalizer = LexicalAnalizer(PATH_FILES)
lexicalAnalizer.analize()
PATH_FILES = "./files"
class SintaxAnalizer(): 
    def __init__(self, tokens: list[str]):
        self.tokens = tokens  
        self.lookahead = tokens[0]
        self.tokensCounter = 1
        self.errors = []
        self.outputFile = None

    def match(self, terminal: str):
        if terminal in self.lookahead:
            self.nextLookahead()
            return True
        else:
            return False
        
    def nextLookahead(self):
        if self.tokensCounter < len(self.tokens):
            self.lookahead = self.tokens[self.tokensCounter]
            self.tokensCounter += 1
        else:
            print("EOF, Arquivo analisado com sucesso!")    

    def saveError(self, expected: str | list, findOut: str):
        self.errors.append("Esperava %s e encontrou na linha %s" % (expected, findOut))
    
    def writeTokensAndErrors(self):
        for token in self.tokens:
            self.outputFile.write(token + "\n")

        if len(self.errors) == 0:
            self.outputFile.write("\n############ Arquivo foi analisado com sucesso! ############")
        else:
            self.outputFile.write("\n############ Erros encontrados ############\n\n")
            for error in self.errors:
                self.outputFile.write(error + "\n")

    def analize(self):
        self.outputFile = open(PATH_FILES + "/sintatico_saida.txt", "w",  buffering=4096, encoding="utf8")

        while self.tokensCounter < len(self.tokens):
            if self.match("const"):
                if not self.match("{"):
                    self.saveError("{", self.lookahead)
                if not self.match("}"):
                    self.saveError("{", self.lookahead)

            elif self.match("variables"):           
                if not self.match("{"):
                    self.saveError("{", self.lookahead)
                if not self.match("}"):
                    self.saveError("{", self.lookahead)

            else:
                self.saveError(["const", "variables"], self.lookahead)
            
        self.writeTokensAndErrors()
        self.outputFile.close()

    
sintaxAnalizer = SintaxAnalizer(["1. <PRE, variables>", "1. <DEL, {>", "1. <DEL, }>"])
sintaxAnalizer.analize()
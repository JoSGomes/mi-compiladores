

class Logger():
    
    def __init__(self, logName):
        self.logFile = open(logName + ".log", 'a+', encoding='utf-8')

    def I(self, message: str) -> None:
        self.logFile.write("INFO: Entrou no método %s\n" % (message))
        
    def closeLogs(self) -> None:
        self.logFile.write("\n############ Final de uma execução ############\n\n")
        self.logFile.close()
    
class Token():
    def __init__(self, name: str, value: str, line: int):
        self.name = name
        self.value = value
        self.line = line


    def formatedValue(self):
        return "%d. <%s, %s>" % (self.line, self.name, self.value)

        
    
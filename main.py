from lexical_analizer import LexicalAnalizer 
from sintax_analizer import SintaxAnalizer

PATH_FILES = "./files"

lexicalAnalizer = LexicalAnalizer(PATH_FILES)
tokensOutputs = lexicalAnalizer.analize()

for tokensOutput in tokensOutputs:
    sintaxAnalizer = SintaxAnalizer(tokensOutput["tokens"], tokensOutput["output"])
    sintaxAnalizer.analize()





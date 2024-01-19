from lexical_analizer import LexicalAnalizer 
from sintax_analizer import SintaxAnalizer
from sintax_semantic_analizer import SintaxSemanticAnalizer

PATH_FILES = "./files"

lexicalAnalizer = LexicalAnalizer(PATH_FILES)
tokensOutputs = lexicalAnalizer.analize()

for tokensOutput in tokensOutputs:
    sintaxAnalizer = SintaxSemanticAnalizer(tokensOutput["tokens"], tokensOutput["output"])
    sintaxAnalizer.analize()





from lexical_analizer import LexicalAnalizer 
from sintax_analizer import SintaxAnalizer

PATH_FILES = "./files"

lexicalAnalizer = LexicalAnalizer(PATH_FILES)
tokens = lexicalAnalizer.analize()

sintaxAnalizer = SintaxAnalizer(tokens)
sintaxAnalizer.analize()





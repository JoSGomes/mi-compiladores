import os 

ROOT_PATH_INPUT_FILES = "./files/input"
ROOT_PATH_OUTPUT_FILES_DIR = "./files/output"

dirs = os.listdir(ROOT_PATH_INPUT_FILES)

for dir in dirs:
    inputFile = open(ROOT_PATH_INPUT_FILES + "/" + dir, "r")
    outputFile = open(ROOT_PATH_OUTPUT_FILES_DIR + "/" + "output_" + dir, "w")
    for line in inputFile.readlines():    
        for symbol in line:
            outputFile.write(symbol + "\n")
    outputFile.close()
    inputFile.close()
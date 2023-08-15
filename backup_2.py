import re

test = "Ã"
cadCaracRegx = re.compile('\w*[\u0020-\u0021]*[\u0023-\u0080]*', re.ASCII)

t = re.search(cadCaracRegx, test)

print(t)
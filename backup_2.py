import re

test = 'a'
cadCaracRegx = re.compile(r'\w*[\u0020-\u0021]*[\u0023-\u0080]*', re.ASCII)

t = re.search(cadCaracRegx, test)
if t.group(0):
    print("hello")
print(t)
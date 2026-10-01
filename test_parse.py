import re

def tokenize(text):
    pattern = r'(\(|\)|[^\s\(\)]+)'
    return [t for t in re.findall(pattern, text)]

def extract_block(tokens, index):
    if index >= len(tokens) or tokens[index] != '(':
        return [], index
    depth = 1
    start = index + 1
    i = start
    while i < len(tokens) and depth > 0:
        if tokens[i] == '(': depth += 1
        elif tokens[i] == ')': depth -= 1
        i += 1
    block_tokens = [tok.replace("\\n", "\n") for tok in tokens[start:i-1]]
    return block_tokens, i

tokens = tokenize("If (label:myif)(cond)(If1 Si (act(A)))")
print(tokens)

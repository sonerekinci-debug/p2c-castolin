import sys
import re

content = open('test_syntax.js', 'r', encoding='utf-8').read()
text = re.sub(r'//.*', '', content)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
text = re.sub(r'"(?:\\.|[^\\"])*"', '""', text)
text = re.sub(r"'(?:\\.|[^\\'])*'", "''", text)
text = re.sub(r'`(?:\\.|[^\\`])*`', '``', text, flags=re.DOTALL)

stack = []
pairs = {'{':'}', '[':']', '(':')'}

for i, c in enumerate(text):
    if c in '{[(': 
        stack.append((c, i))
    elif c in '}])':
        if not stack:
            print(f'Extra {c} at {i}')
            print('CONTEXT:')
            print(content[max(0, i-200):i+200].encode('ascii', 'replace').decode('ascii'))
            break
        top_c, top_i = stack.pop()
        if pairs[top_c] != c:
            print(f'Mismatch: {top_c} at {top_i} closed by {c} at {i}')
            print('CONTEXT:')
            print(content[max(0, i-100):i+100])
            break

if stack:
    print(f'Unclosed {stack[-1][0]} at {stack[-1][1]}')
    idx = stack[-1][1]
    print(content[max(0, idx-100):idx+100])

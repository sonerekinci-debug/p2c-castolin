import re
content = open('p2c_v6.html', 'r', encoding='utf-8').read()
script_content = content.split('<script>')[1].split('</script>')[0]
print('Backtick count:', script_content.count('`'))
text = re.sub(r'//.*', '', script_content)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
text = re.sub(r'".*?"', '""', text)
text = re.sub(r"'.*?'", "''", text)
text = re.sub(r'`.*?`', '``', text, flags=re.DOTALL)
stack = []
pairs = {'{':'}', '[':']', '(':')'}
for i, c in enumerate(text):
    if c in '{[(': stack.append((c, i))
    elif c in '}])':
        if not stack:
            print(f'Extra {c} at {i}')
            break
        top_c, top_i = stack.pop()
        if pairs[top_c] != c:
            print('ERROR CONTEXT:', script_content[i-150:i+150])
            break
if stack:
    print(f'Unclosed {stack[-1][0]} at {stack[-1][1]}')
else:
    print('Brackets OK')

import re

content = open('p2c_v6.html', 'r', encoding='utf-8').read()

def fix_span_fallback(match):
    var_part = match.group(1).strip()
    span_part = match.group(2)
    # Return formatted correctly so it evaluates: t.xxx ? esc(t.xxx) : '<span>...'
    return f"${{{var_part} ? esc({var_part}) : '{span_part}'}}"

content = re.sub(r'\$\{esc\((.*?)\|\|\'(<span.*?>.*?</span>)\'\)\}', fix_span_fallback, content)

open('p2c_v6.html', 'w', encoding='utf-8').write(content)

import sys, os, re

version = sys.argv[1]

if version == 'patch':
    target = 2
elif version == 'minor':
    target = 1
elif version == 'major':
    target = 0
else:
    raise Exception('Invalid version')

pattern = re.compile(r'"version"\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')

def replace_version(match):
    v = list(map(int, match.groups()))
    v[target] += 1
    return '"version": (%d, %d, %d)' % tuple(v)

edit_target_path = os.path.join(os.path.dirname(__file__), '..', '__init__.py')
encoding = "utf-8"

with open(edit_target_path, 'r', encoding=encoding) as reader:
    content = reader.read()

content = pattern.sub(replace_version, content)

with open(edit_target_path, 'w', encoding=encoding) as writer:
    writer.write(content)
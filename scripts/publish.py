import sys, os, re

version = sys.argv[1] if len(sys.argv) > 1 else None

target = -1
if version == 'patch':
    target = 2
elif version == 'minor':
    target = 1
elif version == 'major':
    target = 0

pattern = re.compile(r'"version"\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')

def replace_version(match):
    v = list(map(int, match.groups()))
    v[target] += 1
    return '"version": (%d, %d, %d)' % tuple(v)

def print_version(content):
    match = pattern.search(content)
    if match:
        print('.'.join(match.groups()))

edit_target_path = os.path.join(os.path.dirname(__file__), '..', '__init__.py')
encoding = "utf-8"

with open(edit_target_path, 'r', encoding=encoding, newline='') as reader:
    content = reader.read()

if target != -1:
    content = pattern.sub(replace_version, content)

print_version(content)

with open(edit_target_path, 'w', encoding=encoding, newline='') as writer:
    writer.write(content)
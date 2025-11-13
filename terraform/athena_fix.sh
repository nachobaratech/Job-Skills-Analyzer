python3 << 'PYTHON'
with open('main.tf', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'resource "aws_athena_database"' in line:
        skip = True
        new_lines.append('# Athena database exists - managed manually\n')
        new_lines.append('# ' + line)
        continue
    if skip and line.strip() == '}':
        new_lines.append('# ' + line)
        skip = False
        continue
    if skip:
        new_lines.append('# ' + line)
    else:
        new_lines.append(line)

with open('main.tf', 'w') as f:
    f.writelines(new_lines)
PYTHON

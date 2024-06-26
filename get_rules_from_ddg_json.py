'''
Get rules for ddg json
'''

# <product backlog>

# <sprint #1: />
# <sprint #2: />

# </product backlog>

import os                                                                       # <operating system interfaces />
import re                                                                       # <regular expression operations />
import tqdm                                                                     # <progress bar />
import json                                                                     # <json handling/>

# <settings>

file1_out_name = 'ddg_rules'
path           = './ddg_json'

# </settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Get rules from ddg json                                     \n',
    '# ============================================================\n',
    '# input : url                                                 \n',
    '# output: <ddg_rules> file                                    \n',
    '# ============================================================\n',
)


list1 = os.listdir(path)
list2 = []

for json_file in tqdm.tqdm(list1) :
    list2.append(re.sub(r'\.json$', '', json_file))
    with open(path + '/' + json_file) as json_data :
        json_data = json.load(json_data)
    list2 = list2 + [resources['rule'].replace('\\', '') for resources in json_data['resources']]

list2 = sorted(set(list2))

# <open file1_out file and write header and data>

file1_out = open(file1_out_name, 'w', encoding='UTF-8')

file1_out.write(
      '! ddg rules found in ' + path + '\n'
)

file1_out.writelines(line + '\n' for line in list2)
file1_out.close()

print(
    '\n',
    '{:,}'.format(len(list2)),
    ' lines written to ',
    file1_out_name,
    '\n',
    sep = ''
)

# </open file1_out file and write header and data>

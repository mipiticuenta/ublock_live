'''
Read json from url
'''

# <product backlog>

# <sprint #1: />
# <sprint #2: />

# </product backlog>

import os                                                                       # <operating system interfaces />
import re                                                                       # <regular expression operations />
import requests                                                                 # <get files using url />
import tqdm                                                                     # <progress bar />
import json                                                                     # <json handling/>

# <settings>

file1_out_name = 'ddg_rules'
proxy_servers  = {'https': '', 'http': ''}
proxy_servers_alt  = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}

# </settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Read json from url                                          \n',
    '# ============================================================\n',
    '# input : url                                                 \n',
    '# output: <ddg_rules> file                                    \n',
    '# ============================================================\n',
)

# <test direct connection to internet>

try:
    r = requests.get('https://google.com', timeout = 2, proxies=proxy_servers)
except:
    print('\nUsing alt proxy servers.')
    proxy_servers  = proxy_servers_alt

# </test direct connection to internet>

url = input('Enter url to examine : ')
response = requests.get(url, proxies=proxy_servers)
json_data = json.loads(response.text)

list2 = [resources['rule'].replace('\\', '') for resources in json_data['resources']]
list2 = sorted(set(list2))

# <open file1_out file and write header and data>

file1_out = open(file1_out_name, 'w', encoding='UTF-8')

file1_out.write(
      '! ddg rules found in ' + url + '\n'
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

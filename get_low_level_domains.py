'''
Compile a single deduplicated block list from url sources
'''

# <product backlog>

# <sprint #1: />

# </product backlog>

import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import re                                                                       # <regex capabilities />
import requests                                                                 # <get files using url />
import tqdm                                                                     # <progress bar />

# <settings>

file3_in_name       = 'ipfire_domain_block_list'
file3_out_name      = 'low_level_domain_block_list'
proxy_servers       = {'https': '', 'http': ''}
proxy_servers_alt   = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}

# </settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Get low level domains from ipfire_domain_block_list         \n',
    '# ============================================================\n',
    '# input: <ipfire_domains_block_list> textfile                 \n',
    '# output: <low_level_domain_block_list> textfile              \n',
    '# ============================================================\n',
)

# <test direct connection to internet>

try:
    r = requests.get('https://google.com', timeout = 5, proxies = proxy_servers)
except:
    print('\nUsing alt proxy servers.')
    proxy_servers  = proxy_servers_alt

# </test direct connection to internet>

# <get domains from file, dedup and sort>

list3 = [line.strip() for line in open(file3_in_name, encoding='UTF-8')]        # <populate domain lists />
list3 = [re.sub(r'^ *!.*', '', line) for line in list3]                         # <remove ! comments' />
list3 = sorted([line for line in list3 if line.strip() != ''])                  # <remove empty lines />

# </get domains from file, dedup and sort>

iana_tld = set()

response = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt', proxies=proxy_servers)
if (response.status_code) :
    iana_tld.update(response.text.split('\n'))

iana_tld = [re.sub(r'^#.*', '', line).strip() for line in iana_tld]             # <remove # comments' />
iana_tld = [line.lower() for line in iana_tld if line != '']                    # <remove empty lines />

print('\n IANA top level domains (TLD) list loaded')
print('\n')
print('\n Selecting (@.){2,}tld domains (TLD)')

list3r = []

for tld in tqdm.tqdm(iana_tld):
    pattern = re.compile(r'' + ('^(?:[-_a-z0-9]+\.){2,}' + tld))
    list3r = list3r + [line for line in list3 if pattern.search(line)]

list3r = sorted(set(list3r))

# <open file3r_out file and write header >

file3_out = open(file3_out_name, 'w', encoding='UTF-8')

file3_out.write(
      '! description: @.@.@+ domain filters\n'
    )

# <\open file3_out file and write header />

file3_out.writelines(line + '\n' for line in list3r)
file3_out.close()


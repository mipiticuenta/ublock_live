'''
Check domain list using duck.ai
'''

# <product backlog>

    # <sprint #1: dedup urls/>
    # <sprint #2: apply whitelisting to cosmetic filters/>

# </product backlog>

# <libs & settings>

# from multiprocessing import Pool as ThreadPool                                  # <multithreading function/>
# from multiprocessing import Value                                               # <multithreading function/>
from time import time
import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import pandas as pd
import re                                                                       # <regex capabilities />
import requests                                                                 # <fetch urls />

# file1_in_name   = 'filter_sources'
# file2_out_name  = 'compiled_block_list'
file3_in_name   = 'ipfire_domain_block_list'
# file4_out_name  = 'ipfire_url_block_list'
# file5_out_name  = 'ipfire_regex_block_list'
# file7_out_name  = 'ublock_list_except_domains'
# file8_in_name   = 'domains_white_list'
# file9_in_name   = 'regex_white_list'
# file10_out_name = 'L1_domain_list'
# file11_out_name = 'domain_prefix_list'
# file12_out_name = 'words in long dot separated strings'
no_proxy        = {'https': '', 'http': ''}
local_proxy     = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}
# thr             = os.cpu_count()
t_start         = time()

# </libs & settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Check domain list using duck.ai                             \n',
    '# ============================================================\n',
#     '# input : <filter_sources> textfile                           \n',
#     '# input : <domains_white_list> textfile                       \n',
#     '# input : <regex white list> textfile                         \n',
#     '# output: <compiled_block_list_old> textfile                  \n',
#     '# output: <compiled_block_list> textfile                      \n',
    '# input : <ipfire_domains_block_list> textfile                \n',
#    '# output: <L1_domain_list> textfile                           \n',
#    '# output: <ipfire_urls_block_list> textfile                   \n',
#    '# output: <ipfire_regex_block_list> textfile                  \n',
#    '# output: <ublock_list_except_domains> textfile               \n',
    '# ============================================================\n',
)

# <test direct connection to internet>

proxy_servers = no_proxy                                                          # initialize to direct connection to internet

try:
    r = requests.get(
        'https://google.com',
        timeout = 5,
        proxies = proxy_servers
    )                                                                           # <test direct connection to internet />
except:
    print('Using local proxy\n')
    proxy_servers  = local_proxy                                                # <switch to local proxy />

# </test direct connection to internet>

# < get domain list >

list1 = [line for line in open(file3_in_name, encoding='UTF-8')]

# </ get domain list >

# <populate main list (list2) >

print(
    'reading ',
    len(list1),
    ' domains\n',
    sep = ''
)

line = 'is taboola.com primarily a tracking, advertising, monetisation or engagement subdomain?'
line='Manuela'

def ddg_search(query):
    url = f'https://api.duckduckgo.com/?q={query}&format=json'
    response = requests.get(
        url,
        timeout = 20,
        proxies = proxy_servers
    )
    print(response)
    if response.status_code == 200:
        return response.json()  # Returns the parsed JSON response
    else:
        return None

result = ddg_search(line)
print(result)

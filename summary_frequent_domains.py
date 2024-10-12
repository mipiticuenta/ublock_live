'''
Summary L1 domains frequency in ipfire_domain_block_list
'''

# <product backlog>

    # <sprint #1: />
    # <sprint #2: />

# </product backlog>

# <libs & settings>

from multiprocessing import Pool as ThreadPool                                  # <multithreading function/>
from multiprocessing import Value                                               # <multithreading function/>
from time import time
import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import pandas as pd
import re                                                                       # <regex capabilities />
import requests                                                                 # <fetch urls />

file1_in_name   = 'ipfire_domain_block_list'
file3_out_name  = 'L1_domain_list'
no_proxy        = {'https': '', 'http': ''}
local_proxy     = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}
thr             = os.cpu_count()
t_start         = time()

# </libs & settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Summary L1 domains frequency in ipfire_domain_block_list    \n',
    '# ============================================================\n',
    '# input : <ipfire_domain_block_list> textfile                 \n',
    '# output: <L1_domain_list> textfile                           \n',
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

# <get filter url sources >

list1 = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^ *!.*$', '', line.strip())                            # <remove ! comments />
                for line in open(file1_in_name, encoding='UTF-8')
            ]                                                                   # <populate source lists />
        )                                                                       # <remove empty elements />
    )
)

# </get filter url sources >

# <load iana tld >

iana_tld = set()

try :

    response = requests.get(
        'https://data.iana.org/TLD/tlds-alpha-by-domain.txt',
        timeout = 20,
        proxies = proxy_servers
    )

except :

    print(
        'Error: could not load https://data.iana.org/TLD/tlds-alpha-by-domain.txt',
        flush = True
    )

if response.status_code :
    iana_tld.update(response.text.split('\n'))

iana_tld = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^#.*$', '', line).strip().lower()
                for line in iana_tld
            ]                                                                   # <remove # comments' />
        )
    )
)

iana_sld = iana_tld + [
    (sld + '.' + tld)
    for sld in ['ac' ,'co', 'com', 'edu', 'net', 'org']
    for tld in iana_tld
    if len(tld) == 2
]                                                                               # <frequent slds combined with tlds />

print('IANA top level domains (TLD) list loaded\n')

# </load iana tld >

# <process filter list>

print(
    '{:,}'.format(len(list1)),
    'domains listed\n'
)

# <get L1 domains>

print(
    'reducing domains listed to L1\n'
)

counter = Value('d', 0)
t0 = time()
counter_max = len(list1)

def f_reduce_to_L1(line) :
    global iana_sld
    while re.sub(r'^(?:[^\.]+\.)', '', line) not in iana_sld :
        line = re.sub(r'^(?:[^\.]+\.)', '', line)                               # keep only L1 domain
    counter.value += 1
    print(
        '{:3.0f}'.format((counter.value / counter_max) * 100), '% ',
        '(', '{:.0f}'.format(counter.value), '/', counter_max, ') ',
        '{:.0f}'.format((time() - t0) / 60), '\' elapsed | ',
        '{:.0f}'.format((time() - t0) / counter.value * (counter_max - counter.value) / 60), '\' remaining',
        end = '\r',
        sep = '',
        flush = True
    )
    return line

pool = ThreadPool(thr)                                                       # <make the pool of workers />
list1 = pool.map(f_reduce_to_L1, list1)                                      # <execute function by multi-threading />
pool.close()                                                                 # <close the pool and wait for the work to finish />
pool.join()

print(
    '{:,}'.format(len(list1)),
    'L1_domains listed                                                     \n'
)

df1 = pd.DataFrame()
df1['L1_domain'] = list1
df3 = df1.groupby('L1_domain')['L1_domain'].count()
df3 = df3.sort_values(ascending = False)

# </get L1 domains>

# <write L1 domain list/>

df3.to_csv(file3_out_name, sep='\t')
print(
    'Results saved to textfile <' + file3_out_name + '>\n'
)

# </write L1 domain list>

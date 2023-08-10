''' Compile block list from url sources '''

import os                   # Miscellaneous operating system interfaces
import re                   # Regular expression operations
import progressbar as pb    # Progress bar
import requests             # Get files using url
import time                 # Time functions
import tqdm                 # Progress bar
import math                 # Math functions

# <settings>

file1_in_name  = 'filter_sources'
file2_out_name = 'compiled_block_list'
proxy_servers  = {'https': 'http://fw:8080'}

# <settings>

print(
    '\n',
    '###################################################################################', '\n',
    '#', '\n',
    '# Compile block list from url sources', '\n',
    '#', '\n',
    '# input: <filter_sources> textfile', '\n',
    '# output: <compiled_block_list> textfile, sorted, deduplicated, without empty lines', '\n',
    '#', '\n',
    '###################################################################################', '\n',
    '\n'
    )

# <get filter url sources from file, dedup and sort>

list1 = [line for line in open(file1_in_name, encoding='UTF-8') if line != '']    # <populate from sources/>
list1 = [line                      for line in list1 if line[0] != '!']           # <discard commented lines (leading !)/>
list1 = [re.sub(r'\!.*', '', line) for line in list1]                             # <remove trailing comments'/>
list1 = [line.strip()              for line in list1 if line != '']               # <remove leading/trailing spaces and discard empty lines/>
list1 = sorted(list1)

# </get filter url sources from file, dedup and sort>

# <dump sources to list>

list2 = set()
i        = 1    # <counter for uncommented sources/>

for line in list1 :
    print(
        'reading',
        '{:3.0f}'.format(i),
        '/',
        len(list1),
        'sources listed', ':',
        line
        )
    i += 1
    response = requests.get(line, proxies=proxy_servers)
    if (response.status_code) :
        list2.update(response.text.split('\n'))

print(
    '\n',
    '{:,}'.format(len(list2)),
    'lines gathered from sources',
    '\n'
    )

del(list1)    # <clean up; make sure list1_in is not used anymore hereafter/>

# </dump sources to list>

# <process filter list>

print('Removing unnecessary spaces, lines, comments, etc; applying lower case except for case-sensitive filters')
print('--------------------------------------------------------------------------------------------------------')

print('1.1 : dedup spaces and remove leading/trailing spaces')
list2 = [re.sub(r' +', ' ', line).strip()                      for line in list2]    # <dedup spaces and remove leading/trailing spaces/>

print('1.2 : remove uBO style trailing comments')
list2 = [re.sub(r'!.*', '', line).strip()                      for line in list2]    # <remove uBO style comments'/>

print('1.3 : remove not uBO style trailing comments')
list2 = [re.sub(r'#.*', '', line).strip()                      for line in list2]    # <remove not uBO style trailing comments'/>
list2 = [re.sub(r'^#(?!#).*', '', line)                        for line in list2]    # <remove not uBO style trailing comments'/>

print('1.4 : keep case only for cosmetic filter; apply lower case for the remaining')
# <keep case only for cosmetic filer; lower case for the remaining/>
list2 = [line for line in list2 if re.search(r'#', line)] + [line.lower() for line in list2 if not(re.search(r'#', line))]

print('1.5 : remove items leaded by ****::*')
list2 = [re.sub(r'....\:\:[0-9].*', '', line)                  for line in list2]    # <remove items leaded by '____::_'/>

print('1.6 : remove IP addresses')
list2 = [re.sub(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+.*', '', line) for line in list2]    # <remove IP addresses'/>

print('1.7 : remove www.')
list2 = [re.sub(r'www\.', '', line).strip()                    for line in list2]    # <remove www./>

print('1.8 : remove trailing $all')
list2 = [re.sub(r'\$all$', '', line).strip()                   for line in list2]    # <remove trailing $all/>

print('1.9 : remove trailing $third-party')
list2 = [re.sub(r'\$third-party$', '', line).strip()           for line in list2]    # <remove trailing $third-party/>

print('1.10: remove trailing ^')
list2 = [re.sub(r'\^$', '', line).strip()                      for line in list2]    # <remove trailing ^/>

print('1.11: remove ||')
list2 = [re.sub(r'\|\|', '', line).strip()                     for line in list2]    # <remove ||/>

print('1.12: remove leading 0.0.0.0 ')
list2 = [re.sub(r'0\.0\.0\.0 ', '', line).strip()              for line in list2]    # <remove leading '0.0.0.0 '/>

print('1.13: remove leading 127.0.0.1 ')
list2 = [re.sub(r'127\.0\.0\.1 ', '', line).strip()            for line in list2]    # <remove leading '127.0.0.1 '/>

print('1.14: remove leading ::1 ')
list2 = [re.sub(r'\:\:1 ', '', line).strip()                   for line in list2]    # <remove leading '::1 '/>

print('1.15: remove items with len < 2')
list2 = [line for line in list2 if len(line) > 1]                                     # <remove items with len < 2/>

print('1.16: remove items leaded by localhost')
list2 = [line for line in list2 if line[0:8] != 'localhost']                          # <remove items leaded by localhost />

print(
    '\n',
    '{:,}'.format(len(list2)),
    'lines remaining after 1st pass',
    '\n'
    )

# <extract domains from list>

print('Listing domain filters: ', end = '')

list3 = [line for line in list2 if re.search(r'^[a-z0-9[-_\.a-z0-9]+\.[a-z]+\.[a-z]+(\$important)?$', line) or re.search(r'^[a-z0-9][-_\.a-z0-9]+\.[a-z]+(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]

print(
    '{:,}'.format(len(list3)),
    'domains listed',
    '\n'
    )

# </extract domains from list>

# <remove redundant domains from list>

print('Dedup domains; this operation can take long, please wait')
print('--------------------------------------------------------')

list2 = set(list2) - set(list3)

i_max = math.ceil(math.log(len(list3) / 1e4) / math.log(2))
for i in range(i_max, 0, -1) :
    n = round(len(list3) / (2**i))
    print(
        'recursive size reduccion',
        '{:2.0f}'.format(i_max + 1 - i),
        '/',
        i_max,
        ';',
        '{:,}'.format(len(list3)),
        'domains kept'
        )
    # <filter() + map() option>
    list3 = list(map(lambda line: line if (len(list(filter(lambda substring: substring in line and len(line) > len(substring), list3[:n]))) == 0) else '', tqdm.tqdm(list3)))
    list3 = [line for line in list3 if len(line) > 0]
    # </filter() + map() option>
    
    # <filter() + list comprehension option>
    #list3 = [line for line in list3 if len(list(filter(lambda substring: substring in line and len(line) > len(substring), tqdm.tqdm()list3[:n])))) == 0]
    # </filter() + list comprehension option>

list2 = sorted(set(list2) | set(list3))

print(
    '\n',
    '{:,}'.format(len(list2)),
    'lines remaining after 4th pass',
    '\n'
    )

# </remove redundant domains from list>

# <process filter list>

# <save a backup renamed *_old; overwrite if exists>

filelist = os.listdir('.')

if file2_out_name + '_old' in filelist :
    os.remove(file2_out_name + '_old')

os.rename(file2_out_name, file2_out_name + '_old')

print(
    'backup saved: '
    + file2_out_name
    + '_old'
    + '\n'
)

# </save a backup renamed *_old; overwrite if exists>

# <write output>

file2_out = open(file2_out_name, 'w')
file2_out.writelines(line + '\n' for line in list2)
file2_out.close()

print('Results saved to textfile <' + file2_out_name + '>')
print()

# </write output>


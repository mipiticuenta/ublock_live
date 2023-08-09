""" Compile block list from url sources """

import os                   # Miscellaneous operating system interfaces
import re                   # Regular expression operations
import progressbar as pb    # Progress bar
import requests             # get files using url
import time                 # time functions

# <settings>

file1_in_name  = 'filter_sources'
file2_out_name = "compiled_block_list"
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

list1_out = set()
list1_out = [line for line in open(file1_in_name, encoding='UTF-8') if line != '']    # <populate from sources/>
list1_out = [line                     for line in list1_out if line[0] != '!']        # <discard commented lines (leading !)/>
list1_out = [re.sub('\!.*', '', line) for line in list1_out]                          # <remove trailing comments'/>
list1_out = [line.strip()             for line in list1_out if line != '']            # <remove leading/trailing spaces and discard empty lines/>
list1_out = sorted(list1_out)

print(
    '{:,}'.format(len(list1_out)),
    'sources listed',
    '\n'
    )

# </get filter url sources from file, dedup and sort>

# <dump sources to list>

list2_in = set()
i        = 1    # <counter for uncommented sources/>

for line in list1_out :
    print(
        'reading',
        "{:3.0f}".format(i),
        '/',
        len(list1_out),
        'sources listed', ':',
        line
        )
    i += 1
    response = requests.get(line, proxies=proxy_servers)
    if (response.status_code) :
        list2_in.update(response.text.split('\n'))

print(
    '\n',
    '{:,}'.format(len(list2_in)),
    'lines gathered from sources',
    '\n'
    )

del(list1_out)    # <clean up; make sure list1_in is not used anymore hereafter/>

# </dump sources to list>

# <process filter list>

print('1st pass: removing unnecessary spaces, lines, comments; applying lower case except for case-sensitive filters')


list2_out = sorted(list2_in)

del(list2_in)    # <clean up; make sure list2_in is not used anymore hereafter/>

list2_out = [re.sub(' +', ' ', line).strip()                      for line in list2_out]    # <dedup spaces and remove leading/trailing spaces/>
list2_out = [re.sub('^\:\:1 ', '', line)                          for line in list2_out]    # <remove leading '::1 '/>
list2_out = [re.sub('^....\:\:[0-9].*', '', line)                 for line in list2_out]    # <remove '____::_'/>
list2_out = [re.sub('^127\.0\.0\.1 ', '', line).strip()           for line in list2_out]    # <remove leading '127.0.0.1 '/>
list2_out = [re.sub('^0\.0\.0\.0 ', '', line).strip()             for line in list2_out]    # <remove leading '0.0.0.0 '/>
list2_out = [re.sub('^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', '', line) for line in list2_out]    # <remove IP addresses'/>
list2_out = [re.sub('^!.*', '', line)                             for line in list2_out]    # <remove uBO style comments'/>
list2_out = [re.sub('#.*', '', line).strip()                      for line in list2_out]    # <remove not uBO style trailing comments'/>
list2_out = [re.sub('^#(?!#).*', '', line)                        for line in list2_out]    # <remove not uBO style trailing comments'/>
list2_out = [re.sub('^localhost.*', '', line)                     for line in list2_out]    # <remove leading and trailing spaces/>
list2_out = [re.sub('^www\.', '', line).strip()                   for line in list2_out]    # <remove leading www./>
list2_out = [re.sub('\$all$', '', line).strip()                   for line in list2_out]    # <remove trailing $all/>
list2_out = [re.sub('\$third-party$', '', line).strip()           for line in list2_out]    # <remove trailing $third-party/>
list2_out = [re.sub('\^$', '', line).strip()                      for line in list2_out]    # <remove trailing ^/>
list2_out = [re.sub('^\|\|', '', line).strip()                    for line in list2_out]    # <remove leading ||/>
list2_out = [line for line in list2_out if len(line) > 1]                                   # <discard elements with len <= 1/>

# <keep case only for cosmetic filer; lower case for the remaining/>
list2_out = [line for line in list2_out if re.search(r'#', line)] + [line.lower() for line in list2_out if not(re.search(r'#', line))]

print(
    '\n',
    '{:,}'.format(len(list2_out)),
    'lines remaining after 1st pass',
    '\n'
    )

# <extract domains from list>

print('Listing domain filters: ', end = '')

list3_in = set()
list3_in = [line for line in list2_out if re.search(r'^[a-z0-9[-_\.a-z0-9]+\.[a-z]+\.[a-z]+(\$important)?$', line) or re.search(r'^[a-z0-9][-_\.a-z0-9]+\.[a-z]+(\$important)?$', line)]
list3_in = [re.sub('\$important$', '', line) for line in list3_in]

print(
    '{:,}'.format(len(list3_in)),
    'domains listed',
    '\n'
    )

# </extract domains from list>

# <remove redundant domains from list>

print('2nd pass: listing elemental domains (.@ and .@.@) from ', end = '')

list2_out = set(list2_out) - set(list3_in)
list3_in  = sorted(list3_in, key = lambda x: len(x))    # <sort by increasing length for faster size reduction/>

list3r_in = set()
list3r_in = [line for line in list3_in if re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z]+\.[a-z]+(\$important)?$', line) or re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z]+(\$important)?$', line)]

list3rr_in = set()
list3rr_in = [line for line in list3_in if re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z]+(\$important)?$', line)]

print(
    '{:,}'.format(len(list3r_in)),
    'domains',
    '\n'
    )

i = 1
j = 0
temp  = set(list3r_in) - set(list3rr_in)
temp  = sorted(temp, key = lambda x: -len(x))    # <sort by decreasing length for faster size reduction/>
n     = len(temp)
start = time.time()

while i < n :
    line = temp[i]
    if any(substring in line for substring in list3rr_in) :
        list3r_in.remove(line)    # <reduce size of list3r_in for next iteration/>
        list3_in.remove(line)    # <reduce size of list3_in for next iteration/>
        j += 1
    i += 1
    stop = time.time()
    print(
        "{:6.2f}".format(i / n * 100),
        '% completed,',
        j,
        'domains deduplicated (',
        '{:.1f}'.format(j / i * 100),
        '%) , lap (h) = ',
        '{:.2f}'.format((stop - start) / 3600),
        ', remaining dedup (h) =',
        '{:.2f}'.format((stop - start) / (3600 * i) * (n - i)),
        ', estimated total dur (h) =',
        '{:.2f}'.format((stop - start) / 3600 + (stop - start) / (3600 * i) * (n - i)),
        end = '\r'
        )

print()

print(
    '\n',
    '{:,}'.format(len(list3r_in)),
    'elemental deduplicated domains (.@ and .@.@) listed',
    )

print(
    '\n',
    '{:,}'.format(len(list2_out) + len(list3_in)),
    'lines remaining after 2nd pass',
    )

print('3rd pass: deduplicating using only elemental deduplicated domains')

i = 1
j = 0
temp  = set(list3_in) - set(list3r_in)
temp  = sorted(temp, key = lambda x: -len(x))    # <sort by decreasing length for faster size reduction/>
n     = len(temp)
start = time.time()

while i < n :
    line = temp[i]
    if any(substring in line for substring in list3r_in) :
        list3_in.remove(line)    # <reduce size of list3_in for next iteration/>
        j += 1
    i += 1
    stop = time.time()
    print(
        "{:6.2f}".format(i / n * 100),
        '% completed,',
        j,
        'domains deduplicated (',
        '{:.1f}'.format(j / i * 100),
        '%) , lap (h) = ',
        '{:.2f}'.format((stop - start) / 3600),
        ', remaining dedup (h) =',
        '{:.2f}'.format((stop - start) / (3600 * i) * (n - i)),
        ', estimated total dur (h) =',
        '{:.2f}'.format((stop - start) / 3600 + (stop - start) / (3600 * i) * (n - i)),
        end = '\r'
        )

print()

print(
    '\n',
    '{:,}'.format(len(list2_out) + len(list3_in)),
    'lines remaining after 3rd pass',
    '\n'
    )

print('4th pass: deduplicating domains using all domains')

i = 1
j = 0
temp  = set(list3_in) - set(list3r_in)
temp  = sorted(temp, key = lambda x: -len(x))    # <sort by decreasing length for faster size reduction/>
n     = len(temp)
start = time.time()

while i < n :
    line = temp[i]
    if any(substring in line for substring in list3_in) :
        list3_in.remove(line)    # <reduce size of list3_in for next iteration/>
        j += 1
    i += 1
    stop = time.time()
    print(
        "{:6.2f}".format(i / n * 100),
        '% completed,',
        j,
        'domains deduplicated (',
        '{:.1f}'.format(j / i * 100),
        '%) , lap (h) = ',
        '{:.2f}'.format((stop - start) / 3600),
        ', remaining dedup (h) =',
        '{:.2f}'.format((stop - start) / (3600 * i) * (n - i)),
        ', estimated total dur (h) =',
        '{:.2f}'.format((stop - start) / 3600 + (stop - start) / (3600 * i) * (n - i)),
        end = '\r'
        )

print()

list2_out = sorted(set(list2_out) | set(list3_in))

print(
    '\n',
    '{:,}'.format(len(list2_out)),
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
file2_out.writelines(line + '\n' for line in list2_out)
file2_out.close()

print('Results saved to textfile <' + file2_out_name + '>')
print()

# </write output>


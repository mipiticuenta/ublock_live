''' Compile a single deduplicated lock list from url sources '''

# <product backlog>

# <next sprint: dedup urls/>

# </product backlog>

import os                   # Miscellaneous operating system interfaces
import re                   # Regular expression operations
import requests             # Get files using url
import tqdm                 # Progress bar
import math                 # Math functions

# <settings>

file1_in_name    = 'filter_sources'
file2_out_name   = 'compiled_block_list'
file3r3_out_name = '3words_domain_list'
proxy_servers    = {'https': 'http://fw:8080'}

# </settings>

print(
                                                                      '\n',
    '# ============================================================', '\n',
    '# Compile a single deduplicated block list from url sources',    '\n',
    '# ============================================================', '\n',
    '# input : <filter_sources> textfile',                            '\n',
    '# output: <3words_domain_list> textfile, A-Z by @.@',            '\n',
    '# output: <compiled_block_list> textfile, sorted, deduplicated', '\n',
    '# ============================================================', '\n',
    )

# <get filter url sources from file, dedup and sort>

list1 = [line.strip() for line in open(file1_in_name, encoding='UTF-8')]    # <populate lists from sources/>
list1 = [line.strip()               for line in list1 if line != '']        # <remove leading/trailing spaces and discard empty lines/>
list1 = [line                       for line in list1 if line[0] != '!']    # <discard commented lines (leading !)/>
list1 = [re.sub(r'\ !.*', '', line) for line in list1]                      # <remove trailing comments'/>
list1 = sorted(list1)

# </get filter url sources from file, dedup and sort>

# <dump sources to list>

list2 = set()    # <populating list2 as set type ensures no duplication/>
i     = 1        # <counter for uncommented sources/>

for line in list1 :
    print(
        'reading source',
        '{:3.0f}'.format(i),
        '/',
        len(list1),
        ':',
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

del(list1)    # <clean up; make sure list1 is not used anymore hereafter/>

# </dump sources to list>

# <process filter list>

print('Transforming filters')
print('--------------------')

print(' 1/23 : dedup spaces and remove leading/trailing spaces')
list2 = [re.sub(r' +', ' ', line).strip() for line in list2]                         # <dedup spaces and remove leading/trailing spaces/>

print(' 2/23 : remove uBO style trailing comments')
list2 = [line for line in list2 if len(line) > 1]                                    # <remove items with length < 2/>
list2 = [line for line in list2 if line[0] != '!']                                   # <remove uBO style comments'/>

print(' 3/23 : remove not uBO style trailing comments')
list2 = [line for line in list2 if line[0] != '#']                                   # <remove not uBO style trailing comments/>
list2 = [re.sub(r' #(?!#+).*', '', line) for line in list2]                          # <remove not uBO style trailing comments/>

print(' 4/23 : keep case only for cosmetic filter; apply lower case for the remaining')
list2 = (
        [line         for line in list2 if     re.search(r'#', line) ] + 
        [line.lower() for line in list2 if not(re.search(r'#', line))]               # <lower case for all except cosmetics/>
        )
print(' 5/23 : remove items leaded by ****::*')
list2 = [re.sub(r'....\:\:[0-9].*', '', line) for line in list2]                     # <remove IP6 addresses/>

print(' 6/23 : remove IP addresses (complete or uncomplete)')
list2 = [re.sub(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+.*', '', line) for line in list2]    # <remove IP4 addresses/>
list2 = [re.sub(r'^[0-9]+\.[0-9]+\.[0-9]+\.$', '', line) for line in list2]          # <remove IP4 addresses/>
list2 = [re.sub(r'^[0-9]+\.[0-9]+\..$', '', line) for line in list2]                 # <remove IP4 addresses/>

print(' 7/23 : remove www.')
list2 = [re.sub(r'www\.', '', line).strip() for line in list2]                       # <remove www./>

print(' 8/23 : remove trailing $all')
list2 = [re.sub(r'\$all$', '', line).strip() for line in list2]                      # <remove trailing $all/>

print(' 9/23 : remove trailing $third-party and $3p')
list2 = [re.sub(r'\$third-party$', '', line).strip() for line in list2]              # <remove trailing $third-party/>
list2 = [re.sub(r'\$3p$', '', line).strip() for line in list2]                       # <remove trailing $3p/>

print('10/23 : remove trailing $popup')
list2 = [re.sub(r'(?<=.)\$popup$', '', line).strip() for line in list2]              # <remove trailing $popup/>

print('11/23 : remove trailing ^')
list2 = [re.sub(r'\^$', '', line).strip() for line in list2]                         # <remove trailing ^/>

print('12/23 : remove ||')
list2 = [re.sub(r'\|\|', '', line).strip() for line in list2]                        # <remove ||/>

print('13/23 : remove leading ::1 (dns style filter), :// and :port')
list2 = [re.sub(r'\:\:1 ', '', line).strip() for line in list2]                       # <remove leading '::1 (dns style filter)'/>
list2 = [re.sub(r'^\://', '', line).strip() for line in list2]                        # <remove leading :///>
list2 = [re.sub(r'^\:[0-9]+/', '', line).strip() for line in list2]                   # <remove leading :port/>

print('14/23 : remove leading 0.0.0.0 ')
list2 = [re.sub(r'0\.0\.0\.0 ', '', line).strip() for line in list2]                 # <remove leading '0.0.0.0 (dns style filter)'/>

print('15/23 : remove leading 127.0.0.1 ')
list2 = [re.sub(r'127\.0\.0\.1 ', '', line).strip() for line in list2]               # <remove leading '127.0.0.1 (dns style filter)'/>

print('16/23 : remove items with $badfilter')
list2 = [line for line in list2 if not(re.search(r'[,\$]badfilter', line))]          # <remove items with $badfilter/>

print('17/23 : ensure $csp=all')
list2 = [re.sub(r'.*\$csp=.*', '*$csp=all', line) for line in list2]                 # <ensure *$csp=all'/>

print('18/23 : remove denyallow, popup, popunder, xhr, script, frame filters; keep domains')

list2s = (
    [line for line in list2 if re.search(r'^\*\$.*denyallow.*domain=', line)] +      # <remove denyallow filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$popup.*domain=', line)] +            # <remove popup filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$popunder.*domain=', line)] +         # <remove popunder filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$xhr.*domain=', line)] +              # <remove xhr filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$script.*domain=', line)] +           # <remove script filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$webrtc.*domain=', line)] +           # <remove webrtc filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$image.*domain=', line)] +            # <remove image filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$3p.*domain=', line)] +               # <remove 3p filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\&expire.*domain=', line)] +           # <remove expires filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\&token.*domain=', line)] +            # <remove token filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$ping.*domain=', line)] +             # <remove ping filters and add domains'/>
    [line for line in list2 if re.search(r'^\*\$.*frame.*domain=', line)]            # <remove frame filters and add domains'/>
    )

list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

list2s = [re.sub(r'.*domain=', '', line).strip() for line in list2s]                 # <remove leading .*domain=/>
list2s = [re.sub(r'\,.*$', '', line).strip() for line in list2s]                     # <remove trailing .*,.*/>
list2s = [line.split('|') for line in list2s]                                        # <flatten list2'/>
list2s = [item[0] for line in list2s for item in line]                               # <flatten list2'/>

list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
del(list2s)

print('19/23 : remove items with length < 2')
list2 = [line for line in list2 if len(line) > 1]                                    # <remove items with length < 2/>

print('20/23 : remove items leaded by localhost')
list2 = [line for line in list2 if line[0:8] != 'localhost']                         # <remove items leaded by localhost />

print('21/23 : generalize cosmetic filters (*##)')
list2 = [re.sub(r'^.*(?=##)', '*', line) for line in list2]                          # <generalize cosmetic filters (*##)'/>

print('22/23 : replace trailing .* with .')
list2 = [re.sub(r'\.\*$', '.', line).strip() for line in list2]                      # <replace trailing .* with ./>

print('23/23 : split domains with urls')

list2s = [line for line in list2 if re.search(r'^[-_\.a-z0-9]\.[a-z]/.*', line)]     # <remove domains with url'/>

list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

list22 = (
        [re.sub(r'^[-_\.a-z0-9]+\.[a-z]+/', '/', line) for line in list2s] +         # <isolate url part/>
        [re.sub(r'(?<=\w)/.*', '', line) for line in list2s]                         # <isolate domains part/>
        )

list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
del(list2s)

print(
    '\n',
    '{:,}'.format(len(list2)),
    'lines remaining after 1st pass',
    '\n'
    )

# <extract domains from list>

print('Listing domain filters: ', end = '')

list3 = [line for line in list2 if re.search(r'^[a-z0-9[-_\.a-z0-9]+\.[a-z]+\.[a-z]+(\$important)?$', line) or re.search(r'^[a-z0-9][-_\.a-z0-9]+\.[a-z]+(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]    # <remove trailing $important from domains/>

print(
    '{:,}'.format(len(list3)),
    'found',
    '\n'
    )

# </extract domains from list>

# <remove redundant domains from list>

print('Dedup domains; this operation could take long time, please wait')
print('---------------------------------------------------------------')

list2  = set(list2) - set(list3)    # <only domains part are processed in this section/>
list3r = [line for line in list3 if re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z]+$', line)]    # <@.@ domains are elemental items/>

print(
    '{:,}'.format(len(list3r)),
    'elemental @.@ domains found; excluded from recursive domain downsizing'
    )

list3r3 = [line for line in list3 if re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z0-9][-_a-z0-9]+\.[a-z]+$', line)]    # <@.@.@ domains items/>
list3   = set(list3) - set(list3r) - set(list3r3)    # <elemental domains removed for faster size reduction, and added to final result/>
list3   = sorted(list3, key = lambda x: -len(x))     # <sort by decreasing length for faster size reduction/>

print(
    'recursive domain downsizing',
    '{:2.0f}'.format(1),
    '/',
    '?',
    ';',
    '{:,}'.format(len(list3) + len(list3r3)),
    'domains kept'
    )
list3r3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3r))) == 0) else '', tqdm.tqdm(list3r3)))
list3r3 = [line for line in list3r3 if len(line) > 0]    # <cleanup empty lines/>
list3r  = sorted(set(list3r) | set(list3r3))             # <compile deduplicated domains up to current stage/>

# <write output>

list3r3     = set(list3r3)
list3r3     = sorted(list3r3, key = lambda x: (re.sub(r'^[a-z0-9][-_a-z0-9]+\.', '', x)))    # <sort by a-z @.@/>
file3r3_out = open(file3r3_out_name, 'w')
file3r3_out.writelines(line + '\n' for line in list3r3)
file3r3_out.close()

print(
    'deduplicated 3 words domains (@.@.@) sorted by @.@ saved to textfile <' + file3r3_out_name + '>',
    )

del(list3r3)    # <clean up; make sure list3r3 is not used anymore hereafter/>

# </write output>

i_max = round(math.log((len(list3) + len(list3r)) / 1e5) / math.log(2))
for i in range(i_max, -1, -1) :
    list3_filter = list(set(list3) | set(list3r))
    n = round(len(list3_filter) / (2**i))
    print(
        'recursive domain downsizing',
        '{:2.0f}'.format(i_max + 1 - i + 1),
        '/',
        i_max + 1 + 1,
        ';',
        '{:,}'.format(len(list3)),
        'domains kept'
        )
    # <filter() + map() option>
    list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3_filter[:n]))) == 0) else '', tqdm.tqdm(list3)))
    list3 = [line for line in list3 if len(line) > 0]    # <cleanup empty lines/>
    # </filter() + map() option>
    
    # <filter() + list comprehension option; may worth it a benchmark vs map()?>
    #list3 = [line for line in list3 if len(list(filter(lambda substring: ('.' + substring) in line, tqdm.tqdm(list3_filter[:n])))) == 0]
    # </filter() + list comprehension option>

list2 = sorted(set(list2) | set(list3r) | set(list3))    # <rebuild full list with elemetal domains and shrinked domains part/>

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
    'Backup saved:',
    file2_out_name + '_old',
    '\n'
    )

# </save a backup renamed *_old; overwrite if exists>

# <write output>

file2_out = open(file2_out_name, 'w')
file2_out.writelines(line + '\n' for line in list2)
file2_out.close()

print(
    'Results saved to textfile <' + file2_out_name + '>',
    '\n'
    )

# </write output>


""" Extract domain and url filters from source text file """

# <setup>

import os                   # Miscellaneous operating system interfaces
import re                   # Regular expression operations

file3_out_name = 'ipfire_domain_block_list'
file4_out_name = 'ipfire_url_block_list'
file5_out_name = 'ipfire_regex_block_list'
file7_out_name = 'ublock_list_except_domains'

# <setup/>

print(
                                                                         '\n',
    '# ===============================================================', '\n',
    '# Extract domain and url filters from source text file',            '\n',
    '# ===============================================================', '\n',
    '# input: a text file containing ublock_origin filters',             '\n',
    '# output: text files, sorted, deduplicated, without empty lines:',  '\n',
    '# 1  input file renamed adding _old',                               '\n',
    '# 2  input file written to lower case except filters containing #', '\n',
    '# 3  <ipfire_domains_block_list>',                                  '\n',
    '# 4  <ipfire_urls_block_list>',                                     '\n',
    '# 5  <ipfire_regex_block_list>',                                    '\n',
    '# 7  <ublock_list_except_domains>',                                 '\n',
    '# ===============================================================', '\n',
)

# <get filename containing text lists, dedup and sort >

file1_in_name = input('Please enter filename for source text file : ')
list1 = set(line.strip() for line in open(file1_in_name, encoding='UTF-8'))         # <leading and trailing spaces removed with .strip()/>

list1 = sorted(list1)
list1 = [line for line in list1 if len(line) > 0]                                   # <remove empty elements from list1/>

print(
    '\n',
    '{:,}'.format(len(list1)),
    ' distinct lines read from ',
    file1_in_name,
    ';',
    sep = '',
    end = ''
    )

# <\get filename containing text lists, dedup and sort />

# <save a backup renamed *_old; overwrite if exists >

filelist = os.listdir('.')

if file1_in_name + '_old' in filelist :
    os.remove(file1_in_name + '_old')

os.rename(file1_in_name, file1_in_name + '_old')

print(
    ' backup saved to ',
    file1_in_name,
    '_old',
    '\n',
    sep = ''
)

# </save a backup renamed *_old; overwrite if exists />

# </write domain type filters />

# <save input file written to lower case except cosmetic and regex >

list1 = (
        [line         for line in list1 if     re.search(r'[#\\]', line) ] + 
        [line.lower() for line in list1 if not(re.search(r'[#\\]', line))]          # <lower case for all except cosmetics and regex />
        )

list1 = set(list1)
list1 = sorted(list1)

file1_out_name = file1_in_name
file1_out = open(file1_out_name, 'w', encoding='UTF-8')

file1_out.write(
    '! description: personal filters for uBO; yet under heavy debugging\n' +
    '! expires: 1 day\n' +
    '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/' + file1_out_name + '\n' +
    '! title:' + file1_out_name + '\n' +
    '! #=============================================================================================\n' +
    '!! simple, general filters preferred rather than complicated, specific ones\n' +
    '!! regex only when efficient\n' +
    '!! exceptions only if no better choice\n' +
    '!! #============================================================================================\n' +
    '!!! *$popup,3p avoided (impedes ctrl&click open in another tab)\n' +
    '!!! attribute css selector : ##[]\n' +
    '!!! class css selector     : ##.\n' +
    '!!! id css selector        : ###\n' +
    '!!! #===========================================================================================\n'
)

file1_out.writelines(line + '\n' for line in list1)
file1_out.close()

print(
    '{:,}'.format(len(list1)),
    ' sorted filters written to updated ',
    file1_out_name,
    '\n',
    sep = ''
    )

# </save input file written to lower case except cosmetic and regex >

list1 = [line for line in list1 if line[0] != '!']                                  # <remove uBO style comments from list1 />

# <open file3_out file and write header >

file3_out = open(file3_out_name, 'w', encoding='UTF-8')

file3_out.write(
      '! description: personal domain filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_domain_block_list\n'
    + '! title: domain block list\n'
    )

# <\open file3_out file and write header />

list3 = list1
list3 = [line for line in list3 if re.search(r'^[-_\.a-z0-9]+\.[a-z]+(\.[a-z]+)?(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]                       # <remove trailing $important from domain list/>
list3 = [line for line in list3 if not(re.search(r'.*\.js$', line))]                # <remove .*\.js$ from domain list />
list3 = set(list3)
list3 = sorted(list3, key = lambda x: (re.sub(r'^.*\.(?=[^\.]+\.[^\.]+\Z)', '', x)))    # <sort by a-z @(.@) />
file3_out.writelines(line + '\n' for line in list3)
file3_out.close()

print(
    '{:,}'.format(len(list3)),
    ' domain filters written to '
    + file3_out_name +
    '\n',
    sep = ''
)

# </write domain type filters />

# <write extracted url type filters>

# <open file4_out file and write header>

file4_out = open(file4_out_name, 'w', encoding='UTF-8')

file4_out.write(
      '! description: personal url filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_url_block_list\n'
    + '! title: url block list\n'
)

# <\open file4_out file and write header />

list4 = set(list1) - set(list3)
list4 = [re.sub(r'\$important$', '', line) for line in list4]                       # <remove ''$important'' tag at the end (if present)/>
list4 = [re.sub(r'^\|\|', '', line) for line in list4]                              # <remove ''||'' modifier at the beggining (if present)/>
list4 = [line for line in list4 if re.search(r'^[-_/\.a-z0-9]+$', line)]            # <keep url items/>
list4 = sorted(list4)
file4_out.writelines(line + '\n' for line in list4)
file4_out.close()

print(
    '{:,}'.format(len(list4)),
    ' url filters written to ',
    file4_out_name,
    '\n',
    sep = ''
)

# </write extracted url type filters />

# <write extracted regex type filters>

# <open file5_out file and write header>

file5_out = open(file5_out_name, 'w', encoding='UTF-8')

file5_out.write(
      '! description: personal regex filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_regex_block_list\n'
    + '! title: regex block list\n'
)

# <\open file5_out file and write header />

list5 = list1
list5 = [re.sub(r'\$important$', '', line) for line in list5]                       # <remove ''$important'' tag at the end (if present)/>
list5 = [re.sub(r'^\|\|', '', line) for line in list5]                              # <remove ''||'' modifier at the beggining (if present)/>
list5 = [line for line in list5 if re.search(r'^/.*/$', line)]                      # keep regex items
list5 = sorted(list5)
file5_out.writelines(line + '\n' for line in list5)
file5_out.close()

print(
    '{:,}'.format(len(list5)),
    ' regex filters written to ',
    file5_out_name,
    '\n',
    sep = ''
)

# </write extracted regex type filters />

# <write extracted filters except domains>

# <open file7_out file and write header>

file7_out = open(file7_out_name, 'w', encoding='UTF-8')

file7_out.write(
      '! description: personal filters for ublock_origin (excepting domains)\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ublock_list_except_domains\n'
    + '! title: ublock list except domains\n'
)

# <\open file7_out file and write header />

list7 = set(list1) - set(list3)
list7 = sorted(list7)
file7_out.writelines(line + '\n' for line in list7)
file7_out.close()

print(
    '{:,}'.format(len(list7)),
    ' lines written to ',
    file7_out_name,
    '\n',
    sep = ''
)

# </write extracted filters except domains />


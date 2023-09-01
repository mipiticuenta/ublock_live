""" Extract domain and url filters from source text file """

# <setup>

import os                   # Miscellaneous operating system interfaces
import re                   # Regular expression operations
import progressbar as pb    # Progress bar

file3_out_name = 'ipfire_domain_block_list'
file4_out_name = 'ipfire_url_block_list'
file5_out_name = 'ipfire_regex_block_list'
file7_out_name = 'ublock_list_except_domains'

# <setup/>

print(
                                                                            '\n',
    '# ==================================================================', '\n',
    '# Extract domain and url filters from source text file',               '\n',
    '# ==================================================================', '\n',
    '# input: a text file containing ublock_origin filters',                '\n',
    '# outputs are text files, sorted, deduplicated, without empty lines:', '\n',
    '# 1  input file renamed adding _old',                                  '\n',
    '# 2  input file written to lower case except filters containing #',    '\n',
    '# 3  <ipfire_domains_block_list>',                                     '\n',
    '# 4  <ipfire_urls_block_list>',                                        '\n',
    '# 5  <ipfire_regex_block_list>',                                       '\n',
    '# 7  <ublock_list_except_domains>',                                    '\n',
    '# ==================================================================', '\n',
)

# <get filename containing text lists, convert into list, sort and dedup>

file1_in_name = input('Please enter filename for source text file : ')
list1_in = set(line.strip() for line in open(file1_in_name, encoding='UTF-8'))      # <leading and trailing spaces removed with .strip()/>

list1_in = sorted(list1_in)
list1_in = [line for line in list1_in if len(line) > 0]                             # <remove empty elements from list1_in/>

#for line in list1_in:
#    if len(line) == 0:
#        list1_in.remove(line)    # <remove empty elements from list1_in/>

print(
    '\n',
    '{:,}'.format(len(list1_in)),
    ' lines read from ',
    file1_in_name,
    ';',
    sep = '',
    end = ''
    )

# <\get filename containing text lists, convert into list, sort and dedup>

# <save a backup renamed *_old; overwrite if exists>

filelist = os.listdir('.')

if file1_in_name + '_old' in filelist :
    os.remove(file1_in_name + '_old')

os.rename(file1_in_name, file1_in_name + '_old')

print(
    ' backup saved: ',
    file1_in_name,
    '_old',
    '\n',
    sep = ''
)

# </save a backup renamed *_old; overwrite if exists>

# <save input file written to lower case except cosmetic filters (containing ##)>

file1_out_name = file1_in_name
file1_out = open(file1_out_name, 'w', encoding='UTF-8')
list1_out = set()
list1_out = (
        [line         for line in list1_in if     re.search(r'[#\\]', line) ] + 
        [line.lower() for line in list1_in if not(re.search(r'[#\\]', line))]       # <lower case for all except cosmetics and regex />
        )
list1_out = sorted(list1_out)
file1_out.writelines(line + '\n' for line in list1_out)
file1_out.close()

print(
    '{:,}'.format(len(list1_out)),
    ' sorted filters written to updated ',
    file1_out_name,
    '\n',
    sep = ''
    )

# </save input file written to lower case except cosmetic filters (containing ##)>

list1_in = [line for line in list1_in if line[0] != '!']                            # <remove uBO style comments from list1_in />

# <write extracted L1.root domain type filters>

# <open file3_out file and write header>

file3_out = open(file3_out_name, 'w', encoding='UTF-8')

file3_out.write(
      '! Title: domain block list\n'
    + '! Description: personal domain filters for ipfire and ublock_origin\n'
    + '! Expires: 1 day\n'
    + '! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_domain_block_list\n'
    + '! \n'
    )

# <\open file3_out file and write header>

list3 = [line for line in list1_in if re.search(r'^[-_\.a-z0-9]+\.[a-z]+(\.[a-z]+)?(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]               # <remove trailing $important from domains/>
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

# </write extracted L1.root domain type filters>

# <write extracted url type filters>

# <open file4_out file and write header>

file4_out = open(file4_out_name, 'w', encoding='UTF-8')

file4_out.write(
      '! Title: url block list\n'
    + '! Description: personal url filters for ipfire and ublock_origin\n'
    + '! Expires: 1 day\n'
    + '! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_url_block_list\n'
    + '! \n'
)

# <\open file4_out file and write header>

list4_out = set(list1_in) - set(list3)
list4_out = [re.sub(r'\$important$', '', line) for line in list4_out]               # <remove ''$important'' tag at the end (if present)/>
list4_out = [re.sub(r'^\|\|', '', line) for line in list4_out]                      # <remove ''||'' modifier at the beggining (if present)/>
list4_out = [line for line in list4_out if re.search(r'^[-_/\.a-z0-9]+$', line)]    # <keep url items/>
list4_out = sorted(list4_out)
file4_out.writelines(line + '\n' for line in list4_out)
file4_out.close()

print(
    '{:,}'.format(len(list4_out)),
    ' url filters written to ',
    file4_out_name,
    '\n',
    sep = ''
)

# </write extracted url type filters>

# <write extracted regex type filters>

# <open file5_out file and write header>

file5_out = open(file5_out_name, 'w', encoding='UTF-8')

file5_out.write(
      '! Title: regex block list\n'
    + '! Description: personal regex filters for ipfire and ublock_origin\n'
    + '! Expires: 1 day\n'
    + '! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_regex_block_list\n'
    + '! \n'
)

# <\open file5_out file and write header>

list5_out = list1_in
list5_out = [re.sub(r'\$important$', '', line) for line in list5_out]               # <remove ''$important'' tag at the end (if present)/>
list5_out = [re.sub(r'^\|\|', '', line) for line in list5_out]                      # <remove ''||'' modifier at the beggining (if present)/>
list5_out = [line for line in list5_out if re.search(r'^/.*/$', line)]              # keep regex items
list5_out = sorted(list5_out)
file5_out.writelines(line + '\n' for line in list5_out)
file5_out.close()

print(
    '{:,}'.format(len(list5_out)),
    ' regex filters written to ',
    file5_out_name,
    '\n',
    sep = ''
)

# </write extracted regex type filters>

# <write extracted filters except domains>

# <open file7_out file and write header>

file7_out = open(file7_out_name, 'w', encoding='UTF-8')

file7_out.write(
      '! Title: ublock list except domains\n'
    + '! Description: personal filters for ublock_origin (excepting domains)\n'
    + '! Expires: 1 day\n'
    + '! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ublock_list_except_domains\n'
    + '! \n'
)

# <\open file7_out file and write header>

list7_out = set(list1_in) - set(list3)
list7_out = sorted(list7_out)
file7_out.writelines(line + '\n' for line in list7_out)
file7_out.close()

print(
    '{:,}'.format(len(list7_out)),
    ' lines written to ',
    file7_out_name,
    '\n',
    sep = ''
)

# </write extracted filters except domains>


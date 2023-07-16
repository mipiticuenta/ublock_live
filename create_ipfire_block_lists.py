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
    '\n'
    + '######################################################################\n'
    + '# \n'
    + '# Extract domain and url filters from source text file\n'
    + '#\n'
    + '# input: a text file containing ublock_origin filters\n'
    + '# \n'
    + '# outputs are text files, sorted, deduplicated, without empty lines:\n'
    + '# 1  input file renamed adding _old\n'
    + '# 2  input file written to lower case except filters containing #\n'
    + '# 3  <ipfire_domains_block_list>\n'
    + '# 4  <ipfire_urls_block_list>\n'
    + '# 5  <ipfire_regex_block_list>\n'
    + '# 7  <ublock_list_except_domains>\n'
    + '# \n'
    + '######################################################################\n'
    + '\n'
)

# <get filename containing text lists, convert into list, sort and dedup>

file1_in_name = input('Please enter filename for source text file : ')
list1_in = set(line.strip() for line in open(file1_in_name, encoding='UTF-8'))
list1_in = sorted(list1_in)

print(
    str(len(open(file1_in_name, encoding='UTF-8').readlines()))
    + ' lines read from '
    + file1_in_name
    + '\n'
)

# <\get filename containing text lists, convert into list, sort and dedup>

# <save a backup renamed *_old; overwrite if exists>

filelist = os.listdir('.')

if file1_in_name + '_old' in filelist :
    os.remove(file1_in_name + '_old')

os.rename(file1_in_name, file1_in_name + '_old')

print(
    'backup saved: '
    + file1_in_name
    + '_old'
    + '\n'
)

# </save a backup renamed *_old; overwrite if exists>

# <save input file written to lower case except cosmetic filters (containing ##)>

file1_out_name = file1_in_name
file1_out = open(file1_out_name, 'w', encoding='UTF-8')

print('Building updated input file, please wait')

list1_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()                    # <remove leading and trailing spaces/>
    if len(line) > 0:                      # <remove empty lines/>
        string_r = ''
        if string_r := re.search(r'#', line):
            list1_out.add(line)            # <cosmetics filters are case-sensitive/>
        else :
            list1_out.add(line.lower())    # <transform to lower case/>

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list1_out = sorted(list1_out)

file1_out.writelines(line + '\n' for line in list1_out)
file1_out.close()

print(
    str(len(open(file1_out_name, encoding='UTF-8').readlines()))
    + ' lines written to '
    + file1_out_name +
    '\n'
)

# </save input file written to lower case except cosmetic filters (containing ##)>

## <get filename containing text lists, convert into list, sort and dedup>
#file2_in = input('Please filename for .root library text file2: ')
#list2_in = set(line.strip() for line in open(file2_in, encoding='UTF-8'))
#list2_in = sorted(list2_in)
#print('lines read file2 : ' + str(len(open(file2_in, encoding='UTF-8').readlines())))
#print('\n')
## <\get filename containing text lists, convert into list, sort and dedup>

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

print('Listing domain filters, please wait')

list3_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()
    if len(line) > 0:

        if line[0] != '!':    # <dismiss commented lines/>

            if line[-10:] == '$important':
                line = line[0:-10]    # <remove ''$important'' tag at the end (if present)/>

            # <.root = .@.@ case>
            string_r = ''
            if string_r := re.search(r'\.[a-z|A-Z]+\.[a-z|A-Z]+$', line):
                string_r = string_r.group()
            string_L1_r = ''
            if string_L1_r := re.search(r'^[a-z|A-Z|0-9][a-z|A-Z|0-9|\-|_|\.]+\.[a-z|A-Z]+\.[a-z|A-Z]+$', line):
                string_L1_r = string_L1_r.group()   # L1.root(.@.@)
            # if string_r in list2_in and string_L1_r: list3_out.add(line)    # <forces matching .root in file #2/>
            if string_r and string_L1_r:
                list3_out.add(line)    # <do not apply matching .root in file #2/>
            # </ .root = .@.@ case>

            # <.root = .@ case>
            else:
                string_r = ''
                if string_r := re.search(r'\.[a-z|A-Z]+$', line):
                    string_r = string_r.group()
                string_L1_r = ''
                if string_L1_r := re.search(r'^[a-z|A-Z|0-9][a-z|A-Z|0-9|\-|_|\.]+\.[a-z|A-Z]+$', line):
                    string_L1_r = string_L1_r.group()   # L1.root(.@.@)
                # if string_r in list2_in and string_L1_r: list3_out.add(line)    # <forces matching .root in file #2/>
                if string_r and string_L1_r:
                    list3_out.add(line)    # <do not apply matching .root in file #2/>
            # </ .root = .@ case>

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list3_out = sorted(list3_out)
file3_out.writelines(line + '\n' for line in list3_out)
file3_out.close()

print(
    str(len(open(file3_out_name, encoding='UTF-8').readlines()))
    + ' lines written to '
    + file3_out_name +
    '\n'
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

print('Listing url filters, please wait')

list4_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()
    if len(line) > 0:

        if line[0] != '!' and line[0] != '|':    # <dismiss commented lines/>

            string_r = ''
            if line[-10:] == '$important':
                line = line[0:-10]    # <remove ''$important'' tag at the end (if present)/>
            if line[0:2] == '||':
                line = line[2:]    # <remove ''||'' modifier at the beggining (if present)/>
            if string_r := re.search(r'^[a-z|A-Z|\.|\-|_|\/]+$', line):
                string_r = string_r.group()
            if string_r and string_r not in list3_out:
                list4_out.add(line)

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list4_out = sorted(list4_out)
file4_out.writelines(line + '\n' for line in list4_out)
file4_out.close()

print(
    str(len(open(file4_out_name, encoding='UTF-8').readlines()))
    + ' lines written to '
    + file4_out_name
    + '\n'
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

print('Listing regex filters, please wait')

list5_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()
    if len(line) > 0:

        if line[0] != '!' and line[0] != '|':    # <dismiss commented lines/>

            string_r = ''
            if line[-10:] == '$important':
                line = line[0:-10]    # <remove ''$important'' tag at the end (if present)/>
            if line[0:2] == '||':
                line = line[2:]    # <remove ''||'' modifier at the beggining (if present)/>
            if string_r := re.search(r'^/.*/$', line):
                string_r = string_r.group()[1:-1]
                list5_out.add(string_r)

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list5_out = sorted(list5_out)
file5_out.writelines(line + '\n' for line in list5_out)
file5_out.close()

print(
    str(len(open(file5_out_name, encoding='UTF-8').readlines()))
    + ' lines written to '
    + file5_out_name
    + '\n'
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

print('Listing all filters except domain type, please wait')

list7_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()
    if len(line) > 0:

        if line[0] != '!':    # <dismiss commented lines/>

            if line not in list3_out:
                list7_out.add(line)

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list7_out = sorted(list7_out)
file7_out.writelines(line + '\n' for line in list7_out)
file7_out.close()

print(
    str(len(open(file7_out_name, encoding='UTF-8').readlines()))
    + ' lines written to '
    + file7_out_name
    + '\n'
)

# </write extracted filters except domains>


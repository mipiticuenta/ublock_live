##########################################################################################
#
# Extract L1.root domains from source text file and '.root' library text file
#
# input: 2 textfiles
# output: 'ipfire_domains_block_list'
# output: 'ipfire_urls_block_list'
#
# outputs are text files, sorted, deduplicated, without empty lines
#
##########################################################################################

import re                   # Regular expression operations
import progressbar as pb    # Progress bar

# <settings>
file3_out_name = 'ipfire_domains_block_list'
file4_out_name = 'ipfire_urls_block_list'
# <settings>

print('\n')
print('==================================================================================')
print('Extract L1.root domains and urls from source text file and .root library text file')
print('==================================================================================')
print('\n')

# <get filename containing text lists, convert into list, sort and dedup>
file1_in = input('Please filename for source text file1: ')
list1_in = set(line.strip() for line in open(file1_in, encoding='Latin1'))
list1_in = sorted(list1_in)
print('lines read file1 : ' + str(len(open(file1_in, encoding='Latin1').readlines())))
print('\n')
# <get filename containing text lists, convert into list, sort and dedup>

# <get filename containing text lists, convert into list, sort and dedup>
file2_in = input('Please filename for .root library text file2: ')
list2_in = set(line.strip() for line in open(file2_in, encoding='Latin1'))
list2_in = sorted(list2_in)
print('lines read file2 : ' + str(len(open(file2_in, encoding='Latin1').readlines())))
print('\n')
# <get filename containing text lists, convert into list, sort and dedup>

# <open file3_out file and write header>
file3_out = open(file3_out_name, 'w', encoding='Latin1')
file3_out.write('! Title: Unified block list\n')
file3_out.write('! Description: personal filters for uBlock\n')
file3_out.write('! Expires: 1 day\n')
file3_out.write('! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/unified_block_list\n')
file3_out.write('!\n')
# <open file3_out file and write header>

# <open file4_out file and write header>
file4_out = open(file4_out_name, 'w', encoding='Latin1')
file4_out.write('! Title: Unified block list\n')
file4_out.write('! Description: personal filters for uBlock\n')
file4_out.write('! Expires: 1 day\n')
file4_out.write('! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/unified_block_list\n')
file4_out.write('!\n')
# <open file4_out file and write header>

# <write extracted L1.root elements>

print('Listing L1.root found; please wait')

list3_out = set()

for line in list1_in:

    # <.root = .@.@ case>
    string_r = re.search(r'\.[a-z|A-Z]+\.[a-z|A-Z]+$', line)
    if string_r:
        string_r = string_r.group()
        string_L1_r = re.search(r'^[a-z|A-Z|0-9|\-|_]+\.[a-z|A-Z]+\.[a-z|A-Z]+$', line)   # L1.root(.@.@)
        if string_r in list2_in and string_L1_r:
            list3_out.add(line)            
    # <.root = .@.@ case>

    # <.root = .@ case>
    else:
        string_r = re.search(r'\.[a-z|A-Z]+$', line)
        if string_r:
            string_r = string_r.group()
            string_L1_r = re.search(r'^[a-z|A-Z|0-9|\-|_]+\.[a-z|A-Z]+$', line)   # L1.root(.@)
            if string_r in list2_in and string_L1_r:
                list3_out.add(line)
    # <.root = .@ case>        

list3_out = sorted(list3_out)
file3_out.writelines(line + '\n' for line in list3_out)
file3_out.close()
print('lines written    : ' + str(len(open(file3_out_name, encoding='Latin1').readlines())))
print('\n')

print('Listing urls found; please wait')

list4_out = set()
progress = pb.ProgressBar(maxval = len(list1_in)).start()
progvar = 0

for line in list1_in:

    string_r = re.search(r'^[a-z|A-Z|\.|\-|_|\/]+$', line)
    if string_r:
        string_r = string_r.group()
        if string_r not in list3_out:
            list4_out.add(line) 
    progress.update(progvar + 1)
    progvar += 1

print('\n')

list4_out = sorted(list4_out)
file4_out.writelines(line + '\n' for line in list4_out)
file4_out.close()
print('lines written    : ' + str(len(open(file4_out_name, encoding='Latin1').readlines())))
print('\n')

# <compare list and write common elements>

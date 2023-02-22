#######################################################################################
#
# Extract urls from source text file
#
# output: 'ipfire_urls_block_list' text file, sorted, deduplicated, without empty lines
#
#######################################################################################

import re       # Regular expression operations

# <settings>
file3_out_name = "ipfire_urls_block_list"
# <settings>

print('\n')
print('=========================================================================')
print('Extract urls from source text file')
print('=========================================================================')
print('\n')

# <get filename containing text lists, convert into list, sort and dedup>
file1_in = input('Please filename for source text file1: ')
list1_in = set(line.strip() for line in open(file1_in, encoding='Latin1'))
list1_in = sorted(list1_in)
print('lines read file1 : ' + str(len(open(file1_in, encoding='Latin1').readlines())))
# <get filename containing text lists, convert into list, sort and dedup>

# <open file3_out file and write header>
file3_out = open(file3_out_name, 'w', encoding='Latin1')
file3_out.write('! Title: Unified block list\n')
file3_out.write('! Description: personal filters for uBlock\n')
file3_out.write('! Expires: 1 day\n')
file3_out.write('! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/unified_block_list\n')
file3_out.write('!\n')

# <open file3_out file and write header>

# <write extracted url elements>
print('Listing urls found; please wait')
list3_out = set()
for line in list1_in:

    string_r = re.search(r'^[a-z|A-Z|\.|\-|_|\/]+$', line)
    if string_r:
        list3_out.add(line)            

list3_out = sorted(list3_out)
file3_out.writelines(line + '\n' for line in list3_out)
file3_out.close()
print('lines written    : ' + str(len(open('file3_out', encoding='Latin1').readlines())))
print('\n')
# <compare list and write common elements>

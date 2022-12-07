###############################################################################
#
# Clean text file
#
#   Sort, deduplicate and remove empty lines
#
###############################################################################

import os

# <get filename containing text list to be sorted, deduplicated and saved>
file1 = input('please filename for textfile: ')
# <get filename containing text list to be sorted, deduplicated and saved>

# <convert text file into list>
list1_in = set(line.strip() for line in open(file1, encoding='Latin1'))
print('lines read   : ' + str(len(list1_in)))
# <convert text file into list>

# <save a backup, renamed *_old>
os.rename(file1, file1 + '_old')
# <save a backup, renamed *_old>

# <sort list>
list1_in = sorted(list1_in)
# <sort list>

# <deduplicate list, remove empty lines and save to a file with the same name>
list1_out = set()
output = open(file1, 'w', encoding='Latin1')
for line in list1_in:
    if line not in list1_out and len(line) >0:
            list1_out.add(line)
            output.write(line)
            output.write('\n')
output.close()
# print('lines written: ' + str(len(list1_out)))
# <deduplicate list, remove empty lines and save to a file with the same name>

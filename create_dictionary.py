import re                   # Regular expression operations
import progressbar as pb    # Progress bar

# <settings>

    file3_out_name = "clean_block_list"

# <settings>

print('###############################################################################')
print('#')
print('# Clean block_list textfile')
print('#')
print('# input: 2 textfiles')
print('# output: 'L1.root' text file, sorted, deduplicated, without empty lines')
print('#')
print('###############################################################################')

print('')

# <get filename containing text lists, convert into list, sort and dedup>

    file1_in = input('Please filename for source text file1: ')
    list1_in = set(line.strip() for line in open(file1_in, encoding='Latin1'))
    list1_in = sorted(list1_in)
    print(len(list1_in), 'lines read')

# <get filename containing text lists, convert into list, sort and dedup>

# <get filename containing text lists, convert into list, sort and dedup>

    # file2_in = input('Please filename for .root library text file2: ')
    # list2_in = set(line.strip() for line in open(file2_in, encoding='Latin1'))
    # list2_in = sorted(list2_in)
    # print('lines read file2 : ' + str(len(open(file2_in, encoding='Latin1').readlines())))

# <get filename containing text lists, convert into list, sort and dedup>

# <open file3_out file and write header>

    file3_out = open(file3_out_name, 'w', encoding='Latin1')
    # file3_out.write('! Clean block_list')
    # file3_out.write('\n')

# <open file3_out file and write header>

list3_out = set()

print('1st pass: remove unnecessary spaces and empty lines')
for line in list1_in:
    line = line.strip()                         # remove leading and trailing spaces
    line = re.sub('[ ]+', ' ', line)            # remove repated spaces
while('' in list1_in): list1_in.remove('')      # remove empty lines

print('done!')
print('')

print('2nd pass: send comments, url, cosmetic, exceptions, regex to output')
for line in list1_in:
    if line[0] == '!': 
        list3_out.add(line)                     # comment => output file
    elif line.find('/') >= 0:
        list3_out.add(line)                     # url => output file
    elif line.find('#') >= 0:
        list3_out.add(line)                     # cosmetic => output file
    elif line.find('@') >= 0:
        list3_out.add(line)                     # exception => output file
    elif line.find('\\') >= 0:
        list3_out.add(line)                     # regex => output file
print(len(list3_out), 'lines sent')
print('')

# <remove items send to output>

    list1_in_temp = [i for i in list1_in if i not in list3_out]
    list1_in = list1_in_temp

# <remove items send to output>

# <find and write redundant L2+.domain elements>

    print('3rd pass: clean redundant L2+.domain elements')
    progress = pb.ProgressBar(maxval = len(list1_in)).start()
    progvar = 0

    for line in list1_in:
        string_r = re.search(r'[a-z|A-Z|0-9|\-|_]+\.[a-z|A-Z]+$', line)  # L1.root
        if string_r:
            string_r = string_r.group()
            if string_r in list1_in and string_r != line:
                list3_out.add('! ' + line)      # line is redundant; write as a comment
            else:
                list3_out.add(line)
        else:
            list3_out.add(line)
        progress.update(progvar + 1)
        progvar += 1
    print('')

    print('done!')
    print('')

    list3_out = sorted(list3_out)
    file3_out.writelines(line + '\n' for line in list3_out)
    file3_out.close()

    print(len(list3_out), 'lines written')
    print('Find results in textfile <' + file3_out_name + '>')
    print('\n')

# <find and write redundant L2+.domain elements>

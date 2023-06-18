print('\n')
print('##########################################################################################')
print('#')
print('# Extract L1.root domains and url filters from source text file')
print('#')
print('# input: a text file containing ublock_origin filters')
print('#')
print('# outputs are text files, sorted, deduplicated, without empty lines:')
print('# 1  <ipfire_domains_block_list>')
print('# 2  <ipfire_urls_block_list>')
print('# 3  <ublock_list_except_domains>')
print('#')
print('##########################################################################################')
print('\n')

# <setup/>
import re                   # Regular expression operations
import progressbar as pb    # Progress bar

file3_out_name = 'ipfire_domain_block_list'
file4_out_name = 'ipfire_url_block_list'
file5_out_name = 'ublock_list_except_domains'
# <setup/>

# <get filename containing text lists, convert into list, sort and dedup>
file1_in = input('Please filename for source text file : ')
list1_in = set(line.strip() for line in open(file1_in, encoding='Latin1'))
list1_in = sorted(list1_in)
print(str(len(open(file1_in, encoding='Latin1').readlines())) + 'lines read from ' + file1_in + '\n')
# <\get filename containing text lists, convert into list, sort and dedup>

## <get filename containing text lists, convert into list, sort and dedup>
#file2_in = input('Please filename for .root library text file2: ')
#list2_in = set(line.strip() for line in open(file2_in, encoding='Latin1'))
#list2_in = sorted(list2_in)
#print('lines read file2 : ' + str(len(open(file2_in, encoding='Latin1').readlines())))
#print('\n')
## <\get filename containing text lists, convert into list, sort and dedup>

# <write extracted L1.root domain type filters>

# <open file3_out file and write header>
file3_out = open(file3_out_name, 'w', encoding='Latin1')
file3_out.write('! Title: domain block list\n')
file3_out.write('! Description: personal domain filters for ipfire and ublock_origin\n')
file3_out.write('! Expires: 1 day\n')
file3_out.write('! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_domain_block_list\n')
file3_out.write('\n')
# <\open file3_out file and write header>

print('Listing domain filters, please wait')

list3_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()
    if len(line) > 0:

        if line[0] != '!':    # <dismiss commented lines/>

            if line[-10:] == '$important': line = line[0:-10]    # <remove ''$important'' tag at the end (if present)/>

            # <.root = .@.@ case>
            string_r = ''
            if string_r := re.search(r'\.[a-z|A-Z]+\.[a-z|A-Z]+$', line): string_r = string_r.group()
            string_L1_r = ''
            if string_L1_r := re.search(r'^[a-z|A-Z|0-9][a-z|A-Z|0-9|\-|_|\.]+\.[a-z|A-Z]+\.[a-z|A-Z]+$', line): string_L1_r = string_L1_r.group()   # L1.root(.@.@)
            # if string_r in list2_in and string_L1_r: list3_out.add(line)    # <forces matching .root in file #2/>
            if string_r and string_L1_r: list3_out.add(line)    # <do not apply matching .root in file #2/>
            # </ .root = .@.@ case>

            # <.root = .@ case>
            else:
                string_r = ''
                if string_r := re.search(r'\.[a-z|A-Z]+$', line): string_r = string_r.group()
                string_L1_r = ''
                if string_L1_r := re.search(r'^[a-z|A-Z|0-9][a-z|A-Z|0-9|\-|_|\.]+\.[a-z|A-Z]+$', line): string_L1_r = string_L1_r.group()   # L1.root(.@.@)
                # if string_r in list2_in and string_L1_r: list3_out.add(line)    # <forces matching .root in file #2/>
                if string_r and string_L1_r: list3_out.add(line)    # <do not apply matching .root in file #2/>
            # </ .root = .@ case>

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list3_out = sorted(list3_out)
file3_out.writelines(line + '\n' for line in list3_out)
file3_out.close()
print(str(len(open(file3_out_name, encoding='Latin1').readlines())) + ' lines written to ' + file3_out_name + '\n')

# </write extracted L1.root domain type filters>

# <write extracted url type filters>

# <open file4_out file and write header>
file4_out = open(file4_out_name, 'w', encoding='Latin1')
file4_out.write('! Title: url block list\n')
file4_out.write('! Description: personal url filters for ipfire and ublock_origin\n')
file4_out.write('! Expires: 1 day\n')
file4_out.write('! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_url_block_list\n')
file4_out.write('\n')
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
            if line[-10:] == '$important': line = line[0:-10]    # <remove ''$important'' tag at the end (if present)/>
            if line[0:2] == '||': line = line[2:]    # <remove ''||'' modifier at the beggining (if present)/>
            if string_r := re.search(r'^[a-z|A-Z|\.|\-|_|\/]+$', line): string_r = string_r.group()
            if string_r and string_r not in list3_out: list4_out.add(line)

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list4_out = sorted(list4_out)
file4_out.writelines(line + '\n' for line in list4_out)
file4_out.close()
print(str(len(open(file4_out_name, encoding='Latin1').readlines())) + ' lines written to ' + file4_out_name + '\n')

# </write extracted url type filters>

# <write extracted filters except domains>

# <open file5_out file and write header>
file5_out = open(file5_out_name, 'w', encoding='Latin1')
file5_out.write('! Title: ublock list except domains\n')
file5_out.write('! Description: personal filters for ublock_origin (excepting domains)\n')
file5_out.write('! Expires: 1 day\n')
file5_out.write('! Homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ublock_list_except_domains\n')
file5_out.write('!\n')
# <\open file5_out file and write header>

print('Listing all filters except domain type, please wait')

list5_out = set()
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0

for line in list1_in:

    line = line.strip()
    if len(line) > 0:

        if line not in list3_out: list5_out.add(line)

    progress += 1
    pbar.update(progress)

pbar.finish()
print('\n')

list5_out = sorted(list5_out)
file5_out.writelines(line + '\n' for line in list5_out)
file5_out.close()
print(str(len(open(file5_out_name, encoding='Latin1').readlines())) + ' lines written to ' + file5_out_name + '\n')

# </write extracted filters except domains>

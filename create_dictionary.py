""" Create a dictionary from textfile """

# <settings>

import re                   # Regular expression operations
import pandas as pd
import numpy as np
import progressbar as pb    # Progress bar

file3_out_name = "dictionary"

# </settings>

print('###############################################################################')
print('#')
print('# Create a dictionary from textfile')
print('#')
print('# output: text file, sorted, with duplicates')
print('#')
print('###############################################################################')

print('')

# <get filename containing text lists, convert into list, sort and dedup>

file1_in = input('Please filename for source text file1: ')
list1_in = set(line.strip() for line in open(file1_in, encoding='Latin1'))
list1_in = sorted(list1_in)
print(len(list1_in), 'lines read')

# </get filename containing text lists, convert into list, sort and dedup>

# <open file3_out file and write header>

file3_out = open(file3_out_name, 'w', encoding='Latin1')
    # file3_out.write('! Clean block_list')
    # file3_out.write('\n')

# </open file3_out file and write header>

list3_out = []

# <create dictionary>

print('creating dictionary')
pbar = pb.ProgressBar(maxval = len(list1_in)).start()
progress = 0


for line in list1_in:
    line = re.split(r"[^a-z,^A-Z]+", line)
    for word in line: list3_out.append(word)
    progress += 1
    pbar.update(progress)
print('\n')

pbar.finish()
print(
    '\n'
    + 'done!'
    + '\n'
)

list3_out_pd = pd.DataFrame(list3_out)
list3_out_pd.columns = ['word']
list3_out_pd = pd.crosstab(index=list3_out_pd['word'], columns='freq')
list3_out_pd.to_csv(file3_out_name)

file3_out.close()

print(len(list3_out_pd), 'lines written')
print('Find results in textfile <' + file3_out_name + '>')
print('\n')

# </create dictionary>

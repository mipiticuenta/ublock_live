'''
Find most common text in a list block list from url source
'''

# <product backlog>

    # <sprint #1: dedup urls/>
    # <sprint #2: apply whitelisting to cosmetic filters/>

# </product backlog>

# <libs & settings>

from Levenshtein import distance                # <Levenshtein distance/>                                
from multiprocessing import Pool as ThreadPool  # <multithreading function/>
from multiprocessing import Value               # <multithreading function/>
from time import time
import math                                     # <math functions />
import numpy as np
import os                                       # <operating system interfaces />
import pandas as pd
import re                                       # <regex capabilities />

file1_in_name   = 'compiled_block_list'
file2_out_name  = 'word_frequency'
thr             = os.cpu_count()
t_start         = time()

pd.options.mode.chained_assignment = None       # <prevent SettingWithCopyWarning message from appearing />


# </libs & settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Find most common text in a list block list                  \n',
    '# ============================================================\n',
    '# input : <compiled_block_list> textfile                      \n',
    '# output: <most_common_text_list> textfile                    \n',
    '# ============================================================\n',
)

# <get words list >

list1 = list(
    filter(
        None,
        [
            re.sub(r'^[!\*].*$', '', line).strip()
            for line in open(file1_in_name, encoding='UTF-8')
        ]                                                                   # <populate filters />
    )                                                                       # <remove empty elements />
)

def f_split(line) :
    line = re.sub(r'[_\W]+', ',', line)                                     # <split each word>
    line = line.split(',')
    return line

pool = ThreadPool(thr)                                                      # <make the pool of workers />
list1 = pool.map(f_split, list1)                                            # <execute function by multithreading />
pool.close()                                                                # <close the pool and wait for the work to finish />
pool.join()

list1 = [
    line if (type(line) == str)                                             # <prevents word atomization into chars if word type />
    else item
    for line in list1
    for item in line
]                                                                           # <flatten list />

list1 = [word for word in list1 if len(word) > 3]                           # <discard short words />

print(
    '{:,}'.format(len(list1)),
    'words gathered\n'
)

# </get words list >

# <process filter list>

print(
    '--------------------\n',
    'finding distances   \n',
    '--------------------\n',
    sep = ''
)

dist_df = pd.DataFrame()
dist_df['word'] = list(filter(None, sorted(set(list1))))                    # <df deduplication />

print(
    '{:,}'.format(dist_df..shape[0]),
    'unique words gathered\n'
)

# <write main output>

file2_out = dist_df.to_csv(file2_out_name, index = False)
print(
    'words saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>

dist_df['sum_dist'] = dist_df['word'].apply(lambda x: sum([distance(word, x) for word in list1]))
dist_df = dist_df.sort_values(by = ['sum_dist'], ascending = False)

# <write main output>

file2_out = dist_df.to_csv(file2_out_name, index = False)
print(
    'words saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>
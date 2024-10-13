'''
Find most common text in a list block list from url source
'''

# <product backlog>

    # <sprint #1: dedup urls/>
    # <sprint #2: apply whitelisting to cosmetic filters/>

# </product backlog>

# <libs & settings>

from functools import reduce
from Levenshtein import distance                # <Levenshtein distance/>                                
from multiprocessing import Pool as ThreadPool  # <multithreading function/>
from multiprocessing import Value               # <multithreading function/>
from progress.bar import ChargingBar
from time import time
import math                                     # <math functions />
import numpy as np
import os                                       # <operating system interfaces />
import pandas as pd
import re                                       # <regex capabilities />

file1_in_name   = 'compiled_block_list'
file2_out_name  = 'word_freq'
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

print(
    'listing words\n'
)

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

# def sum_dist(word) :
#     global list1
#     sum_distance = reduce(lambda word, word1: sum([--(word1 == word)]), list1)
#     return sum_distance

# def w_in_w(word) :
#     global list1
#     sum_distance = reduce(lambda word, word1: sum([--(word in [word1])]), list1)
#     return w_in_w

# dist_df = pd.DataFrame()
# dist_df['word'] = list1
# dist_df = dist_df.groupby('word')['word'].aggregate(['count', w_in_w])
# dist_df = dist_df.sort_values(by = ['sw_in_w'], ascending = False)

metrics_df = pd.DataFrame()

list1c = list(set(list1))

print(
    '{:,}'.format(len(list1c)),
    'unique words gathered\n'
)

metrics_df['word'] = list1c

bar = ChargingBar('Loading...')
count_match = np.array([sum([--(x == y) for y in list1]) for x in list1c if not bar.next()])
bar.finish()

# count_match = np.array([--(x == y) for x in list1c for y in list1])
print('count_match completed\n')
count_match = count_match.reshape(len(list1c), len(list1))
print('reshape completed\n')
count_match = np.sum(count_match, axis = 1)
print('sum completed\n')
count_match = count_match.tolist()
print('tolist completed\n')
metrics_df['count'] = count_match
del(count_match)

# <write main output>

file2_out = distmetrics_df_df.to_csv(file2_out_name)
print(
    'words saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>

lv_dist = np.array([distance(x,y) for x in list1c for y in list1]).reshape(len(list1c), len(list1))
metrics_df['sum_dist'] = np.sum(lv_dist , axis = 1).tolist()
del(lv_dist)

# <write main output>

file2_out = distmetrics_df_df.to_csv(file2_out_name)
print(
    'words saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>
'''
Find most common text in a list block list from url source
'''

# <product backlog>

    # <sprint #1: dedup urls/>
    # <sprint #2: apply whitelisting to cosmetic filters/>

# </product backlog>

# <libs & settings>

from functools import reduce
from Levenshtein import distance                                                # <Levenshtein distance/>
from multiprocessing import Pool as ThreadPool                                  # <multithreading function/>
from multiprocessing import Value                                               # <multithreading function/>
from time import time
import math                                                                     # <math functions />
import numpy as np
import os                                                                       # <operating system interfaces />
import pandas as pd
import re                                                                       # <regex capabilities />

file1_in_name   = 'compiled_block_list'
file2_out_name  = 'word_freq'
thr             = os.cpu_count()
t_start         = time()
pd.options.mode.chained_assignment = None                                       # <prevent SettingWithCopyWarning message from appearing />

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
        ]                                                                       # <populate filters />
    )                                                                           # <remove empty elements />
)

def f_split(line) :
    line = re.sub(r'[_\W]+', ',', line)                                         # <split each word>
    line = line.split(',')
    return line


pool = ThreadPool(thr)                                                          # <make the pool of workers />
list1 = pool.map(f_split, list1)                                                # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list1 = [
    line if (type(line) == str)                                                 # <prevents word atomization into chars if word type />
    else item
    for line in list1
    for item in line
]                                                                               # <flatten list />

list1 = [word for word in list1 if len(word) > 3]                               # <discard short words />

print(
    '{:,}'.format(len(list1)),
    'words gathered\n'
)

# </get words list >

# <process filter list>

metrics_df = pd.DataFrame()
metrics_df['word'] = list1
metrics_df = metrics_df.groupby('word')['word'].aggregate(['count']).reset_index()
metrics_df = metrics_df.sort_values('count', ascending = False)

# <write main output>

file2_out = metrics_df.to_csv(file2_out_name, index = False)
print(
    '{:,}'.format(metrics_df.shape[0]),
    'unique words saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>

print(
    'finding distances\n',
)

counter = Value('d', 0)
t0 = time()
counter_max = metrics_df.shape[0]

def f_dist(word) :
    global list1
    # w_dist = sum([distance(word, y) for y in list1])                          # <using list comprenhension/>
    w_dist = np.sum([distance(word,y) for y in list1], axis = 0)                # <using numpy + list comprehension/>
    counter.value += 1
    print(
        '        ',
        '{:3.0f}'.format((counter.value / counter_max) * 100), '% ',
        '(', '{:.0f}'.format(counter.value), '/', counter_max, ') ',
        '{:.0f}'.format((time() - t0) / 60), '\' elapsed | ',
        '{:.0f}'.format((time() - t0) / counter.value * (counter_max - counter.value) / 60), '\' remaining',
        end = '\r',
        sep = '',
        flush = True
    )
    return w_dist

pool = ThreadPool(thr)                                                          # <make the pool of workers />
s_dist = pool.map(f_dist, list(metrics_df['word']))                             # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

metrics_df['sum_dist'] = s_dist
metrics_df = metrics_df.sort_values('sum_dist', ascending = True)
del(s_dist)

# <write main output>

file2_out = metrics_df_df.to_csv(file2_out_name)
print(
    'words saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>

# def w_in_w(word) :
#     global list1
#     sum_distance = reduce(lambda word, word1: sum([--(word in [word1])]), list1)
#     return w_in_w


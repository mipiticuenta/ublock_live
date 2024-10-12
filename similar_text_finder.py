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
file2_out_name  = 'most_common_text_list'
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

# <get filter list >

list1 = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^.*[^\w\.\-].*$', '', line.strip())                    # <remove filters with any symbol except \.\-\_ />
                for line in open(file1_in_name, encoding='UTF-8')
            ]                                                                   # <populate source lists />
        )                                                                       # <remove empty elements />
    )
)

# </get filter list >

# <populate list >

list1 = list(filter(None, sorted(set(list1))))                                  # <remove empty elements />

print(
    '\n',
    '{:,}'.format(len(list1)),
    'unique filters gathered'
)

# </populate list >

# <process filter list>

print(
    '--------------------\n',
    'finding distances   \n',
    '--------------------\n',
    sep = ''
)

def f_dist(series) :
        return reduce(lambda x, y:dist(x, y), series)

dist_df = pd.DataFrame()
dist_df['filter'] = list1
dist_df = dist_df.groupby('filter').agg(f_dist)

dist_df = dist_df.sort_values(by = ['sum_dist'], ascending = True)

file2_out = dist_df.to_csv(file2_out_name, index = False)

file2_out.close()

print(
    'Results saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>
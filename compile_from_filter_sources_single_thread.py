'''
Compile a single deduplicated block list from url sources
'''

# <product backlog>

    # <sprint #2: dedup urls/>
    # <sprint #3: apply multicore/>
    # <sprint #4: apply whitelisting to cosmetic filters/>
    # <sprint #5: check for mismatching () [] {} />

# </product backlog>

# <libs & settings>

import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import re                                                                       # <regex capabilities />
import requests                                                                 # <fetch urls />
import tqdm                                                                     # <progress bar />
from multiprocessing import Pool as ThreadPool                                  # <multithreading function/>

file1_in_name  = 'filter_sources'
file2_out_name = 'compiled_block_list'
file3_out_name = 'ipfire_domain_block_list'
file4_out_name = 'ipfire_url_block_list'
file5_out_name = 'ipfire_regex_block_list'
file7_out_name = 'ublock_list_except_domains'
file8_in_name  = 'domains_white_list'
file9_in_name  = 'regex_white_list'
no_proxy       = {'https': '', 'http': ''}
local_proxy    = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}

# </ libs & settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# Compile a single deduplicated block list from url sources   \n',
    '# ============================================================\n',
    '# input : <filter_sources> textfile                           \n',
    '# input : <domains_white_list> textfile                       \n',
    '# input : <regex white list> textfile                         \n',
    '# output: <compiled_block_list_old> textfile                  \n',
    '# output: <compiled_block_list> textfile                      \n',
    '# output: <ipfire_domains_block_list> textfile                \n',
    '# output: <ipfire_urls_block_list> textfile                   \n',
    '# output: <ipfire_regex_block_list> textfile                  \n',
    '# output: <ublock_list_except_domains> textfile               \n',
    '# ============================================================\n',
)

# <test direct connection to internet>

proxy_servers = no_proxy                                                          # initialize to direct connection to internet

try:
    r = requests.get(
        'https://google.com',
        timeout = 5,
        proxies = proxy_servers
    )                                                                           # <test direct connection to internet />
except:
    print('Using local proxy\n')
    proxy_servers  = local_proxy                                                # <switch to local proxy />

# </test direct connection to internet>

# <get filter url sources, dedup and sort>

list1 = sorted(
    list(
        filter(
            None, 
            [
                re.sub(r'^ *!.*', '', line.strip())                             # <remove ! comments />
                for line in open(file1_in_name, encoding='UTF-8')
            ]                                                                   # <populate source lists />
        )                                                                       # <remove empty elements />
    )
)

# </get filter url sources, dedup and sort>

# <dump sources to list>

list2 = set()                                                                   # <set() type ensures deduplication />
list5 = []                                                                      # <intialize list5 (regex) />
i     = 1                                                                       # <counter for uncommented sources />

for line in list1 :
    print(
        'reading source',
        '{:3.0f}'.format(i),
        '/',
        len(list1),
        ':',
        line
    )
    i += 1
    response = requests.get(
        line,
        proxies = proxy_servers
    )
    if (response.status_code) :
        list2.update(response.text.split('\n'))
        print(
            '                         ',
            '{:,}'.format(len(list2)),
            'cumulated filters'
        )

# </dump sources to list>

# <load iana tld >

iana_tld = set()

response = requests.get(
    'https://data.iana.org/TLD/tlds-alpha-by-domain.txt',
    proxies = proxy_servers
)

if (response.status_code) :
    iana_tld.update(response.text.split('\n'))

iana_tld = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^#.*', '', line).strip().lower()
                for line in iana_tld
            ]                                                                   # <remove # comments' />
        )
    )
)

iana_sld = iana_tld + [
    (sld + '.' + tld)
    for sld in ['ac' ,'co', 'com', 'edu', 'net', 'org']
    for tld in iana_tld
    if len(tld) == 2
]                                                                               # <frequent slds combined with tlds />

print('\nIANA top level domains (TLD) list loaded')

# </load iana tld >

# <process filter list>

print(
                        '\n',
    '--------------------\n',
    'Transforming filters\n',
    '--------------------\n',
    sep = ''
)

# <transforming loop>

print(' 1/21 : remove leading/trailing/dup spaces ')

list2 = [
    re.sub(r'\t', ' ', line)
    for line in list2
]                                                                               # <replace tab with space  />

list2 = [
    re.sub(r' +', ' ', line).strip()
    for line in list2
]                                                                               # <dedup spaces and remove leading/trailing spaces />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 2/21 : remove comments ')

list2 = [re.sub(r'^ *[!\[\{].*', '', line)
    for line in list2
]                                                                               # <remove !comment [comment] {comment} />

list2 = [re.sub(r'^ *#(?![\?\@\#]).*', '', line)
    for line in list2
]                                                                               # <remove #comment; preserve cosmetics and exceptions />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 3/21 : clean dns/domain filters ')

list2 = [re.sub(r'^0\.0\.0\.0 ', '', line)
    for line in list2
]                                                                               # <remove leading 0.0.0.0 (dns style filter) />

list2 = [re.sub(r'^127\.0\.0\.1 ', '', line)
    for line in list2
]                                                                               # <remove leading 127.0.0.1 (dns style filter) />

list2 = [re.sub(r'^\:+1 ', '', line)
    for line in list2
]                                                                               # <remove leading ::1 (dns style filter) />

list2 = [
    re.sub(r'[\|\^]', '', line) if re.search(r'^\|{1, 2}[-\.\w]+\^$', line)
    else line
    for line in list2
]                                                                               # <remove || ^ from abp syntax ||domain^ />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 4/21 : remove items containing % about: $badfilter localhost; remove http: IP4 IP6 :port/; clean from=, path=, replace=, transform=')

list2 = [
    line
    for line in list2
    if not(re.search(r'\%', line))
]                                                                               # <remove items comprising % >

list2 = [
    line
    for line in list2
    if not(re.search(r'about\:', line))
]                                                                               # <remove items comprising about: >

list2 = [
    line
    for line in list2
    if not(re.search(r'[,\$]badfilter', line))
]                                                                               # <remove items comprising $badfilter />

list2 = [
    line
    for line in list2
    if not(re.search(r'localhost', line))
]                                                                               # <remove items containing localhost />

list2 = [
    re.sub(r'^[^a-z]+$', '', line)
    for line in list2
]                                                                               # <remove filters comprised only by simbols and numbers (includes IP4 addresses) />

list2 = [
    line for line in list2
    if not(re.search(r'\:\:', line))
]                                                                               # <remove IP6 addresses :: />

list2 = [
    re.sub(r'^\:[0-9]+/', '/', line)
    for line in list2
]                                                                               # <replace leading :port/ with / />

list2 = [
    re.sub(r'https?\:/*', '', line)
    for line in list2
]                                                                               # <remove http:/* />

list2 = [
    re.sub(r'[\|\^]', '', line) if re.search(r'^\|{1, 2}[-\.\w]+\^.*$', line)
    else line
    for line in list2
]                                                                               # <remove || ^ from abp syntax ||domain^ />

list2 = [
    re.sub(r',?from=.*$', '', line)
    for line in list2
]                                                                               # <remove (,)from=.* />

list2 = [
    re.sub(r',?path=.*$', '', line)
    for line in list2
]                                                                               # <remove (,)path=.* />

list2 = [
    re.sub(r',?replace=.*$', '', line)
    for line in list2
]                                                                               # <remove (,)replace=.* />

list2 = [
    re.sub(r',?transform=.*$', '', line)
    for line in list2
]                                                                               # <remove (,)transform=.* />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 5/21 : apply lower case except for cosmetics and regex')

list2 = [
    line if re.search(r'[#\\]', line)
    else line.lower()
    for line in list2
]                                                                               # <apply lower case except cosmetics and regex />

list2 = list(filter(None, list2))                                               # <remove empty elements />

# <segregate regex filters >

list2 = [
    re.sub(r'^/([-\.\+\~\!\=/\w]+)/$', r'/\1/*', line)
    for line in list2
]                                                                               # <add trailing * for /@/ url filters (false regex) />

list2 = [
    line
    for line in list2
    if not(re.search(r'^/.*\\/$', line))
]                                                                               # <remove broken regex (bad termination) />

list5 = [
    line
    for line in list2
    if re.search(r'^/.+/(?:\$important)?$', line)
]                                                                               # <populate regex filters/>

list5 = [
    line
    for line in list5
    if not(re.search(r'^/.*[\^\?]\*.*/$', line))                                # <remove wrong regex filters/>
]

list5 = [
    line
    for line in list5
    if not(re.search(r'^/.*\/\$.*/$', line))                                    # <remove wrong regex filters/>
]

list2  = set(list2) - set(list5)

# </segregate regex filters >

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 6/21 : generalize cosmetic filters (*##) and exceptions (*#@ *#? *@@) ')

list2 = [
    re.sub(r'^.*(?=\#[\#\?])', '*', line)
    for line in list2
]                                                                               # <generalize *## *#? />

list2 = [
    re.sub(r'^.*(?=[\#\@]\@)', '*', line)
    for line in list2
]                                                                               # <generalize *#@ *@@ />

list2 = [
    re.sub(r'^.*removeparam\=', '*$removeparam=', line)
    for line in list2
]                                                                               # <generalize *$removeparam />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 7/21 : remove cosmetic filters (## #?) and exceptions (@@ #@) except *##:')

list2 = [
    re.sub(r'^\*?\#\#(?!\:).*', '', line)
    for line in list2
]                                                                               # <remove cosmetic filters except ##: />

list2 = [
    re.sub(r'^\*?\#[\@|\?].*', '', line)
    for line in list2
]                                                                               # <remove #@ #? exceptions />

list2 = [
    re.sub(r'^\*?\@\@.*', '', line)
    for line in list2
]                                                                               # <remove @@ exceptions />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 8/21 : split urls with $ domain= ')

list2s = [
    line
    for line in list2
    if re.search(r'\$.*domain=', line)
]                                                                               # <get urls with $ domain= '/>

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = (
    [
        re.sub(r',.*', '', re.sub(r'^.*domain=', '', line))
        for line in list2s
    ] +                                                                         # <isolate domain list part/>
    [
        re.sub(r'\$.*', '', line)
        for line in list2s
    ]                                                                           # <isolate url part/>
)

list2s = [
    line.split('|')
    for line in list2s
]                                                                               # <flatten list'/>

list2s = [
    item
    for line in list2s
    for item in line
    if line !=[''] and item != ''
]                                                                               # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>

list2 = list(filter(None, list2))                                               # <remove empty elements />

del(list2s)

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print(' 9/21 : remove domain= denyallow= and keep the related domains')

list2s = [
    line
    for line in list2
    if re.search(r'.*(domain|denyallow)=', line)
]                                                                               # <select *$ filters />

list2 = set(list2) - set(list2s)                                                # <segregate selected filters'/>

list2s = [
    re.sub(r'.*domain=', '', line).strip()
    for line in list2s
]                                                                               # <remove leading .*domain=/>

list2s = [
    re.sub(r'.*denyallow=', '', line).strip()
    for line in list2s
]                                                                               # <remove leading .*denyallow=/>

list2s = [
    re.sub(r',.*$', '', line).strip()
    for line in list2s
]                                                                               # <remove trailing .*,.*/>

list2s = [
    line.split('|')
    for line in list2s
    if len(line) > 0
]                                                                               # <flatten list'/>

list2s = [
    item
    for line in list2s
    for item in line
    if line !=[''] and item != ''
]                                                                               # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>

list2 = list(filter(None, list2))                                               # <remove empty elements />

del(list2s)

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print('10/21 : split , separated domains ')

list2   = [
    re.sub(r'^,', '', line).strip()
    for line in list2
]                                                                               # <remove leading , />

list2   = [
    re.sub(r',$', '', line).strip()
    for line in list2
    ]                                                                           # <remove trailing , />

list2s = [
    line
    for line in list2
    if re.search(r'\,', line)
]                                                                               # <remove , separated domains />

list2s = [
    line
    for line in list2s
    if not(re.search(r'[\$\&]', line))
]                                                                               # <exclude $ & filters />

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = [
    line.split(',')
    for line in list2s
]

list2s = [
    item
    for line in list2s
    for item in line
    if line !=[''] and item != ''
]                                                                               # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>

list2 = list(filter(None, list2))                                               # <remove empty elements />

del(list2s)

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

n_1 = len(list2) + 1
i   = 0

while n_1 > len(list2):                                                         # <recursive loops up to no further length reduction for list2 />

    i   = i + 1
    n_1 = len(list2)

    print(
        'loop ', i, '\n',
        '-------',
        sep = ''
    )

    print('11/21 : clean up leading symbols numbers prefix etc')

    list2 = [
        re.sub(r'www[0-9]*\.', '', line)
        for line in list2
    ]                                                                           # <remove www#. />

    list2 = [
        re.sub(r'^[_\W0-9]*(?=[/\.\$])', '', line)
        for line in list2
    ]                                                                           # <remove leading symbols and numbers preceding / . $ />

    list2 = [
        re.sub(r'^[/\.]?\w(?=[/\.\$])', '', line)
        for line in list2
    ]                                                                           # <remove leading single a-z0-9 char preceding / . $ />

    list2 = [
        re.sub(r'^\.(?=\*)', '', line)
        for line in list2
    ]                                                                           # <remove leading . if followed by * />

    list2 = [re.sub(
        r'^\W*(?=\$)', '*', line)
        for line in list2
    ]                                                                           # <replace symbol/none replace leading $ /$ .$ =$ ?$ with *$ />

    list2 = [
        re.sub(r'^\.?[-\*\w]+/', '/', line)
        for line in list2
    ]                                                                           # <replace leading (.)@/ with / />

    list2 = [
        re.sub(r'^/\*.*[^/]', '', line)
        for line in list2
    ]                                                                           # <remove leading /* except for regex filters />

    list2 = [
        re.sub(r'^\*(?=[^\$\#])', '', line)
        for line in list2
    ]                                                                           # <remove leading /* except for regex filters />

    list2 = [
        re.sub(r'^/([-\.\+\!\~/\w]+)/$', r'/\1/*', line)
        for line in list2
    ]                                                                           # <add trailing * for /@/ url filters (false regex) />

    list2 = list(filter(None, list2))                                           # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list5)),
        'filters kept'
    )

    print('12/21 : clean up trailing symbols numbers suffix $filters etc')

    list2 = [
        re.sub(r'[\^\|\=]\$', '$', line).strip()
        for line in list2
    ]                                                                           # <replace ^$ |$ =$ with $ />

    list2 = [
        re.sub(r'\|+\$', '$', line).strip()
        for line in list2
    ]                                                                           # <replace |$ with $ />

    list2 = [
        re.sub(r'[#,\~\|\^\?\=\&]+$', '', line).strip()
        for line in list2
    ]                                                                           # <remove trailing # , ~ | ^ ? = & />

    list2 = [
        re.sub(r'(?<!/)\*$', '', line).strip()
        for line in list2
    ]                                                                           # <remove trailing * except /url/* />

    list2 = [
        re.sub(r'\.\*$', '.', line).strip()
        for line in list2
    ]                                                                           # <replace trailing .* with . />

    list2 = [
        re.sub(r'\*\.$', '', line).strip()
        for line in list2
    ]                                                                           # <remove trailing *. />

    list2 = [
        re.sub(r'\.cgi\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .cgi? />

    list2 = [
        re.sub(r'\.ashx\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .ashx? />

    list2 = [
        re.sub(r'\.asp\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .asp? />

    list2 = [
        re.sub(r'\.?html?\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .html? />

    list2 = [
        re.sub(r'\.jpe?g\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .jp(e)g? />

    list2 = [
        re.sub(r'\.php\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .php? />

    list2 = [
        re.sub(r'\.png\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .png? />

    list2 = [
        re.sub(r'\.svg\??$', '.', line)
        for line in list2
    ]                                                                           # <remove trailing .svg? />

    list2 = [
        re.sub(r'\.js\??[^\./]*$', '.js', line)
        for line in list2
    ]                                                                           # <clean up trailing .js />

    list2 = [
        re.sub(r'^([-\w]+)=.*$', r'\1', line)
        for line in list2
    ]                                                                           # <remove trailing .=.* />

    list2 = [
        re.sub(r'(^[^#]{2,})\$[-~,=a-z0-9]*$(?<!/)(?<!important)', r'\1', line)
        for line in list2
    ]                                                                           # <remove specific trailing $ filters except *$ or ending with important />

    list2 = [
        re.sub(r'\??\*\=.*$', '', line).strip()
        for line in list2
    ]                                                                           # <remove trailing ?*=... />

    list2 = list(filter(None, list2))                                           # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list5)),
        'filters kept'
    )

    print('13/21 : split domain and url ')

    list2s = [
        line
        for line in list2
        if re.search(r'^[-\.\w]+\.[a-z]+/.*', line)
    ]                                                                           # <get domains with url'/>

    list2 = set(list2) - set(list2s)                                            # <segregate removed filters'/>

    list2s = (
        [
            re.sub(r'^[-\.\w]+/', '/', line)
            for line in list2s
        ] +                                                                     # <isolate url part/>
        [
            re.sub(r'/.*$', '', line)
            for line in list2s
        ]                                                                       # <isolate domains part/>
    )

    list2 = sorted(set(list2) | set(list2s))                                    # <join retrieved domains to main list'/>
    
    list2 = [
        re.sub(r'^/([-\.\+\~\!/\w]+)/$', r'/\1/*', line)
        for line in list2
    ]                                                                           # <add trailing * for /@/ url filters (false regex) />
    
    list2 = list(filter(None, list2))                                           # <remove empty elements />

    del(list2s)

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list5)),
        'filters kept'
    )

    print('14/21 : clean up urls')

    list2 = [
        re.sub(r'\*+', '*', line).strip()
        for line in list2
    ]                                                                           # <dedup * />

    list2 = [
        re.sub(r'\.+', '.', line).strip()
        for line in list2
    ]                                                                           # <dedup . />

    list2 = [
        re.sub(r'/+', '/', line).strip()
        for line in list2
    ]                                                                           # <dedup / />

    list2 = [
        re.sub(r'^.*/\*/', '/', line)
        for line in list2
    ]                                                                           # <replace any url preceded by /*/ (included) with / />

    list2 = [
        re.sub(r'([-\./\w]+)\$(?!important)[-\,\=\.\w]*$', r'\1', line)
        for line in list2
    ]                                                                           # <remove $* tail except for *$ />

    list2 = list(filter(None, list2))                                           # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list5)),
        'filters kept'
    )

# <transforming loop/>

print('15/21 : split space separated domains ')

list2s = [
    line
    for line in list2
    if re.search(r' ', line) and not(re.search(r'[\$\@\#]', line))
]                                                                               # <remove space separated domains />

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = [
    line.split(' ')
    for line in list2s
]                                                                               # <flatten list'/>

list2s = [
    item
    for line in list2s
    for item in line
    if line !=[''] and item != ''
]                                                                               # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>

list2 = list(filter(None, list2))                                               # <remove empty elements />

del(list2s)

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print('16/21 : remove lines leaded by ! # + & ? ^ : ; @ and @.exe @.gif @.rar @.zip')

list2 = [
    re.sub(r'^\*?\^.*', '', line)
    for line in list2
]                                                                               # <remove ^ leaded lines />

list2 = [
    re.sub(r'^\|+', '', line)
    for line in list2
]                                                                               # <remove leading | />

list2 = [
    re.sub(r'^\!.*', '', line)
    for line in list2
]                                                                               # <remove ! leaded lines />

list2 = [
    re.sub(r'^#.*', '', line)
    for line in list2
]                                                                               # <remove # leaded lines />

list2 = [
    re.sub(r'^[/\*]?\+.*', '', line)
    for line in list2
]                                                                               # <remove + leaded lines />

list2 = [
    re.sub(r'^\*?\&.*', '', line)
    for line in list2
]                                                                               # <remove & leaded lines />

list2 = [
    re.sub(r'^\*?\?.*', '', line)
    for line in list2
]                                                                               # <remove ? leaded lines />

list2 = [
    re.sub(r'^\*?\:.*', '', line)
    for line in list2
]                                                                               # <remove : leaded lines />

list2 = [
    re.sub(r'^\*?\;.*', '', line)
    for line in list2
]                                                                               # <remove ; leaded lines />

list2 = [
    re.sub(r'^\*?\".*', '', line)
    for line in list2
]                                                                               # <remove " leaded lines />

list2 = [
    re.sub(r'^[/\*]?\@.*', '', line)
    for line in list2
]                                                                               # <remove @ leaded lines />

list2 = [
    re.sub(r'^.*\.gif$', '.gif', line)
    for line in list2
]                                                                               # <enforce .gif filter />

list2 = [
    re.sub(r'^.*\.rar$', '', line)
    for line in list2
]                                                                               # <remove @.rar filters />

list2 = [
    re.sub(r'^.*\.zip$', '', line)
    for line in list2
]                                                                               # <remove @.zip filters />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print('17/21 : arrange *$ filters; keep beacon csp inline-font inline-script object other ping popunder script websocket xhr ')

list2 = [
    re.sub(r'^\*\$\~?1p.*', '', line)
    for line in list2
]                                                                               # <remove *$1p />

list2 = [
    re.sub(r'^\*\$\~?3p.*', '', line)
    for line in list2
]                                                                               # <remove *$3p />

list2 = [
    re.sub(r'^\*\$\~?third\-party.*', '', line)
    for line in list2
]                                                                               # <remove *$3p />

list2 = [
    re.sub(r'^\*\$\~?all.*', '', line)
    for line in list2
]                                                                               # <remove *$all />

list2 = [
    re.sub(r'^\*\$\~?beacon.*', '*$beacon', line)
    for line in list2
]                                                                               # <enforce *$beacon />

list2 = [
    re.sub(r'.*\$csp.*', '*$csp=all', line)
    for line in list2
]                                                                               # <enforce *$csp=all />

list2 = [
    re.sub(r'^\*\$\~?css.*', '', line)
    for line in list2
]                                                                               # <remove *$css />

list2 = [
    re.sub(r'^\*\$\~?stylesheet.*', '', line)
    for line in list2
]                                                                               # <remove *$css />

list2 = [
    re.sub(r'^\*\$\~?(sub)?doc(ument)?.*', '', line)
    for line in list2
]                                                                               # <remove *$(sub)doc />

list2 = [
    re.sub(r'^\*\$\~?from.*', '', line)
    for line in list2
]                                                                               # <remove *$from />

list2 = [
    re.sub(r'^\*\$\~?image.*', '', line)
    for line in list2
]                                                                               # <remove *$image />

list2 = [
    re.sub(r'^\*\$\~?inline\-font.*', '*$inline-font', line)
    for line in list2
]                                                                               # <enforce *$inline-font />

list2 = [
    re.sub(r'^\*\$\~?inline\-script.*', '*$inline-script', line)
    for line in list2
]                                                                               # <enforce *$inline-script />

list2 = [
    re.sub(r'^\*\$\~?media.*', '', line)
    for line in list2
]                                                                               # <remove *$media />

list2 = [
    re.sub(r'^\*\$\~?object.*', '*$object', line)
    for line in list2
]                                                                               # <enforce *$object />

list2 = [
    re.sub(r'^\*\$\~?other.*', '*$other', line)
    for line in list2
]                                                                               # <enforce *$other />

list2 = [
    re.sub(r'^\*\$\~?ping.*', '*$ping', line)
    for line in list2
]                                                                               # <enforce *$ping />

list2 = [
    re.sub(r'^\*\$\~?popup.*', '', line)
    for line in list2
]                                                                               # <remove *$popup />

list2 = [
    re.sub(r'^\*\$\~?popunder.*', '*$popunder', line)
    for line in list2
]                                                                               # <enforce *$popunder />

list2 = [re.sub(
    r'^(.*)\$\~?script.*', r'\1', line)
    for line in list2
]                                                                               # <remove *$script />

list2 = [
    re.sub(r'^\*\$\~?rewrite.*', '', line)
    for line in list2
]                                                                               # <remove *$rewrite />

list2 = [
    re.sub(r'^\*\$\~?websocket.*', '*$websocket', line)
    for line in list2
]                                                                               # <enforce *$websocket />

list2 = [
    re.sub(r'^\*\$\~?xhr.*', '*$xhr', line)
    for line in list2
]                                                                               # <enforce *$xhr />

list2 = [
    re.sub(r'^\*\$\~?xmlhttprequest.*', '*$xhr', line)
    for line in list2
]                                                                               # <enforce *$xhr />

list2 = [
    re.sub(r'^\*\$important.*', '', line)
    for line in list2
]                                                                               # <remove *$important filters />

list2 = [
    re.sub(r'^\*\$.*\.js$', '', line)
    for line in list2
]                                                                               # <remove *$...js filters />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print('18/21 : remove broken filters and fix false regex ')

list2 = [
    line
    for line in list2
    if re.search(r'^[^\(\)\[\]\{\}\~]', line)
]                                                                               # <remove broken filters; improve this filter />

list2 = [
    line
    for line in list2
    if not(re.search(r'^.*\([^\)]*$', line))
]                                                                               # <remove broken filters; improve this filter for multiple () />

list2 = [
    line
    for line in list2
    if not(re.search(r'^.*\[[^\]]*$', line))
]                                                                               # <remove broken filters; improve this filter for multiple [] />

list2 = [
    line
    for line in list2
    if not(re.search(r'^.*\{[^\}]*$', line))
]                                                                               # <remove broken filters; improve this filter for multiple {} />

list2 = [
    line
    for line in list2
    if not(re.search(r'^/.*[\[\\].*[^/]$', line))
]                                                                               # <remove broken filters (unterminated regex) />

list2 = [
    line
    for line in list2
    if not(re.search(r'^/.*\\/$', line))
]                                                                               # <remove broken regex (bad termination) />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print('19/21 : simplify urls keeping last /* part')

list2s = [
    line
    for line in list2
    if re.search(r'[\#\@\$]', line)
]                                                                               # <segregate *#(cosmetics) *@(exceptions) *$(removeparam and others) filters/>

list2  = set(list2) - set(list2s)

# <cleaunp cosmetic filters >

list2s = [
    line
    for line in list2s
    if not(re.search(r'^[_\W]*\:is', line))
]                                                                               # <remove *##:is filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'^[_\W]*\:matches', line))
]                                                                               # <remove *##:matches filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'^[_\W]*\:root', line))
]                                                                               # <remove *##:root filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'^[_\W]*\:xpath', line))
]                                                                               # <remove *##:xpath filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'not\(this\-site\-promotes\-malware\)', line))
]                                                                               # <remove spurious filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'not\(obhod\-adblocka\)', line))
]                                                                               # <remove spurious filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'not\(my\-obnaruzhili\-blokirovshchik\)', line))
]                                                                               # <remove spurious filters />

list2s = [
    line
    for line in list2s
    if not(re.search(r'^[_\W]*\:not\(input\)\:not\(textarea\)', line))
]

list2s = [
    line
    for line in list2s
    if not(re.search(r'removeparam.*smilformats', line))
]

list2s = [
    line
    for line in list2s
    if not(re.search(r'removeparam.*formatsprofile', line))
]

# </cleaunp cosmetic filters >

list2 = [
    re.sub(r'^.+(?=/[^/]+$)', '', line)
    for line in list2
]                                                                               # <simplify urls keeping last /* part />

list2 = [
    line
    for line in list2
    if len(line) > 3
]                                                                               # <keep filters with len > 3 />

list2 = [
    line
    for line in list2
    if (re.search(r'[^\[\]\{\}\;\,\\]', line))
]                                                                               # <remove broken regex filters />

list2 = list(filter(None, list2))                                               # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

print('20/21 : apply <regex_white_list> rules', sep = '')

# <get regex white list from file, dedup, sort and clean up filters>

list9 = list(
    filter(
        None,
        [
            re.sub(r'^ *!.*', '', line).strip()                                 # <remove ! comments />
            for line in open(
                file9_in_name,
                encoding='UTF-8'
            )                                                                   # <populate <regex_white_list> />
        ] + [
            ('^[_\W]*' + re.sub(r'\.', '\.', tld) + '[_\W]*$')
            for tld in iana_sld
        ]                                                                       # <add regex rules to enforce sld whitelisting />
    )                                                                           # <remove empty elements />
)

for pattern in tqdm.tqdm(list9) :
    try :
        pattern = re.compile(r'' + (pattern[: -1] + '(?:\$important)?$'))
        list2 = [
            line
            for line in list2
            if not(pattern.search(line))
        ]                                                                       # <remove filters based on <regex-white_list> />
        list5 = [
            line
            for line in list5
            if (
                not(pattern.search(re.sub(r'\$important$', '', line)[1: -1])) 
                and 
                re.search(r'\w+', re.sub(r'\$important$', '', line)[1: -1])
            )
        ]                                                                       # <remove text-only regex filters based on <regex-white_list> />
    except :
        print('Error: check for ' + pattern + ' pattern in regex_white_list')

list2 = list(filter(None, list2))                                               # <remove empty elements />

# </get regex white list from file, dedup, sort and clean up filters>

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

# <write extracted regex type filters>

# <open file5_out file and write header>

file5_out = open(
    file5_out_name,
    'w',
    encoding='UTF-8'
)

file5_out.write(
      '! description: personal regex filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_regex_block_list\n'
    + '! title: regex block list\n'
)

# </open file5_out file and write header>

file5_out.writelines(line + '\n' for line in list5)
file5_out.close()

print(
    '\n',
    '        ',
    '{:,}'.format(len(list5)),
    ' regex filters written to ',
    file5_out_name,
    '\n',
    sep = ''
)

# </write extracted regex type filters>

print('21/21 : deflat url filters redundant with regex filters', sep = '')

# <remove url filters covered by regex filters>

for pattern in tqdm.tqdm(list5):
    try :
        pattern = re.compile(r'' + re.sub(r'\$important$', '', pattern)[1: -1]) # < create regex pattern for faster processing />
        list2 = [
            line
            for line in list2
            if not(pattern.search(' ' + line + ' '))
        ]
    except :
        print('Error: check for ' + pattern + ' regex pattern in url sources')

# </remove url filters covered by regex filters>

# <aggregate filters >

list2 = sorted(set(list2) | set(list2s) | set(list5))                           # <join lists2, list2s, list5' />
del(list2s)                                                                     # <discard list2s, keep list5/>

# </aggregate filters >

print(
    '       ',
    '{:,}'.format(len(list2) + len(list5)),
    'filters kept'
)

# <segregate domains from list >

print('\nListing domain filters :')

list3 = [
    re.sub(r'\$important$', '', line)
    for line in list2
    if (re.sub(r'^(?:[-\w]*\.)*', '', re.sub(r'\$important$', '', line)) in iana_tld)
]                                                                               # <get (@.)+tld domains, removing trailing $important />

list3 = [
    line
    for line in list3
    if line[0] != '-'
]                                                                               # <remove -@.@ from domains list />

list3 = sorted(set(list3))
list2 = sorted(set(list2) - set(list3))                                         # <only domains part are processed in this section; @.js are kept in list2 />

list3 = [
    re.sub(r'^[-_\.0-9]*\.', '', line)
    for line in list3
]                                                                               # <remove numerical low levels from domains and preceding . />

list3 = sorted(set(list3) - set(iana_sld))                                      # <remove IANA sld root domains />

print(
    '       ',
    '{:,}'.format(len(list3)),
    'domains kept'
    )

# </segregate domains from list >

# <get domains white list from file, dedup, sort and substract from domains filters>

list8 = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^ *!.*', '', line.strip())
                for line in open(file8_in_name, encoding='UTF-8')
                if re.sub(r'^ *!.*', '', line.strip()) != ''
            ]                                                                   # <populate list removing ! comments />
        )                                                                       # <remove empty elements />
    )
)

list3 = sorted(set(list3) - set(list8))                                         # <remove whitelisted domains />

print(
    'domains white list applied:\n'
    '       ',
    '{:,}'.format(len(list3)),
    'domains kept'
    )

# </get domains white list from file, dedup, sort and substract from domains filters>

# <remove L5+ domains >

list3 = [
    re.sub(r'^(?:[-\w]+\.)+(?=(?:[-\w]+\.){3}[\w]+$)', '', line)                # <remove L5+ domains />
    for line in list3
]

list3 = sorted(set(list3))

print(
    'L5+ domains removed:\n',
    '       ',
    '{:,}'.format(len(list3)),
    'domains kept'
    )

# </remove L5+ domains >

# <preserve low level filters of white listed domains >

print('\npreserving low level filters of white listed domains', sep = '')

list3s = [
    line
    for line in tqdm.tqdm(list3)
    if (re.sub(r'^([-\w]+\.)+', '', line) in list8)
]                                                                               # <get (@.)+tld domains, removing trailing $important />

list3 = sorted(set(list3) - set(list3s))

# </preserve low level filters of white listed domains >

# <deflat domain filters >

print('\ndeflating domain filters, pass 1 / 2:')

list3 = [
    re.sub(r'^[-\w]+\.', '', line) if (
        (re.sub(r'^[-\w]+\.', '', line) not in iana_sld)
        and
        (re.sub(r'^[-\w]+\.', '', line) not in list8)
    )
    else line
    for line in list3
]

list3 = sorted(set(list3))

print(
    '       ',
    '{:,}'.format(len(list3) + len(list3s)),
    'domains kept'
    )

print('deflating domain filters, pass 2 / 2:')

list3 = [
    re.sub(r'^[-\w]+\.', '', line) if (
        (re.sub(r'^[-\w]+\.', '', line) not in iana_sld)
        and
        (re.sub(r'^[-\w]+\.', '', line) not in list8)
    )
    else line
    for line in list3
]

list3 = sorted(set(list3))

print(
    '       ',
    '{:,}'.format(len(list3) + len(list3s)),
    'domains kept'
    )

# </deflat domain filters >

#         ## <filter() + map() option>
#         #list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3_filter))) == 0) else '', tqdm.tqdm(list3)))
#         #list3 = [line for line in list3 if line]    # <cleanup empty lines/>
#         ## </filter() + map() option>

#         ## <filter() + list comprehension option; may worth it a benchmark vs map()?>
#         ##list3 = [line for line in list3 if len(list(filter(lambda substring: ('.' + substring) in line, tqdm.tqdm(list3_filter[:n])))) == 0]
#         ## </filter() + list comprehension option>

#         # </remove redundant domains from list>

list3 = sorted(set(list3) | set(list3s))                                        # <join list3, list3s />
del(list3s)                                                                     # <clean up; make sure list3s is not used anymore hereafter/>

list2 = sorted(set(list2) | set(list3))                                         # <joint list2, list3 />

print(
    '       ',
    '{:,}'.format(len(list2)),
    'filters kept'
    )

# <dedup filter if filter$important is present >

print('dedup filter if filter($|,)important present', sep = '')

list2s = [
    line
    for line in list2
    if re.search(r'[\$\,]important$', line)
]                                                                               # <segregate ($|,)important filters />

list2  = set(list2) - set(list2s)

list2 = [
    line
    for item in tqdm.tqdm(list2s)
    for line in list2
    if (item != (line + '$important') and (item != (line + ',important')))
]

list2 = sorted(set(list2) | set(list2s))                                        # <aggregate lists />
del(list2s)

print(
    '{:,}'.format(len(list2)),
    'filters remaining after compilation'
)

# </dedup filter if filter$important is present >

# <process filter list>

# <save a backup renamed *_old; overwrite if exists>

filelist = os.listdir('.')

if file2_out_name + '_old' in filelist : os.remove(file2_out_name + '_old')
os.rename(file2_out_name, file2_out_name + '_old')

print(
    'Backup saved:',
    file2_out_name + '_old\n'
)

# </save a backup renamed *_old; overwrite if exists>

# <write main output>

print('Added generic filters and exceptions\n')

list2.append('/^(?:[-\w]+\.)*[-_0-9]+\.[a-z]+(\.[a-z]+)?//')    # <add filter to block [-_/\.0-9]+\.[a-z]+ domains />
list2.append('/^go\./$important')
list2.append('/^s?metrics?\./$important')

list2.append('*$beacon')
list2.append('*$csp=all')
list2.append('*$inline-font')
list2.append('*$inline-script')
list2.append('*$object')
list2.append('*$other')
list2.append('*$ping')
list2.append('*$popunder')
list2.append('*$websocket')
list2.append('*$xhr')

list2.append('@@||accounts.google.com$domain=youtube.com')
list2.append('@@||amazon.com^$inline-script,1p')
list2.append('@@||amazon.es^$inline-script,1p')
list2.append('@@||backmarket.es^$inline-script,1p')
list2.append('@@||bbc.com^$inline-script,1p')
list2.append('@@||cloudfront.net^$script,domain=backmarket.es')
list2.append('@@||gitlab.com^$inline-script,xhr,1p')
list2.append('@@||google.com^$inline-script,1p')
list2.append('@@||googlevideo.com^$removeparam=/mgte/')
list2.append('@@||googlevideo.com^$xhr')
list2.append('@@||gstatic.com^$xhr,domain=youtube.com')
list2.append('@@||gstatic.com/ui/v1/icons/*$inline-font,domain=google.com')
list2.append('@@||gstatic.com/ui/v1/icons/*$xhr,domain=google.com')
list2.append('@@||iberia.com^$inline-script,1p')
list2.append('@@||ikea.com^$inline-script,1p')
list2.append('@@||ikea.com/*/header-footer/menu-products.html$xhr,1p')
list2.append('@@||ikea.es^$inline-script,1p')
list2.append('@@||imf.org^$inline-script,1p')
list2.append('@@||licdn.com^$xhr,domain=linkedin.com')
list2.append('@@||linkedin.com^$inline-script,1p')
list2.append('@@||linkedin.com^$removeparam=/redir/')
list2.append('@@||mail.google.com^$removeparam=view')
list2.append('@@||mail.google.com^$xhr,1p')
list2.append('@@||meteoblue.com^$inline-script,xhr,1p')
list2.append('@@||meteoblue.com^$removeparam=/callback/i')
list2.append('@@||meteoblue.com^$removeparam=/metric/i')
list2.append('@@||morningstar.es^$inline-script,1p')
list2.append('@@||openstreetmap.org^$xhr,1p')
list2.append('@@||startpage.com^$inline-script,1p')
list2.append('@@/[_\W]adunits?[_\W]/$domain=youtube.com')
list2.append('@@||wired.com^$inline-script,1p')
list2.append('@@||worldbank.org^$inline-script,1p')
list2.append('@@||www.linkedin.com^$inline-script,xhr,1p')
list2.append('@@||youtube.com^$inline-script,xhr,1p')

list2 = sorted(set(list2))

file2_out = open(
    file2_out_name,
    'w',
    encoding='UTF-8'
)

file2_out.write(
    '! description: personal filters for uBO; yet under heavy debugging\n' +
    '! expires: 1 day\n' +
    '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/' + file2_out_name + '\n' +
    '! title:' + file2_out_name + '\n' +
    '! ===========================================================================================\n' +
    '! simple, general filters preferred rather than complicated, specific ones\n' +
    '! regex only when efficient\n' +
    '! exceptions only if no better choice\n' +
    '! ===========================================================================================\n' +
    '! sources:\n'
)

file2_out.writelines('! ' + line + '\n' for line in list1)

file2_out.write(
    '! ===========================================================================================\n'
)

file2_out.writelines(line + '\n' for line in list2)
file2_out.close()

print(
    'Results saved to textfile <' + file2_out_name + '>\n'
)

# </write main output>

# <write domain type filters />

# <open file3_out file and write header >

file3_out = open(
    file3_out_name,
    'w',
    encoding='UTF-8'
)

file3_out.write(
      '! description: personal domain filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_domain_block_list\n'
    + '! title: domain block list\n'
    )

# <\open file3_out file and write header />

list3 = set(list3)
list3 = sorted(
    list3,
    key = lambda x: (re.sub(r'^.*\.(?=[^\.]+\.[^\.]+\Z)', '', x))
)                                                                               # <sort by a-z @(.@) />

file3_out.writelines(line + '\n' for line in list3)
file3_out.close()

print(
    '{:,}'.format(len(list3)),
    ' domain filters written to '
    + file3_out_name +
    '\n',
    sep = ''
)

# </write domain type filters />

# <write extracted url type filters>

# <open file4_out file and write header>

file4_out = open(
    file4_out_name,
    'w',
    encoding='UTF-8'
)

file4_out.write(
      '! description: personal url filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_url_block_list\n'
    + '! title: url block list\n'
)

# </open file4_out file and write header>

list4 = set(list2) - set(list3) - set(list5)

list4 = [
    re.sub(r'\$important$', '', line)
    for line in list4
]                                                                               # <remove ''$important'' tag at the end (if present)/>

list4 = [
    line
    for line in list4
    if re.search(r'^[-/\.\w]+$', line)
]                                                                               # <keep url items/>

list4 = sorted(list4)

file4_out.writelines(line + '\n' for line in list4)
file4_out.close()

print(
    '{:,}'.format(len(list4)),
    ' url filters written to ',
    file4_out_name,
    '\n',
    sep = ''
)

# </write extracted url type filters />

# <write extracted filters except domains>

# <open file7_out file and write header>

file7_out = open(
    file7_out_name,
    'w',
    encoding='UTF-8'
)

file7_out.write(
      '! description: personal filters for ublock_origin (excepting domains)\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ublock_list_except_domains\n'
    + '! title: ublock list except domains\n'
)

# <\open file7_out file and write header />

list7 = set(list2) - set(list3)
list7 = sorted(list7)

file7_out.writelines(line + '\n' for line in list7)
file7_out.close()

print(
    '{:,}'.format(len(list7)),
    ' lines written to ',
    file7_out_name,
    '\n',
    sep = ''
)

# </write extracted filters except domains />

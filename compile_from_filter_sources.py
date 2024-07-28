'''
Compile a single deduplicated block list from url sources
'''

# <product backlog>

    # <sprint #1: dedup urls/>
    # <sprint #2: apply whitelisting to cosmetic filters/>

# </product backlog>

# <libs & settings>

import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import re                                                                       # <regex capabilities />
import requests                                                                 # <fetch urls />
from multiprocessing import Pool as ThreadPool                                  # <multithreading function/>
from multiprocessing import Value                                               # <multithreading function/>
from time import time

file1_in_name   = 'filter_sources'
file2_out_name  = 'compiled_block_list'
file3_out_name  = 'ipfire_domain_block_list'
file4_out_name  = 'ipfire_url_block_list'
file5_out_name  = 'ipfire_regex_block_list'
file7_out_name  = 'ublock_list_except_domains'
file8_in_name   = 'domains_white_list'
file9_in_name   = 'regex_white_list'
no_proxy        = {'https': '', 'http': ''}
local_proxy     = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}
thr             = os.cpu_count()
t_start         = time()

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

# <get filter url sources >

list1 = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^ *!.*$', '', line.strip())                            # <remove ! comments />
                for line in open(file1_in_name, encoding='UTF-8')
            ]                                                                   # <populate source lists />
        )                                                                       # <remove empty elements />
    )
)

# </get filter url sources >

# <populate main list (list2) >

print(
    'reading ',
    len(list1),
    ' sources\n',
    sep = ''
)

def f00(line) :

    global proxy_servers
    list2 = set()

    try :

        response = requests.get(
            line,
            timeout = 20,
            proxies = proxy_servers
        )
        if response.status_code :
            list2.update(response.text.split('\n'))
            print(
                line,
                '\n',
                '    ',
                '{:,}'.format(len(list2)),
                'filters read',
                flush = True
            )
        else :
            print(
                'Error: could not load ' + line,
                flush = True
            )
        list2 = sorted(list2)

    except :

        print(
            'Error: could not load ' + line,
            flush = True
        )

    return list2

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f00, list1)                                                    # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = sorted(
    set(
        [
            line if (type(line) == str)                                         # <prevents string atomization into chars is string type />
            else item
            for line in list2
            for item in line
        ]                                                                       # <flatten list />
    )                                                                           # <dedup list />
)

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '\n',
    '{:,}'.format(len(list2)),
    'unique filters gathered'
)

# </populate main list (list2) >

# <load iana tld >

iana_tld = set()

try :

    response = requests.get(
        'https://data.iana.org/TLD/tlds-alpha-by-domain.txt',
        timeout = 20,
        proxies = proxy_servers
    )

except :

    print(
        'Error: could not load https://data.iana.org/TLD/tlds-alpha-by-domain.txt',
        flush = True
    )

if response.status_code :
    iana_tld.update(response.text.split('\n'))

iana_tld = sorted(
    list(
        filter(
            None,
            [
                re.sub(r'^#.*$', '', line).strip().lower()
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

print('\nIANA top level domains (TLD) list loaded\n')

# </load iana tld >

# <process filter list>

print(
    '--------------------\n',
    'Transforming filters\n',
    '--------------------\n',
    sep = ''
)

# <transforming loop>

print(' 1/20 : remove leading / trailing / dup spaces ')

def f01(line) :

    line = re.sub(r'[\t ]+', ' ', line).strip()                                 # <replace tab with space, dedup spaces and remove leading/trailing spaces />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f01, list2)                                                    # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2)),
    'filters kept'
)

print(' 2/20 : remove comments ')

def f02(line) :

    line = re.sub(r' #.*$', '', line)                                           # < clean # comments on the right/>

    if re.search(r'^[\!\[\{]', line) :
        line = ''                                                               # <remove !comment [comment] {comment} />
    elif re.search(r'^#(?![\?\@\#])', line) :
        line = ''                                                               # <remove #comment; preserve cosmetics and exceptions />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f02, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2)),
    'filters kept'
)

print(' 3/20 : clean dns domain filters, :port, http(s): ')

def f03(line) :

    line = re.sub(r'https?\:/*', '', line)                                      # <remove http(s):/* />
    line = re.sub(r'www\d*\.', '', line)                                        # <remove www#. />
    line = re.sub(r'^\d+(?:\.\d+)+ ', '', line)                                 # <remove leading 0.0.0.0 or 127.0.0.1 (dns style filter) />
    line = re.sub(r'^\:+1 ', '', line)                                          # <remove leading ::1 (dns style filter) />
    line = re.sub(r'^\|{1,2}([-\.\w]+)\^$', r'\1', line)                        # <cleanup || ^ from abp domain syntax />
    line = re.sub(r'^\:\d+', '', line).strip()                                  # <remove leading :port />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f03, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2)),
    'filters kept'
)

# <segregate domains from list >

print('\nListing domain filters\n')

def f_clean_domains_1(line) :

    global iana_sld

    if re.sub(
        r'^([-\w]*\.)*',
        '',
        re.sub(r'/(?:\$important)?$', '', line)
    ) in iana_sld :                                                             # < check for a match with (@.)+sld />
        if line[0] != '-' :
            line = re.sub(r'/(?:\$important)?$', '', line)                      # < remove trailing /, $important />

    return line

pool = ThreadPool(thr)                                                          # < make the pool of workers />
list2 = pool.map(f_clean_domains_1, list2)                                      # < execute function by multi-threading />
pool.close()                                                                    # < close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # < only domains part are processed in this section; @.js are kept in list2 />

def f_list_domains(line) :

    global iana_sld

    if re.sub(
        r'^\.?([-\w]+\.)+',
        '',
        re.sub(r'\$important$', '', line)
    ) not in iana_sld :                                                         # < check for a match with (@.)+sld />
        line = ''                                                               # < return only domain items />

    return line

pool = ThreadPool(thr)                                                          # < make the pool of workers />
list3 = pool.map(f_list_domains, list2)                                         # < execute function by multi-threading />
pool.close()                                                                    # < close the pool and wait for the work to finish />
pool.join()

list3 = list(filter(None, sorted(set(list3))))
list2 = list(filter(None, sorted(set(list2) - set(list3))))                     # < only domains part are processed in this section; @.js are kept in list2 />

# </segregate domains from list >

print(' 4/20 : remove items containing % ?? about: $badfilter localhost; remove IP4 IP6')

def f04(line) :

    if re.search(r'\%', line) :
        line = ''                                                               # <remove items comprising % >
    elif re.search(r'(?<!\\\?)\?{2,}', line) :
        line = ''                                                               # <remove items comprising ?? >
    elif re.search(r'about\:', line) :
        line = ''                                                               # <remove items comprising about: >
    elif re.search(r'[,\$]badfilter', line) :
        line = ''                                                               # <remove items comprising $badfilter />
    elif re.search(r'localhost', line) :
        line = ''                                                               # <remove items containing localhost />
    elif re.search(r'\:{2,}', line) :
        line = ''                                                               # <remove IP6 addresses :: />
    elif re.search(r'^[^a-z]+$', line) :
        line = ''                                                               # <remove filters comprised only by symbols and numbers (includes IP4 addresses) />
    elif (
        re.search(r'\:', line) 
        and not re.search(r'[#\$\?]', line)
        and not re.search(r'^/.*/(?:\$important)?$', line)
        ) :
        line = ''                                                               # <remove lines containing : except for regex and cosmetics filters/>

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f04, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3)),
    'filters kept'
)

print(' 5/20 : apply lower case except for cosmetics and regex')

def f05(line) :

    if not re.search(r'[#@\\]', line) :
        line = line.lower()                                                     # <apply lower case except cosmetics and regex />

    if re.search(r'^/.*\\/$', line) :
        line = ''                                                               # <remove broken regex (bad termination) />

    line = re.sub(r'/+$', '/', line)                                            # <fix trailing // />
    line = re.sub(r'\$/$', '/', line)                                           # <fix trailing $/ />
    line = re.sub(r'^(/.*)\.\*/$', r'\1/', line)                                # <fix regex trailing .*/ />
    line = re.sub(r'^(/[-\.\+\~\!\=/\w]+/)$', r'\1*', line)                     # <add trailing * for /@/ url filters (false regex) />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f05, list2)                                                    # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

# <segregate regex filters >

list5 = [
    line
    for line in list2
    if re.search(r'^/.+/(?:\$important)?$', line)                               # <match regex filter syntax />
]

list2 = list(filter(None, sorted(set(list2) - set(list5))))

list5 = [
    line for line in list5
    if not re.search(r'^/\*', line)                                             # <remove /* bad regex filter />
    if not re.search(r'[\^\?]\*', line)                                         # <remove wrong ^* ?* in regex filter />
    if not re.search(r'/\$(?!important)', line)                                 # <remove wrong /$ in regex filter />
    if not re.search(r'^/[\^\(]http', line)                                     # <remove [^(]http regex filter />
    if not re.search(r'^/www\\\.', line)                                        # <remove /www\. regex filter />
    if not re.search(r'^/[\.\d\*\\/]+/$', line)                                 # <remove numerical regex filter />
    if not re.search(r'^/[-\w]*\*[-\w]*/$', line)                               # <remove /@*@/ regex filter />
    if not re.search(r'^/(?:[-\w\.]*\\?/)+[-\w\.]*/$', line)                    # <remove regex filter containing @\/@ />
    if line[1: -1] not in iana_sld                                              # <remove /item/ if item in iana_sld />
    if len(line) > 5                                                            # <remove too short regex filter />
]

list5 = list(filter(None, sorted(set(list5))))

# </segregate regex filters >

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept'
)

print(' 6/20 : generalize cosmetic filters (*##), exceptions (*#@ *#? *@@) and removeparams ')

def f06(line) :

    line = re.sub(r'^.*(?=#[#@\?])', '*', line)                                 # <generalize *## *#@ *#? />
    line = re.sub(r'^.*(?=@@)', '*', line)                                      # <generalize *@@ />
    line = re.sub(r'^.*removeparam\=', '*$removeparam=', line)                  # <generalize *$removeparam />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f06, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept'
)

print(' 7/20 : remove cosmetic filters (## #?) and exceptions (@@ #@) except *##:')

def f07(line) :

    if re.search(r'^\*?#[^#]', line) :                                          # <remove *# not followed by # />
        line = ''
    elif re.search(r'^\*?@', line) :                                            # <remove @@ exceptions />
        line = ''
    elif re.search(r'^\*##(?!\:not\(html\))', line) :                           # <remove cosmetic filters not matching *##:not(html) pattern />
        line = ''

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f07, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept'
)

print(' 8/20 : split urls with $ domain=, denyallow= ')

def f08(line) :

    if re.search(r'\$.*(domain|denyallow)=', line) :
        domains_part = re.sub(r'^.*(domain|denyallow)=', '', line).split('|')   # <split domains and  url part />
        url_part     = [re.sub(r'\$.*$', '', line)]                             # <add url part/>
        line = domains_part + url_part
    else:
        [line]

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f08, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = sorted(
    set(
        [
            line if (type(line) == str)                                         # <prevents string atomization into chars is string type />
            else item
            for line in list2
            for item in line
        ]                                                                       # <flatten list />
    )                                                                           # <dedup list />
)

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept'
)

print(' 9/20 : clean from=, path=, replace=, transform=')

def f09(line) :

    line = re.sub(r',?(from|path|replace|transform)=.*$', '', line)             # <remove (,)from=.* , (,)path=.* , (,)replace=.* , (,)transform=.* />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2 = pool.map(f09, list2)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # <remove empty elements />

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list5 = pool.map(f09, list5)                                                    # <execute function by multithreading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list5 = list(filter(None, sorted(set(list5))))                                  # <remove empty elements />

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept'
)

i   = 0
converged = False

while not converged :                                                           # <recursive loops until converged />

    # < transforming loop >

    i += 1
    n_1 = len(list2)

    print(
        'loop ', i, '\n',
        '-------',
        sep = ''
    )

    print('10/20 : split , ~ space separated items ')

    def f10(line) :

        line = re.sub(r'^,', '', line)                                          # <remove leading , />
        line = re.sub(r',$', '', line)                                          # <remove trailing , />

        if re.search(r'^[- /\.\,\~\w]+$', line) :
            line = re.split(r'[- \,\~]', line)                                  # <split domains />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f10, list2)                                                # <execute function by multithreading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = sorted(
        set(
            [
                line if (type(line) == str)                                     # <prevents string atomization into chars is string type />
                else item
                for line in list2
                for item in line
            ]                                                                   # <flatten list />
        )                                                                       # <dedup list />
    )

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('11/20 : remove @.exe @.gif @.rar @.zip')

    def f16(line) :

        if re.search(r'\.rar$', line) :
            line = ''                                                           # <remove @.rar filters />
        elif re.search(r'\.zip$', line) :
            line = ''                                                           # <remove @.zip filters />
        elif re.search(r'\.gif$', line) :
            line = ''                                                           # <remove @.zip filters />
        elif re.search(r'\.exe$', line) :
            line = ''                                                           # <remove @.exe filters />
        elif re.search(r'\.webp$', line) :
            line = ''                                                           # <remove @.webp filters />
        elif re.search(r'\.mp4$', line) :
            line = ''                                                           # <remove @.mp4 filters />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f16, list2)                                                # <execute function by multithreading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('12/20 : clean up leading symbols numbers prefix etc')

    def f11(line) :

        line = re.sub(r'^[^a-z]*(?=[\*\$])', '', line)                          # <remove leading symbols and numbers preceding * ? />
        line = re.sub(r'^[^\*a-z]*(?=[/\.\?])', '', line)                       # <remove leading symbols and numbers preceding / . ? />
        line = re.sub(r'^[/\.]?\w(?=[/\.\$])', '', line)                        # <remove leading single a-z0-9 char preceding / . $ />
        line = re.sub(r'^\|+', '', line)                                        # <remove leading | />
        line = re.sub(r'^\W*(?=\$)', '*', line)                                 # <replace leading symbols followed by $ (/$ .$ =$ ?$ etc) with *$ />
        line = re.sub(r'^\.?[-\*\w]+/', '/', line)                              # <replace leading (.)@/ with / />
        line = re.sub(r'^\*(?![\$#])', '', line)                                # <remove leading * except for generic $ # filters />
        line = re.sub(r'^/?jquery\.', '', line)                                 # <remove leading /?jquery\. />
        line = re.sub(r'^/?static\.', '', line)                                 # <remove leading /?static\. />
        line = re.sub(r'^/?www\.', '', line)                                    # <remove leading /?www\. />
        line = re.sub(r'^/?ww[\d]+\.', '', line)                                # <remove leading /?ww[\d]+\. />
        line = re.sub(r'^.*\.asp(?=\?)', '', line)                              # <remove .*asp lines />
        line = re.sub(r'^.*\.cgi(?=\?)', '', line)                              # <remove .*cgi lines />
        line = re.sub(r'^.*\.php(?=\?)', '', line)                              # <remove .*php lines />
        line = re.sub(r'^.*\.php$', '', line)                                   # <remove .*php lines />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f11, list2)                                                # <execute function by multithreading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('13/20 : clean up trailing symbols numbers suffix $filters etc')

    def f12(line) :

        line = re.sub(r'[\^\|\=]\$', '$', line)                                 # <replace ^$ |$ =$ with $ />
        line = re.sub(r'[\#\,\~\|\^\?\=\&]+$', '', line)                        # <remove trailing # , ~ | ^ ? = & />
        line = re.sub(r'(?<!/)\*$', '', line)                                   # <remove trailing * except /url/* />
        line = re.sub(r'\.\*$', '.', line)                                      # <replace trailing .* with . />
        line = re.sub(r'\*\.$', '', line)                                       # <remove trailing *. />
        line = re.sub(r'\??\*\=.*$', '', line)                                  # <remove trailing (?)*=... />
        line = re.sub(r'^.*\.ashx\??$', '', line)                               # <remove *.ashx(?) filters />
        line = re.sub(r'^.*\.aspx\??$', '', line)                               # <remove *.aspx(?) filters />
        line = re.sub(r'^.*\.html?\??$', '', line)                              # <remove *.html(?) filters />
        line = re.sub(r'^.*\.jpe?g\??$', '', line)                              # <remove *.jp(e)g(?) filters />
        line = re.sub(r'^.*\.png\??$', '', line)                                # <remove *.png(?) filters />
        line = re.sub(r'^.*\.svg\??$', '', line)                                # <remove *.svg(?) filters />
        line = re.sub(r'\.js\??[^\./]*$', '.js', line)                          # <clean up trailing .js />
        line = re.sub(r'^([-\w]+)=.*$', r'\1', line)                            # <remove trailing .=.* />
        line = re.sub(r'^([-\.\w]+)/$', r'\1', line)                            # <remove trailing /  />
        line = re.sub(r'\^\*$', '', line)                                       # <remove trailing ^* />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f12, list2)                                                # <execute function by multithreading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('14/20 : split domain and url ')

    def f13(line) :

        line = line.strip()

        if re.search(r'^[-\.\w]+\.[a-z]+/.*', line) :
            domain_part = [re.sub(r'/.*$', '', line)]                           # <add domain part />
            url_part    = re.sub(r'^[-\.\w]+/', '/', line)                      # <add url part/>
            url_part    = [re.sub(r'^.+(?=/[^/]+(?:/\*)?$)', '', url_part)]     # <simplify url keeping last /* part />
            line = domain_part + url_part
        else:
            [line]
        
        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f13, list2)                                                # <execute function by multithreading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = sorted(
        set(
            [
                line if (type(line) == str)                                     # <prevents string atomization into chars is string type />
                else item
                for line in list2
                for item in line
            ]                                                                   # <flatten list />
        )                                                                       # <dedup list />
    )

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('15/20 : clean up urls')

    def f14(line) :

        line = re.sub(r'\*+', '*', line)                                        # <dedup * />
        line = re.sub(r'\.+', '.', line)                                        # <dedup . />
        line = re.sub(r'/+', '/', line)                                         # <dedup / />
        line = re.sub(r'^.*/\*/', '/', line)                                    # <replace /*/ with / />
        line = re.sub(r'[^\*]\$.*$', '', line)                                  # <remove $* tail except for *$ />
        line = re.sub(r'/wp\-content/uploads/.*$', '', line)                    # <clean trailing /wp-content/uploads/* />

        if re.search(r'^[-\w]+\\\.[-\w]+', line) :
            line = ''                                                           # <remove faulty \. />

        if re.search(r'^[-\.\w]+\^\*[-/\.\w]+', line) :
            line = ''                                                           # <remove spurious ^*/>

        if re.search(r'^[\./]?[-\w]*/[-\./\w]+[-\.\w](?:/\*)?$', line) :
            line = re.sub(r'^.+(?=/[^/]+(?:/\*)?$)', '', line)                  # <simplify urls keeping last /* part />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f14, list2)                                                # <execute function by multi-threading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('16/20 : arrange *$ filters; keep beacon csp inline-font inline-script object other ping popunder script websocket xhr ')

    def f17(line) :

        line = re.sub(r'\$\~?1p.*$', '', line)                                  # <remove $1p />
        line = re.sub(r'\$\~?3p.*$', '', line)                                  # <remove $3p />
        line = re.sub(r'\$\~?all.*$', '', line)                                 # <remove $all />
        line = re.sub(r'\$\~?css.*$', '', line)                                 # <remove $css />
        line = re.sub(r'\$\~?frame.*$', '', line)                               # <remove $frame />
        line = re.sub(r'\$\~?from.*$', '', line)                                # <remove $from />
        line = re.sub(r'\$\~?image.*$', '', line)                               # <remove $image />
        line = re.sub(r'\$\~?media.*$', '', line)                               # <remove $media />
        line = re.sub(r'\$\~?popup.*$', '', line)                               # <remove $popup />
        line = re.sub(r'\$\~?rewrite.*$', '', line)                             # <remove $rewrite />
        line = re.sub(r'\$\~?script.*$', '', line)                              # <remove $script />
        line = re.sub(r'\$\~?stylesheet.*$', '', line)                          # <remove $css />
        line = re.sub(r'\$\~?(?:sub)?doc(?:ument)?.*$', '', line)               # <remove $(sub)doc />
        line = re.sub(r'\$\~?third\-party.*$', '', line)                        # <remove $3p />

        line = re.sub(r'^\*\$important.*$', '', line)                           # <remove *$important />
        line = re.sub(r'^\*\$.*\.js$', '', line)                                # <remove *$...js filters />

        line = re.sub(r'^\*\$\~?beacon.*$', '*$beacon', line)                   # <enforce *$beacon />
        line = re.sub(r'^.*\$csp.*$', '*$csp=all', line)                        # <enforce *$csp=all />
        line = re.sub(r'^\*\$\~?inline\-font.*$', '*$inline-font', line)        # <enforce *$inline-font />
        line = re.sub(r'^\*\$\~?inline\-script.*$', '*$inline-script', line)    # <enforce *$inline-script />
        line = re.sub(r'^\*\$\~?object.*$', '*$object', line)                   # <enforce *$object />
        line = re.sub(r'^\*\$\~?other.*$', '*$other', line)                     # <enforce *$other />
        line = re.sub(r'^\*\$\~?ping.*$', '*$ping', line)                       # <enforce *$ping />
        line = re.sub(r'^\*\$\~?popunder.*$', '*$popunder', line)               # <enforce *$popunder />
        line = re.sub(r'^\*\$\~?rpc.*', '', line)                               # <remove *$rpc />
        line = re.sub(r'^\*\$\~?web.*', '', line)                               # <remove *$web />
        line = re.sub(r'^\*\$\~?websocket.*$', '*$websocket', line)             # <enforce *$websocket />
        line = re.sub(r'^\*\$\~?xhr.*$', '*$xhr', line)                         # <enforce *$xhr />
        line = re.sub(r'^\*\$\~?xmlhttprequest.*$', '*$xhr', line)              # <enforce *$xhr />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f17, list2)                                                # <execute function by multi-threading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('17/20 : remove broken filters and fix regex ')

    def f18(line) :

        if re.search(r'^[#\!\<]$', line) :
            line = ''                                                           # <remove # ! < leaded lines />
        elif re.search(r'^\*?#[^#]', line) :
            line = ''                                                           # <remove *# not followed by # />
        elif re.search(r'^[/\*]?[\^\&\?\:\;\"\@\+\(\)\[\]\{\}\~]', line) :
            line = ''                                                           # <remove ^ & ? : ; " @ + ( ) [ ] { } ~ leaded lines />
        elif re.search(r'^/.*\\/$', line) :
            line = ''                                                           # <remove broken regex (bad termination) />
        elif (
            re.search(r'[\[\]\{\}\;\,\<\>\\]', line)
            and not(re.search(r'^\*##', line))
            and not(re.search(r'^/.*/(?:\$important)?$', line))
            ) :
            line = ''                                                           # <remove broken regex or cosmetic filters />

        line = re.sub(r'/+$', '/', line)                                        # fix trailing // />
        line = re.sub(r'\$/$', '/', line)                                       # fix trailing $/ />
        line = re.sub(r'^(/.*)\.\*/$', r'\1/', line)                            # fix regex trailing .*/ />
        line = re.sub(r'^(/[-\.\+\~\!\=/\w]+/)$', r'\1*', line)                 # <add trailing * for /@/ url filters (false regex) />

        # < remove unbalanced () [] {} >

        n = 0
        depth_p = 0
        depth_b = 0
        depth_l = 0
        flag = 0
        while n < len(line) :
            if line[n] == '(' : depth_p += 1
            if line[n] == ')' : depth_p -= 1
            if line[n] == '[' : depth_b += 1
            if line[n] == ']' : depth_b -= 1
            if line[n] == '{' : depth_l += 1
            if line[n] == '}' : depth_l -= 1
            if min(depth_p, depth_b, depth_l) < 0 : flag = 1
            n += 1

        if (flag > 0 or depth_p != 0 or depth_b != 0 or depth_l != 0) : line = ''

        # < remove unbalanced () [] {} >

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f18, list2)                                                # <execute function by multi-threading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    print('18/20 : simplify urls keeping last /* part')

    def f19(line) :

        if not re.search(r'[#@\\]', line) :
            line = line.lower()                                                 # <apply lower case except cosmetics and regex />

        if re.search(r'[\#\@\$]', line) :                                       # <segregate *#(cosmetics) *@(exceptions) *$(removeparam and others) filters/>
            if re.search(r'^[_\W]*\:is', line) :
                line = ''                                                       # <remove *##:is filters />
            elif re.search(r'^[_\W]*\:match', line) :
                line = ''                                                       # <remove *##:matches filters />
            elif re.search(r'^[_\W]*\:root', line) :
                line = ''                                                       # <remove *##:root filters />
            elif re.search(r'^[_\W]*\:xpath', line) :
                line = ''                                                       # <remove *##:xpath filters />
            elif re.search(r'\$discovery', line) :
                line = ''

        if re.search(r'^[\./]?[-\w]+/[-\.\=\@\w/]+(?:/\*)?$', line) :
            line = re.sub(r'^.+(?=/[^/]+(?:/\*)?$)', '', line)                  # <simplify urls keeping last /* part />

        if re.search(r'[-\w]{40,}', line) :
            line = ''                                                           # <remove items with text strings longer than 40 chars />

        if len(re.findall(r'[a-z]', line)) <= 3 :
            line = ''                                                           # <keep filters with len > 3 />

        if (
            len(line) - len(re.findall(r'\d', line)) - len(re.findall(r'[a-z]', line)) <= 2
            and len(re.findall(r'\d', line)) >= len(re.findall(r'[a-z]', line))
            ) :
            line = ''                                                           # <keep filters more numbers than chars />

        return line

    pool = ThreadPool(thr)                                                      # <make the pool of workers />
    list2 = pool.map(f19, list2)                                                # <execute function by multi-threading />
    pool.close()                                                                # <close the pool and wait for the work to finish />
    pool.join()

    list2 = list(filter(None, sorted(set(list2))))                              # <remove empty elements />

    print(
        '       ',
        '{:,}'.format(len(list2) + len(list3) + len(list5)),
        'filters kept'
    )

    # <segregate regex filters >

    list5 = list5 + [
        line
        for line in list2
        if re.search(r'^/.+/(?:\$important)?$', line)                           # <match regex filter syntax />
    ]

    list2 = list(filter(None, sorted(set(list2) - set(list5))))

    list5 = [
        line for line in list5
        if not re.search(r'^/\*', line)                                             # <remove /* bad regex filter />
        if not re.search(r'[\^\?]\*', line)                                         # <remove wrong ^* ?* in regex filter />
        if not re.search(r'/\$(?!important)', line)                                 # <remove wrong /$ in regex filter />
        if not re.search(r'^/[\^\(]http', line)                                     # <remove [^(]http regex filter />
        if not re.search(r'^/www\\\.', line)                                        # <remove /www\. regex filter />
        if not re.search(r'^/[\.\d\*\\/]+/$', line)                                 # <remove numerical regex filter />
        if not re.search(r'^/[-\w]*\*[-\w]*/$', line)                               # <remove /@*@/ regex filter />
        if not re.search(r'^/(?:[-\w\.]*\\?/)+[-\w\.]*/$', line)                    # <remove regex filter containing @\/@ />
        if line[1: -1] not in iana_sld                                              # <remove /item/ if item in iana_sld />
        if len(line) > 5                                                            # <remove too short regex filter />
    ]

    list5 = list(filter(None, sorted(set(list5))))

    # </segregate regex filters >

    converged = (len(list2) == n_1)

    # </ transforming loop >

# <segregate domains from list >

print('\nListing domain filters\n')

pool = ThreadPool(thr)                                                          # < make the pool of workers />
list2 = pool.map(f_clean_domains_1, list2)                                      # < execute function by multi-threading />
pool.close()                                                                    # < close the pool and wait for the work to finish />
pool.join()

list2 = list(filter(None, sorted(set(list2))))                                  # < only domains part are processed in this section; @.js are kept in list2 />

def f_list_domains(line) :

    global iana_sld

    if re.sub(
        r'^\.?([-\w]+\.)+',
        '',
        re.sub(r'\$important$', '', line)
    ) not in iana_sld :                                                         # < check for a match with (@.)+sld />
        line = ''                                                               # < return only domain items />

    return line

pool = ThreadPool(thr)                                                          # < make the pool of workers />
list3b = pool.map(f_list_domains, list2)                                        # < execute function by multi-threading />
pool.close()                                                                    # < close the pool and wait for the work to finish />
pool.join()

list3 = list(filter(None, sorted(set(list3) | set(list3b))))
list2 = list(filter(None, sorted(set(list2) - set(list3))))                     # < only domains part are processed in this section; @.js are kept in list2 />

del list3b

# </segregate domains from list >

# <dedup . / leading filters >

print(
    'Dedup . / - leading filters and .js .css .ttf .woff .woff2 trailing filters'
)

list2s = [line[1:] for line in list2 if line[0] in './-']
list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <dedup . / - leading filters />

list2s = [line[:-3] for line in list2 if line[-3:] == '.js']
list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <dedup .js trailing filters />

list2s = [line[:-4] for line in list2 if line[-4:] == '.css']
list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <dedup .css trailing filters />

list2s = [line[:-4] for line in list2 if line[-4:] == '.ttf']
list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <dedup .ttf trailing filters />

list2s = [line[:-5] for line in list2 if line[-5:] == '.woff']
list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <dedup .woff trailing filters />

list2s = [line[:-6] for line in list2 if line[-6:] == '.woff2']
list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <dedup .woff2 trailing filters />

del(list2s)

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept\n',
    flush = True
)

# </dedup . / leading filters >

print('19/20 : apply <regex_white_list> rules', sep = '')

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
            ('^[_\W]*' + re.sub(r'\.', '\.', sld) + '[_\W]*$')
            for sld in iana_sld
        ]                                                                       # <add regex rules to enforce sld whitelisting />
    )                                                                           # <remove empty elements />
)

print(
    '       ',
    '<regex_white_list> loaded'
)

print(
    '       ',
    'removing regex filters based on <regex-white_list>')

list5 = list(filter(None, sorted(set(list5))))                                  # <remove empty elements />

def f20_5(pattern) :

    global list5
    list5wl = []

    try :
        pattern = re.compile(r'' + (pattern[: -1] + '(?:\$important)?$'))
        list5wl = [
            line
            for line in list5
            if (
                pattern.search(re.sub(r'\$important$', '', line)[1: -1])
                and 
                re.search(r'^\w+$', re.sub(r'\$important$', '', line)[1: -1])
            )
        ]                                                                       # <remove text-only regex filters based on <regex-white_list> />
    except :
        print(
            'Error: check for ' + pattern + ' pattern in regex_white_list',
            flush = True
        )

    return list5wl

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list5wl = list(pool.map(f20_5, list9))                                          # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list5wl = sorted(
    set(
        [
            line if (type(line) == str)                                         # <prevents string atomization into chars is string type />
            else item
            for line in list5wl
            for item in line
        ]                                                                       # <flatten list />
    )                                                                           # <dedup list />
)

list5 = list(filter(None, sorted(set(list5) - set(list5wl))))                   # <remove empty elements />

counter = Value('d', 0)
t0 = time()
counter_max = len(list9)

def f20_2(pattern) :

    global list2
    list2wl = []

    try :
        pattern = re.compile(r'' + (pattern[: -1] + '(?:\$important)?$'))
        list2wl = [
            line
            for line in list2
            if pattern.search(line)
            if not re.search(r'^\*\$', line)
            if not re.search(r'^\*##', line)
        ]                                                                       # <remove filters based on <regex-white_list> />
    except :
        print(
            'Error: check for ' + pattern + ' pattern in regex_white_list',
            flush=True
        )

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

    return list2wl

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2wl = pool.map(f20_2, list9)                                                # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()                                                                     # <wait for all threads in the pool to be shutdown />

list2wl = sorted(
    set(
        [
            line if (type(line) == str)                                         # <prevents string atomization into chars if string type />
            else item
            for line in list2wl
            for item in line
        ]                                                                       # <flatten list />
    )                                                                           # <dedup list />
)
list2 = list(filter(None, sorted(set(list2) - set(list2wl))))                   # <remove elements in list2wl and empty elements />

print()

print(
    '       ',
    '{:,}'.format(len(list2) + len(list3) + len(list5)),
    'filters kept',
    flush = True
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

print('20/20 : remove url filters redundant with regex filters', sep = '')

list5 = list(filter(None, sorted(set(list5))))                                  # <remove empty elements />

counter = Value('d', 0)
t0 = time()
counter_max = len(list5)

def f21(pattern) :

    global list2
    list2du = []

    try :
        pattern = re.compile(r'' + re.sub(r'\$important$', '', pattern)[1: -1]) # < create regex pattern for faster processing />
        list2du = [
            line
            for line in list2
            if pattern.search(' ' + line + ' ')
        ]
    except :
        print(
            'Error: check for ' + pattern + ' pattern in regex_white_list',
            flush=True
        )

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

    return list2du

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2du = pool.map(f21, list5)                                                  # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2du = sorted(
    set(
        [
            line if (type(line) == str)                                         # <prevents string atomization into chars is string type />
            else item
            for line in list2du
            for item in line
        ]                                                                       # <flatten list />
    )                                                                           # <dedup list />
)

# <aggregate filters >

list2 = list(filter(None, sorted((set(list2) - set(list2du)) | set(list5))))    # <join lists2, list5 and remove empty elements />

# </aggregate filters >

print(
    '\n       ',
    '{:,}'.format(len(list2) + len(list3)),
    'filters kept'
)

# <remove leading . , L5+ domains and numerial low levels >

def f_clean_domains_2(line) :

    line = re.sub(r'^(?:[-_\d]*\.)+', '', line)                                 # <remove numerical low levels from domains and preceding . />
    line = re.sub(r'^(?:[^\.]*\.)+(?=(?:[-\w]+\.){3}[\w]+$)', '', line)         # <remove L5+ domains />

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list3 = pool.map(f_clean_domains_2, list3)                                      # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list3 = list(filter(None, sorted(set(list3) - set(iana_sld))))                  # <remove IANA sld root domains />

print(
    '\nleading . , L5+ domains and numerical low levels removed:\n',
    '      ',
    '{:,}'.format(len(list3)),
    'domains kept'
    )

# </remove leading . , L5+ domains and numerial low levels >

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

#<open file8_in file and write sorted deduped domains_white_list >

filelist = os.listdir('.')

if file8_in_name + '_old' in filelist : os.remove(file8_in_name + '_old')
os.rename(file8_in_name, file8_in_name + '_old')

print(
    '\nBackup saved:',
    file8_in_name + '_old'
)

file8_in = open(
    file8_in_name,
    'w',
    encoding='UTF-8'
)

file8_in.write(
      '! description: domains_white_list\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/domains_white_list\n'
)

file8_in.writelines(line + '\n' for line in list8)
file8_in.close()

#</ open file8_in file and write sorted deduped domains_white_list >

list3 = list(filter(None, sorted(set(list3) - set(list8))))

print('\n<domains_white_list> loaded and applied')

print(
    '       ',
    '{:,}'.format(len(list3)),
    'domains kept'
    )

# </get domains white list from file, dedup, sort and substract from domains filters>

# <deflat domain filters >

print('\ndeflating domain filters, pass 1 / 2:')

counter = Value('d', 0)
t0 = time()
counter_max = len(list3)

def f_deflat_domain(line) :

    global iana_sld
    global list8

    if not(re.sub(r'^[^\.]*\.', '', line) in iana_sld) :
        if not(re.sub(r'^[^\.]*\.', '', line) in list8) :
            line = re.sub(r'^[^\.]+\.', '', line)

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

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list3 = pool.map(f_deflat_domain, list3)                                        # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list3 = list(filter(None, sorted(set(list3))))

print(
    '        ',
    '{:,}'.format(len(list3)),
    'domains kept',
    '                                       ',
    )

print('deflating domain filters, pass 2 / 2:')

counter = Value('d', 0)
t0 = time()
counter_max = len(list3)

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list3 = pool.map(f_deflat_domain, list3)                                        # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list3 = pool.map(f_clean_domains_2, list3)                                      # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list3 = list(filter(None, sorted(set(list3) - set(iana_sld))))                  # <remove IANA sld root domains />

list3b = [item for item in list3 if item[0] == '-']

list3 = list(filter(None, sorted(set(list3) - set(list3b))))
list2 = list(filter(None, sorted(set(list2) | set(list3b))))

del list3b

print(
    '        ',
    '{:,}'.format(len(list3)),
    'domains kept',
    '                                       ',
    )   

# </deflat domain filters >

list2 = list(filter(None, sorted(set(list2) | set(list3))))                     # <joint list2, list3 />

print()

print(
    '       ',
    '{:,}'.format(len(list2)),
    'filters kept',
    '\n'
    )

# <dedup filter if filter$important is present >

print('dedup filter if filter($|,)important present', sep = '')

def f_dedup_important(line) :

    global list2

    if re.search(r'[\$\,]important$', line) :
        line = re.sub(r'[\$\,]important$', '', line)
    else :
        line = ''

    return line

pool = ThreadPool(thr)                                                          # <make the pool of workers />
list2s = pool.map(f_dedup_important, list2)                                     # <execute function by multi-threading />
pool.close()                                                                    # <close the pool and wait for the work to finish />
pool.join()

list2 = [line for line in list2 if not re.search(r'^[a-z0-9]*$', line)]

list2 = list(filter(None, sorted(set(list2) - set(list2s))))                    # <remove redundant filters />
del(list2s)

print(
    '        ',
    '{:,}'.format(len(list2)),
    'filters remaining after compilation'
)

# </dedup filter if filter$important is present >

# <process filter list>

# <save a backup renamed *_old; overwrite if exists>

filelist = os.listdir('.')

if file2_out_name + '_old' in filelist : os.remove(file2_out_name + '_old')
if file2_out_name in filelist : os.rename(file2_out_name, file2_out_name + '_old')

print(
    '\nBackup saved:',
    file2_out_name + '_old\n'
)

# </save a backup renamed *_old; overwrite if exists>

# <write main output>

print('Added generic filters and exceptions\n')

list2.append('/^(?:[-\w]+\.)*[-_0-9]+\.[a-z]+(\.[a-z]+)?/')                     # <add filter to block [-_/\.0-9]+\.[a-z]+ domains />

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

list2.append('@@*$inline-font,domain=youtube.com')
list2.append('@@*$inline-script,domain=20minutos.es')
list2.append('@@*$inline-script,domain=amazon.com')
list2.append('@@*$inline-script,domain=amazon.es')
list2.append('@@*$inline-script,domain=backmarket.es')
list2.append('@@*$inline-script,domain=bbc.com')
list2.append('@@*$inline-script,domain=bloomberg.com')
list2.append('@@*$inline-script,domain=dw.com')
list2.append('@@*$inline-script,domain=gitlab.com')
list2.append('@@*$inline-script,domain=iberia.com')
list2.append('@@*$inline-script,domain=ikea.com')
list2.append('@@*$inline-script,domain=ikea.es')
list2.append('@@*$inline-script,domain=imf.org')
list2.append('@@*$inline-script,domain=investing.com')
list2.append('@@*$inline-script,domain=linkedin.com')
list2.append('@@*$inline-script,domain=meteoblue.com')
list2.append('@@*$inline-script,domain=morningstar.es')
list2.append('@@*$inline-script,domain=open-vsx.org')
list2.append('@@*$inline-script,domain=startpage.com')
list2.append('@@*$inline-script,domain=wired.com')
list2.append('@@*$inline-script,domain=workdbank.com')
list2.append('@@*$xhr,domain=gitlab.com')
list2.append('@@*$xhr,domain=linkedin.com')
list2.append('@@*$xhr,domain=meteoblue.com')
list2.append('@@*$xhr,domain=open-vsx.org')
list2.append('@@||accounts.google.com$inline-font,domain=google.com|youtube.com')
list2.append('@@||cloudfront.net^$script,domain=backmarket.es')
list2.append('@@||google.com^$inline-font,1p')
list2.append('@@||google.com^$inline-script,1p')
list2.append('@@||googlevideo.com^$xhr,domain=youtube.com')
list2.append('@@||gstatic.com^$inline-font,domain=google.com|youtube.com')
list2.append('@@||gstatic.com^$xhr,domain=google.com|youtube.com')
list2.append('@@||ikea.com/*/header-footer/menu-products.html$xhr,1p')
list2.append('@@||licdn.com^$xhr,domain=linkedin.com')
list2.append('@@||linkedin.com^$removeparam=/redir/')
list2.append('@@||mail.google.com^$removeparam=view')
list2.append('@@||mail.google.com^$xhr,1p')
list2.append('@@||meteoblue.com^$removeparam=/callback/i')
list2.append('@@||meteoblue.com^$removeparam=/metric/i')
list2.append('@@||music.youtube.com^$inline-script,domain=music.youtube.com')
list2.append('@@||music.youtube.com^$xhr,domain=music.youtube.com')
list2.append('@@||openstreetmap.org^$xhr,1p')
list2.append('@@||youtube.com/youtubei/v1/next$xhr,1p')
list2.append('@@||youtube.com/youtubei/v1/player$xhr,1p')
list2.append('@@||youtube.com/youtubei/v1/search$xhr,1p')
list2.append('@@||youtube.com^$xhr,1p')

list2.append('*##+js(json-prune, actionProto)')
list2.append('*##+js(json-prune, ad_fallback)')
list2.append('*##+js(json-prune, ad_id)')
list2.append('*##+js(json-prune, adEnabled)')
list2.append('*##+js(json-prune, adPlacements)')
list2.append('*##+js(json-prune, ads)')
list2.append('*##+js(json-prune, adsbygoogle)')
list2.append('*##+js(json-prune, adService)')
list2.append('*##+js(json-prune, adSlots)')
list2.append('*##+js(json-prune, bgChallenge)')
list2.append('*##+js(json-prune, botguardData)')
list2.append('*##+js(json-prune, breaks)')
list2.append('*##+js(json-prune, challenge)')
list2.append('*##+js(json-prune, consent)')
list2.append('*##+js(json-prune, Consent)')
list2.append('*##+js(json-prune, ContentBreaks)')
list2.append('*##+js(json-prune, cookie)')
list2.append('*##+js(json-prune, Cookie)')
list2.append('*##+js(json-prune, creation)')
list2.append('*##+js(json-prune, data)')
list2.append('*##+js(json-prune, enforcementMesageVewMdel)')
list2.append('*##+js(json-prune, enqueueTimeSec)')
list2.append('*##+js(json-prune, expiration)')
list2.append('*##+js(json-prune, headers)')
list2.append('*##+js(json-prune, isAd)')
list2.append('*##+js(json-prune, key)')
list2.append('*##+js(json-prune, legacyImportant)')
list2.append('*##+js(json-prune, pause_ads)')
list2.append('*##+js(json-prune, playerAds)')
list2.append('*##+js(json-prune, playerconfig)')
list2.append('*##+js(json-prune, playerConfig)')
list2.append('*##+js(json-prune, playerResponse)')
list2.append('*##+js(json-prune, plg_system_ochaddads)')
list2.append('*##+js(json-prune, postParams)')
list2.append('*##+js(json-prune, promotext)')
list2.append('*##+js(json-prune, responseContext)')
list2.append('*##+js(json-prune, retryScheduleIndex)')
list2.append('*##+js(json-prune, rootActionId)')
list2.append('*##+js(json-prune, shortsAdsRenderer)')
list2.append('*##+js(json-prune, showAds)')
list2.append('*##+js(json-prune, ssapConfig)')
list2.append('*##+js(json-prune, testhide)')
list2.append('*##+js(json-prune, trackingId)')
list2.append('*##+js(json-prune, X-YouTube-Ad-Signals)')

list2.append('*##+js(set, adPlacements, undefined)')
list2.append('*##+js(set, adsbygoogle, undefined)')
list2.append('*##+js(set, adSlots, undefined)')
list2.append('*##+js(set, consent, undefined)')
list2.append('*##+js(set, Consent, undefined)')
list2.append('*##+js(set, cookie, undefined)')
list2.append('*##+js(set, Cookie, undefined)')
list2.append('*##+js(set, enforcementMesageVewMdel, undefined)')
list2.append('*##+js(set, playerAds, undefined)')
list2.append('*##+js(set, playerconfig, undefined)')
list2.append('*##+js(set, playerConfig, undefined)')

list2.append('*$removeparam=/^((?!formats|profile).)*/,badfilter')
list2.append('*$removeparam=id,badfilter')
list2.append('*$removeparam=/^((?!smil|formats).)*/,badfilter')
list2.append('*$removeparam=source,badfilter')
list2.append('*$removeparam=v,badfilter')

list2.append('/^([^\.]*\.)*[\d]+\.([a-z]{2,}\.)?[a-z]{2,}/$important')

list2 = list(filter(None, sorted(set(list2))))

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

# </write domain type filters>

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

# </write extracted url type filters>

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

print(
    'Total compilation time: ',
    '{:.0f}'.format((time() - t_start) / 60), '\' elapsed',
    '\n',
    sep = '',
)

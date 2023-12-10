'''
Compile a single deduplicated block list from url sources
'''

# <product backlog>

# <sprint #1: dedup urls/>
# <sprint #2: apply multicore/>
# <sprint #3: apply whitelisting to cosmetic filters/>
# <sprint #4: check for mismatching () [] {} />

# </product backlog>

import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import re                                                                       # <regex cpapbilities />
import requests                                                                 # <get files using url />
import tqdm                                                                     # <progress bar />

# <settings>

file1_in_name  = 'filter_sources'
file2_out_name = 'compiled_block_list'
file3_out_name = 'ipfire_domain_block_list'
file4_out_name = 'ipfire_url_block_list'
file5_out_name = 'ipfire_regex_block_list'
file7_out_name = 'ublock_list_except_domains'
file8_in_name  = 'domains_white_list'
file9_in_name  = 'regex_white_list'
proxy_servers  = {'https': '', 'http': ''}
proxy_servers_alt  = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}

# </settings>

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

dom_sw = input('Enter <y> to include domain deflation : ')

# <test direct connection to internet>

try:
    r = requests.get('https://google.com', timeout = 5, proxies = proxy_servers)
except:
    print('\nUsing alt proxy servers.')
    proxy_servers  = proxy_servers_alt

# </test direct connection to internet>

# <get filter url sources from file, dedup and sort>

list1 = [line.strip() for line in open(file1_in_name, encoding='UTF-8')]        # <populate source lists />
list1 = [re.sub(r'^ *!.*', '', line) for line in list1]                         # <remove ! comments' />
list1 = sorted([line for line in list1 if line.strip() != ''])                  # <remove empty lines />

# </get filter url sources from file, dedup and sort>

# <dump sources to list>

list2 = set()                                                                   # <set() type ensures no elements' duplication />
i     = 1                                                                       # <counter for uncommented sources />

for line in list1 :
    print(
        '\n',
        'reading source',
        '{:3.0f}'.format(i),
        '/',
        len(list1),
        ':',
        line
    )
    i += 1
    response = requests.get(line, proxies=proxy_servers)
    if (response.status_code) :
        list2.update(response.text.split('\n'))
        print(
            '                          ',
            '{:,}'.format(len(list2)),
            'cumulated filters'
        )

# </dump sources to list>

iana_tld = set()

response = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt', proxies=proxy_servers)
if (response.status_code) :
    iana_tld.update(response.text.split('\n'))

iana_tld = [re.sub(r'^#.*', '', line).strip() for line in iana_tld]             # <remove # comments' />
iana_tld = [line.lower() for line in iana_tld if line != '']                    # <remove empty lines />

print('\n IANA top level domains (TLD) list loaded')

# <process filter list>

print(
    '\n',
    'Applying transforming filters\n',
    '-----------------------------\n'
)

list5 = []

# <transforming loop>

print(' 1/20 : remove leading/trailing/dup spaces ')

list2 = [re.sub(r'\t', ' ', line) for line in list2]                            # <replace tab with space  />
list2 = [re.sub(r' +', ' ', line).strip() for line in list2]                    # <dedup spaces and remove leading/trailing spaces />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 2/20 : remove comments ')

list2 = [re.sub(r'^ *[!\[\{].*', '', line) for line in list2]                   # <remove !comment [comment] {comment} />
list2 = [re.sub(r'^ *#(?![\?|@|#]).*', '', line) for line in list2]             # <remove #comment; preserve cosmetics and exceptions />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 3/20 : clean dns filters ')

list2 = [re.sub(r'^0\.0\.0\.0 ', '', line) for line in list2]                   # <remove leading 0.0.0.0 (dns style filter) />
list2 = [re.sub(r'^127\.0\.0\.1 ', '', line) for line in list2]                 # <remove leading 127.0.0.1 (dns style filter) />
list2 = [re.sub(r'^\:+1 ', '', line) for line in list2]                         # <remove leading ::1 (dns style filter) />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 4/20 : remove items containing % about: $badfilter localhost; remove http: IP4 IP6 :port/ www ||')

list2 = [line for line in list2 if not(re.search(r'\%', line))]                 # <remove items comprising % >
list2 = [line for line in list2 if not(re.search(r'about\:', line))]            # <remove items comprising about: >
list2 = [line for line in list2 if not(re.search(r'[,\$]badfilter', line))]     # <remove items comprising $badfilter />
list2 = [line for line in list2 if not(re.search(r'localhost', line))]          # <remove items containing localhost />
list2 = [re.sub(r'^[^a-z]+$', '', line) for line in list2]                      # <remove filters comprised only by simbols and numbers (includes IP4 addresses) />
list2 = [line for line in list2 if not(re.search(r'\:+', line))]                # <remove IP6 addresses :: />
list2 = [re.sub(r'^\:[0-9]+/', '/', line) for line in list2]                    # <replace leading :port/ with / />
list2 = [re.sub(r'https?\:/*', '', line) for line in list2]                     # <remove http:/* />
list2 = (
    [re.sub(r'[\|\^]', '', line) if re.search(r'^\|+.*\^.*$', line)             # <remove || ^ from ||domain.tld^ />
    else line
    for line in list2]
)
list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 5/20 : apply lower case except for cosmetics and regex')
list2 = [line if re.search(r'[#\\]', line) else line.lower() for line in list2] # <apply lower case except cosmetics and regex />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />

# <segregate regex filters >

list2 = [re.sub(r'^/([-\.\+\!\~/\w]+)/$', r'/\1/*', line) for line in list2]    # <add trailing * for /@/ url filters (false regex) />
list2 = [line for line in list2 if not(re.search(r'^.*\\/$', line))]            # <remove broken regex (bad termination) />

list5 = [line for line in list2 if re.search(r'^/.+/(?:\$important)?$', line)]
list2  = set(list2) - set(list5)

# </segregate regex filters >

print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 6/20 : generalize cosmetic filters (*##) and exceptions (*#@ *#? *@@) ')

list2 = [re.sub(r'^.*(?=\#[\#\?])', '*', line) for line in list2]               # <generalize *## *#? />
list2 = [re.sub(r'^.*(?=[\#\@]\@)', '*', line) for line in list2]               # <generalize *#@ *@@ />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 7/20 : remove cosmetic filters (##) and exceptions (@@) except *##:')   # <currently discarded; consider processing (future sprints?)/>

list2 = [re.sub(r'^\*?\#\#(?!\:).*', '', line) for line in list2]               # <remove cosmetic filters except ##: />
list2 = [re.sub(r'^\*?\#[\@|\?].*', '', line) for line in list2]                # <remove #@ #? exceptions />
list2 = [re.sub(r'^\*?\@\@.*', '', line) for line in list2]                     # <remove @@ exceptions />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 8/20 : split urls with $ domain= ')

list2s = [line for line in list2 if re.search(r'\$.*domain=', line)]            # <get urls with $ domain= '/>

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = (
    [re.sub(r',.*', '', re.sub(r'^.*domain=', '', line)) for line in list2s] +  # <isolate domain list part/>
    [re.sub(r'\$.*', '', line) for line in list2s]                              # <isolate url part/>
)

list2s = [line.split('|') for line in list2s]                                   # <flatten list'/>
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
del(list2s)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 9/20 : remove domain= denyallow= and keep the related domains')

list2s = (
    [line for line in list2 if re.search(r'.*domain=', line)] +                 # <select *$ filters />
    [line for line in list2 if re.search(r'.*denyallow=', line)]                # <select denyallow filters />
)

list2 = set(list2) - set(list2s)                                                # <segregate selected filters'/>

list2s = [re.sub(r'.*domain=', '', line).strip() for line in list2s]            # <remove leading .*domain=/>
list2s = [re.sub(r'.*denyallow=', '', line).strip() for line in list2s]         # <remove leading .*denyallow=/>
list2s = [re.sub(r',.*$', '', line).strip() for line in list2s]                 # <remove trailing .*,.*/>

list2s = [line.split('|') for line in list2s if len(line) > 0]                  # <flatten list'/>
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
del(list2s)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('10/20 : split , separated domains ')

list2   = [re.sub(r'^,', '', line).strip() for line in list2]                   # <remove leading , />
list2   = [re.sub(r',$', '', line).strip() for line in list2]                   # <remove trailing , />
list2s = [line for line in list2 if re.search(r'\,', line)]                     # <remove , separated domains />
list2s = [line for line in list2s if not(re.search(r'[\$\&]', line))]           # <exclude $ & filters />

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = [line.split(',') for line in list2s]
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
del(list2s)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

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

    print('11/20 : clean up leading symbols numbers prefix etc')

    list2 = [re.sub(r'^[_\W0-9]*(?=[/\.\$])', '', line) for line in list2]      # <remove leading symbols and numbers preceding / . $ />
    list2 = [re.sub(r'^[/\.]?[-\*\w](?=[/\.\$])', '', line) for line in list2]  # <remove leading single -_* a-z0-9 char preceding / . $ />
    list2 = [re.sub(r'^\.(?=\*)', '', line) for line in list2]                  # <remove leading . if followed by * />
    list2 = [re.sub(r'^[/\.\=\?]?\$', '*$', line) for line in list2]            # <replace leading $ /$ .$ =$ ?$ with *$ />
    list2 = [re.sub(r'^\.?[-\*\w]+/', '/', line) for line in list2]             # <replace leading @/ with / />
    list2 = [re.sub(r'^/([-\.\+\!\~/\w]+)/$', r'/\1/*', line) for line in list2]    # <add trailing * for /@/ url filters (false regex) />
    list2 = [re.sub(r'www[0-9]*\.', '', line) for line in list2]                # <remove www#. />

#    list2 = [re.sub(r'^[/\.]?ajax\*?(?=[/\.])', '', line) for line in list2]    # <remove leading ajax />
#    list2 = [re.sub(r'^[/\.]?api\*?(?=[/\.])', '', line) for line in list2]     # <remove leading api />
#    list2 = [re.sub(r'^[/\.]?apple\*?(?=[/\.])', '', line) for line in list2]   # <remove leading apple />
#    list2 = [re.sub(r'^[/\.]?app\*?(?=[/\.])', '', line) for line in list2]     # <remove leading app />
#    list2 = [re.sub(r'^[/\.]?assets?\*?(?=[/\.])', '', line) for line in list2] # <remove leading asset />
#    list2 = [re.sub(r'^[/\.]?attachments?\*?(?=[/\.])', '', line) for line in list2]    # <remove leading attachment />
#    list2 = [re.sub(r'^[/\.]?brands?\*?(?=[/\.])', '', line) for line in list2] # <remove leading brand(s) />
#    list2 = [re.sub(r'^[/\.]?build\*?(?=[/\.])', '', line) for line in list2]   # <remove leading build />
#    list2 = [re.sub(r'^[/\.]?business\*?(?=[/\.])', '', line) for line in list2]        # <remove leading business />
#    list2 = [re.sub(r'^[/\.]?catalog\*?(?=[/\.])', '', line) for line in list2] # <remove leading catalog />
#    list2 = [re.sub(r'^[/\.]?cdn(\-cgi)?(?=[/\.])', '', line) for line in list2]        # <remove leading cdn(-cgi) />
#    list2 = [re.sub(r'^[/\.]?center\*?(?=[/\.])', '', line) for line in list2]  # <remove leading center />
#    list2 = [re.sub(r'^[/\.]?cgi\-bin\*?(?=[/\.])', '', line) for line in list2]        # <remove leading cgi-bin />
#    list2 = [re.sub(r'^[/\.]?comm?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading com(m) />
#    list2 = [re.sub(r'^[/\.]?common\*?(?=[/\.])', '', line) for line in list2]  # <remove leading common />
#    list2 = [re.sub(r'^[/\.]?contents?\*?(?=[/\.])', '', line) for line in list2]       # <remove leading content(s) />
#    list2 = [re.sub(r'^[/\.]?core\*?(?=[/\.])', '', line) for line in list2]    # <remove leading core />
#    list2 = [re.sub(r'^[/\.]?creatives?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading creative(s) />
#    list2 = [re.sub(r'^[/\.]?css\*?(?=[/\.])', '', line) for line in list2]     # <remove leading css />
#    list2 = [re.sub(r'^[/\.]?custom\*?(?=[/\.])', '', line) for line in list2]  # <remove leading custom />
#    list2 = [re.sub(r'^[/\.]?data\*?(?=[/\.])', '', line) for line in list2]    # <remove leading data />
#    list2 = [re.sub(r'^[/\.]?default\*?(?=[/\.])', '', line) for line in list2] # <remove leading default />
#    list2 = [re.sub(r'^[/\.]?ebay\*?(?=[/\.])', '', line) for line in list2]    # <remove leading ebay />
#    list2 = [re.sub(r'^[/\.]?ext\*?(?=[/\.])', '', line) for line in list2]     # <remove leading ext />
#    list2 = [re.sub(r'^[/\.]?files?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading file(s) />
#    list2 = [re.sub(r'^[/\.]?forum\*?(?=[/\.])', '', line) for line in list2]   # <remove leading forum />
#    list2 = [re.sub(r'^[/\.]?home?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading home />
#    list2 = [re.sub(r'^[/\.]?html?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading html />
#    list2 = [re.sub(r'^[/\.]?ima?ge?(ne)?s?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading image />
#    list2 = [re.sub(r'^[/\.]?jquery\*?(?=[/\.])', '', line) for line in list2]  # <remove leading jquery />
#    list2 = [re.sub(r'^[/\.]?js\*?(?=[/\.])', '', line) for line in list2]      # <remove leading js />
#    list2 = [re.sub(r'^[/\.]?libs?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading lib(s) />
#    list2 = [re.sub(r'^[/\.]?min\*?(?=[/\.])', '', line) for line in list2]     # <remove leading min />
#    list2 = [re.sub(r'^[/\.]?modules?\*?(?=[/\.])', '', line) for line in list2]    # <remove leading module(s) />
#    list2 = [re.sub(r'^[/\.]?(multi)?media\*?(?=[/\.])', '', line) for line in list2]   # <remove leading (multi)media />
#    list2 = [re.sub(r'^[/\.]?news?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading new(s) /
#    list2 = [re.sub(r'^[/\.]?pics?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading pic(s) /
#    list2 = [re.sub(r'^[/\.]?plugins?\*?(?=[/\.])', '', line) for line in list2]        # <remove leading plugin(s) /
#    list2 = [re.sub(r'^[/\.]?public\*?(?=[/\.])', '', line) for line in list2]  # <remove leading public />
#    list2 = [re.sub(r'^[/\.]?resources?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading resource(s) />
#    list2 = [re.sub(r'^[/\.]?scripts?\*?(?=[/\.])', '', line) for line in list2]        # <remove leading script(s) />
#    list2 = [re.sub(r'^[/\.]?scr\*?(?=[/\.])', '', line) for line in list2]     # <remove leading src />
#    list2 = [re.sub(r'^[/\.]?sdk\*?(?=[/\.])', '', line) for line in list2]     # <remove leading sdk />
#    list2 = [re.sub(r'^[/\.]?sites?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading site(s) />
#    list2 = [re.sub(r'^[/\.]?source\*?(?=[/\.])', '', line) for line in list2]  # <remove leading source />
#    list2 = [re.sub(r'^[/\.]?_?statics?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading static />
#    list2 = [re.sub(r'^[/\.]?styles?\*?(?=[/\.])', '', line) for line in list2] # <remove leading style(s) />
#    list2 = [re.sub(r'^[/\.]?temp\*?(?=[/\.])', '', line) for line in list2]    # <remove leading temp />
#    list2 = [re.sub(r'^[/\.]?themes?\*?(?=[/\.])', '', line) for line in list2] # <remove leading theme(s) />
#    list2 = [re.sub(r'^[/\.]?uploads?.?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading uploads />
#    list2 = [re.sub(r'^[/\.]?videos?\*?(?=[/\.])', '', line) for line in list2] # <remove leading video(s) />
#    list2 = [re.sub(r'^[/\.]?v.?\*?(?=[/\.])', '', line) for line in list2]     # <remove leading v />
#    list2 = [re.sub(r'^[/\.]?web(resources?)?\*?(?=[/\.])', '', line) for line in list2]    # <remove leading web(resource(s)) />
#    list2 = [re.sub(r'^[/\.]?wp\-content\*?(?=[/\.])', '', line) for line in list2]     # <remove leading wp-content />
#    list2 = [re.sub(r'^[/\.]?www\*?(?=[/\.])', '', line) for line in list2]     # <remove leading www />
#    list2 = [re.sub(r'^\.?aspx?\??(?![a-z0-9])', '*', line).strip() for line in list2]  # <replace leading asp with * >
#    list2 = [re.sub(r'^\.?cgi\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading cgi with * >
#    list2 = [re.sub(r'^\.?cfm\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading cfm with * >
#    list2 = [re.sub(r'^\.?gif\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading gif with * >
#    list2 = [re.sub(r'^\.?html?\??(?![a-z0-9])', '*', line).strip() for line in list2]  # <replace leading htm with * >
#    list2 = [re.sub(r'^\.?jpg\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading jpg with * >
#    list2 = [re.sub(r'^[/\.]?js/', '/', line) for line in list2]                # <replace leading js/ with / />
#    list2 = [re.sub(r'^\.?js\??(?![a-z0-9])', '*', line).strip() for line in list2]     # <replace leading js with * >
#    list2 = [re.sub(r'^\.?mp[0-9]\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading mp* with * >
#    list2 = [re.sub(r'^\.?php\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading php with * >
#    list2 = [re.sub(r'^\.?png\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading png with * >
#    list2 = [re.sub(r'^\.?tiff\??(?![a-z0-9])', '*', line).strip() for line in list2]   # <replace leading tiff with * >

    list2 = sorted([line for line in list2 if len(line) > 1])                   # <remove line if length < 2 />
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

    print('12/20 : clean up trailing symbols numbers suffix $filters etc')

    list2 = [re.sub(r'[\^\|\=]\$', '$', line).strip() for line in list2]        # <replace ^$ |$ =$ with $ />
    list2 = [re.sub(r'\|+\$', '$', line).strip() for line in list2]             # <replace |$ with $ />
    list2 = [re.sub(r'[#,\~\|\^\?\=\&]+$', '', line).strip() for line in list2] # <remove trailing # , ~ | ^ ? = & />
    list2 = [re.sub(r'(?<!/)\*$', '', line).strip() for line in list2]          # <remove trailing * except /url/* />
    list2 = [re.sub(r'\.\*$', '.', line).strip() for line in list2]             # <replace trailing .* with . />
    list2 = [re.sub(r'\*\.$', '', line).strip() for line in list2]              # <remove trailing *. />
    list2 = [re.sub(r'\.cgi\??$', '.', line) for line in list2]                 # <remove trailing .cgi? />
    list2 = [re.sub(r'\.ashx\??$', '.', line) for line in list2]                # <remove trailing .ashx? />
    list2 = [re.sub(r'\.asp\??$', '.', line) for line in list2]                 # <remove trailing .asp? />
    list2 = [re.sub(r'\.?html?\??$', '.', line) for line in list2]              # <remove trailing .html? />
    list2 = [re.sub(r'\.jpe?g\??$', '.', line) for line in list2]               # <remove trailing .jp(e)g? />
    list2 = [re.sub(r'\.php\??$', '.', line) for line in list2]                 # <remove trailing .php? />
    list2 = [re.sub(r'\.png\??$', '.', line) for line in list2]                 # <remove trailing .png? />
    list2 = [re.sub(r'\.svg\??$', '.', line) for line in list2]                 # <remove trailing .svg? />
    list2 = [re.sub(r'\.js\??[^\./]*$', '.js', line) for line in list2]         # <clean up trailing .js />
    list2 = [re.sub(r'(^[^#]{2,})\$[-~,=a-z0-9]*$(?<!/)(?<!important)', r'\1', line) for line in list2]    # <remove specific trailing $ filters except *$ or ending with important />
    list2 = [re.sub(r'\??\*\=.*$', '', line).strip() for line in list2]         # <remove trailing ?*=... />

    list2 = sorted([line for line in list2 if len(line) > 1])                   # <remove line if length < 2 />
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

    print('13/20 : split domain and url ')

    list2s = [line for line in list2 if re.search(r'^[-\.\w]+\.[a-z]+/.*', line)]   # <get domains with url'/>

    list2 = set(list2) - set(list2s)                                            # <segregate removed filters'/>

    list2s = (
        [re.sub(r'^[-\.\w]+/', '/', line) for line in list2s] +                 # <isolate url part/>
        [re.sub(r'/.*$', '', line) for line in list2s]                          # <isolate domains part/>
    )

    list2 = sorted(set(list2) | set(list2s))                                    # <join retrieved domains to main list'/>
    list2 = sorted([line for line in list2 if len(line) > 1])                   # <remove line if length < 2 />
    del(list2s)
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

    print('14/20 : clean up urls')

    list2 = [re.sub(r'\*+', '*', line).strip() for line in list2]               # <dedup * />
    list2 = [re.sub(r'\.+', '.', line).strip() for line in list2]               # <dedup . />
    list2 = [re.sub(r'/+', '/', line).strip() for line in list2]                # <dedup / />
    list2 = [re.sub(r'^.*/\*/', '/', line) for line in list2]                   # <replace any url preceded by /*/ (included) with / />

#    list2 = [re.sub(r'^[_\W]?a?[^d]?[_\W]?\*?$', '', line) for line in list2]   # <remove 2 ax pd sequence filter />
#    list2 = [re.sub(r'^[_\W]?p?[^x]?[_\W]?\*?$', '', line) for line in list2]   # <remove 2 ax pd sequence filter />
#    list2 = [re.sub(r'^[_\W]?[^a]?d?[_\W]?\*?$', '', line) for line in list2]   # <remove 2 ax pd sequence filter />
#    list2 = [re.sub(r'^[_\W]?[^p]?x?\*?$', '', line) for line in list2]         # <remove 2 ax pd sequence filter />

    list2 = sorted([line for line in list2 if len(line) > 1])                   # <remove line if length < 2 />
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

# <transforming loop/>

print('15/20 : split space separated domains ')

list2s = [line for line in list2 if re.search(r' ', line) and not(re.search(r'[\$\&\#]', line))]    # <remove space separated domains />

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = [line.split(' ') for line in list2s]                                   # <flatten list'/>
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
del(list2s)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('16/20 : remove lines leaded by ! # + & ? ^ : ; @ and @.exe @.gif @.rar @.zip')

list2 = [re.sub(r'^\*?\^.*', '', line) for line in list2]                       # <remove ^ leaded lines />
list2 = [re.sub(r'^\|\|', '', line) for line in list2]                          # <remove leading || />
list2 = [re.sub(r'^\!.*', '', line) for line in list2]                          # <remove ! leaded lines />
list2 = [re.sub(r'^#.*', '', line) for line in list2]                           # <remove # leaded lines />
list2 = [re.sub(r'^[/\*]?\+.*', '', line) for line in list2]                    # <remove + leaded lines />
list2 = [re.sub(r'^\*?\&.*', '', line) for line in list2]                       # <remove & leaded lines />
list2 = [re.sub(r'^\*?\?.*', '', line) for line in list2]                       # <remove ? leaded lines />
list2 = [re.sub(r'^\*?\:.*', '', line) for line in list2]                       # <remove : leaded lines />
list2 = [re.sub(r'^\*?\;.*', '', line) for line in list2]                       # <remove ; leaded lines />
list2 = [re.sub(r'^\*?\".*', '', line) for line in list2]                       # <remove " leaded lines />
list2 = [re.sub(r'^[/\*]?\@.*', '', line) for line in list2]                    # <remove @ leaded lines />
list2 = [re.sub(r'^.*\.gif$', '.gif', line) for line in list2]                  # <enforce .gif filter />
list2 = [re.sub(r'^.*\.rar$', '', line) for line in list2]                      # <remove @.rar filters />
list2 = [re.sub(r'^.*\.zip$', '', line) for line in list2]                      # <remove @.zip filters />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('17/20 : arrange *$ filters; keep beacon csp inline-font inline-script object other ping popunder script websocket xhr ')

list2 = [re.sub(r'^\*\$\~?1p.*', '', line) for line in list2]                   # <remove *$1p />
list2 = [re.sub(r'^\*\$\~?3p.*', '', line) for line in list2]                   # <remove *$3p />
list2 = [re.sub(r'^\*\$\~?third\-party.*', '', line) for line in list2]         # <remove *$3p />
list2 = [re.sub(r'^\*\$\~?all.*', '', line) for line in list2]                  # <remove *$all />
list2 = [re.sub(r'^\*\$\~?beacon.*', '*$beacon', line) for line in list2]       # <enforce *$beacon />
list2 = [re.sub(r'.*\$csp.*', '*$csp=all', line) for line in list2]             # <enforce *$csp=all />
list2 = [re.sub(r'^\*\$\~?css.*', '', line) for line in list2]                  # <remove *$css />
list2 = [re.sub(r'^\*\$\~?stylesheet.*', '', line) for line in list2]           # <remove *$css />
list2 = [re.sub(r'^\*\$\~?(sub)?doc(ument)?.*', '', line) for line in list2]    # <remove *$(sub)doc />
list2 = [re.sub(r'^\*\$\~?from.*', '', line) for line in list2]                 # <remove *$from />
list2 = [re.sub(r'^\*\$\~?image.*', '', line) for line in list2]                # <remove *$image />
list2 = [re.sub(r'^\*\$\~?inline\-font.*', '*$inline-font', line) for line in list2]        # <enforce *$inline-font />
list2 = [re.sub(r'^\*\$\~?inline\-script.*', '*$inline-script', line) for line in list2]    # <enforce *$inline-script />
list2 = [re.sub(r'^\*\$\~?media.*', '', line) for line in list2]                # <remove *$media />
list2 = [re.sub(r'^\*\$\~?object.*', '*$object', line) for line in list2]       # <enforce *$object />
list2 = [re.sub(r'^\*\$\~?other.*', '*$other', line) for line in list2]         # <enforce *$other />
list2 = [re.sub(r'^\*\$\~?ping.*', '*$ping', line) for line in list2]           # <enforce *$ping />
list2 = [re.sub(r'^\*\$\~?popup.*', '', line) for line in list2]                # <remove *$popup />
list2 = [re.sub(r'^\*\$\~?popunder.*', '*$popunder', line) for line in list2]   # <enforce *$popunder />
list2 = [re.sub(r'^\*\$\~?script.*', '*$script', line) for line in list2]       # <enforce *$script />
list2 = [re.sub(r'^\*\$\~?rewrite.*', '', line) for line in list2]              # <remove *$rewrite />
list2 = [re.sub(r'^\*\$\~?websocket.*', '*$websocket', line) for line in list2] # <enforce *$websocket />
list2 = [re.sub(r'^\*\$\~?xhr.*', '*$xhr', line) for line in list2]             # <enforce *$xhr />
list2 = [re.sub(r'^\*\$\~?xmlhttprequest.*', '*$xhr', line) for line in list2]  # <enforce *$xhr />
list2 = [re.sub(r'^\*\$important.*', '', line) for line in list2]               # <remove *$important filters />
list2 = [re.sub(r'^\*\$.*\.js$', '', line) for line in list2]                   # <remove *$...js filters />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('18/20 : remove broken filters and fix false regex ')

list2 = [line for line in list2 if re.search(r'^[^\(\)\[\]\{\}\~]', line)]      # <remove broken filters; improve this filter />
list2 = [line for line in list2 if not(re.search(r'^.*\([^\)]*$', line))]       # <remove broken filters; improve this filter for multiple () />
list2 = [line for line in list2 if not(re.search(r'^.*\[[^\]]*$', line))]       # <remove broken filters; improve this filter for multiple [] />
list2 = [line for line in list2 if not(re.search(r'^.*\{[^\}]*$', line))]       # <remove broken filters; improve this filter for multiple {} />
list2 = [line for line in list2 if not(re.search(r'^/.*[\[\\].*[^/]$', line))]  # <remove broken filters (unterminated regex) />

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('19/20 : apply regex_white_list rules')

# <get regex white list from file, dedup, sort and clean up filters>

list9 = [line.strip() for line in open(file9_in_name, encoding='UTF-8')]        # <populate list; remove leading/trailing spaces />
list9 = [re.sub(r'^ *!.*', '', line) for line in list9]                         # <remove ! comments' />
list9 = [line for line in list9 if line != '']                                  # <remove empty lines />
list9 = list9 + ['/[_\W]*' + tld + '[_\W]*/' for tld in iana_tld]               # <enforce tld whitelisting />

list2s = [line for line in list2 if re.search(r'^.*[\#|\@|\$].*$', line)]       # <segregate *#(cosmetics) *@(exceptions) *$(removeparam and others) filters/>
list2  = set(list2) - set(list2s)

for pattern in tqdm.tqdm(list9) :
    try :
        pattern = re.compile(r'' + (pattern[: -1] + '(?:\$important)?$'))
        list2 = [pattern.sub(r'', line) for line in list2]                          # <remove spurious filter from main list based on regex-white_list/>
        list5 = [pattern.sub(r'', line) for line in list5]                          # <remove spurious filter from regex list based on regex-white_list />
    except :
        print('Error found; check for ' + pattern + ' pattern in regex_white_list')

print()

# </get regex white list from file, dedup, sort and clean up filters>

list2 = sorted([line for line in list2 if len(line) > 1])                       # <remove line if length < 2 />
list5 = sorted([line for line in list5 if len(line) > 1])                       # <remove line if length < 2 />
print('       ', '{:,}'.format(len(list2) + len(list2s) + len(list5)), 'filters kept')

# <write extracted regex type filters>

# <open file5_out file and write header>

file5_out = open(file5_out_name, 'w', encoding='UTF-8')

file5_out.write(
      '! description: personal regex filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_regex_block_list\n'
    + '! title: regex block list\n'
)

# </open file5_out file and write header>

list5 = sorted(list5)
file5_out.writelines(re.sub(r'\$important$', '', line)[1: -1] + '\n' for line in list5)
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

# <remove url filters covered by regex filters>

print('20/20 : simplify urls keeping last /* part and deflat url filters redundant with regex filters', sep = '')

list2 = [re.sub(r'^.+(?=/[^/]+$)', '', line) for line in list2]                 # <simplify urls keeping last /* part />
list2 = [line for line in list2 if len(line) > 3]                               # <keep filters with len > 3 />
list2 = [line for line in list2 if (re.search(r'[^\[\]\{\}\;\,\\]', line))]     # <remove broken regex filters />

for pattern in tqdm.tqdm(list5):
    pattern = re.sub(r'\$important$', '', pattern)[1: -1]
    try :
        pattern = re.compile(r'' + pattern)                                     # < create regex pattern for faster processing />
        list2 = [line for line in list2 if not(pattern.search(' ' + line + ' '))]
    except :
        print('Error found; check for ' + pattern + ' regex pattern in url sources')

list2 = sorted(set(list2) | set(list2s))                                        # <join lists'/>

print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept', '\n')

# </remove url filters covered by regex filters>

# <aggregate regex filters >

list2 = sorted(set(list2) | set(list5))

# </aggregate regex filters >

# <extract domains from list >

print('Listing domain filters : ', sep = '')

list3 = []

list2 = sorted(set(list2) - set(iana_tld))                                      # <remove IANA tld root domains from main list />

for tld in tqdm.tqdm(iana_tld):
    pattern = re.compile(r'' + ('^[-\.\w]+\.' + tld + '(?:\$important)?$'))
    list3 = list3 + [line for line in list2 if pattern.search(line)]

list3 = [line for line in list3 if line[0] != '-']                              # <remove -@.@ from domains list />
list2 = set(list2) - set(list3)                                                 # <only domains part are processed in this section; @.js are kept in list2 />

# </extract domains from list >

print('\nRemoving #.@(.@) numerical domain filters, IANA tld root domains and applying domains white list', sep = '')

list3 = [re.sub(r'^\.', '', line)  for line in list3]                           # <remove leading . preceding domain />
list3 = [re.sub('r\$important$', '', line) for line in list3]                   # <remove trailing $important from domains/>
list3 = [re.sub(r'^[-_\.0-9]+\.', '', line) for line in list3]                  # <remove #.@(.@) numerical domains/>
list3 = sorted(set(list3) - set(iana_tld))                                      # <remove IANA tld root domains />

#list3 = [line for line in list2 if re.search(r'^[-\.\w]+\.[a-z]+(\.[a-z]+)?(\$important)?$', line)]
#list3 = [line for line in list3 if not(re.search(r'^.*\.js(?:on)?(\$important)?$', line))]  # <remove @.js from domains list />
#list3 = [line for line in list3 if not(re.search(r'^.*\.css(\$important)?$', line))]        # <remove @.css from domains list />
#list3 = [line for line in list3 if not(re.search(r'^.*\.webp(\$important)?$', line))]       # <remove @.webp from domains list />
#list3 = [line for line in list3 if not(re.search(r'^.*\.bin(\$important)?$', line))]        # <remove @.bin from domains list />
#list3 = [line for line in list3 if not(re.search(r'^.*\.woff[0-9]?(\$important)?$', line))] # <remove @.woff# from domains list />
#list3 = [line for line in list3 if not(re.search(r'^.*\.link(\$important)?$', line))]       # <remove @.link from domains list />
#list3 = [line for line in list3 if not(re.search(r'^.*\.ttf(\$important)?$', line))]        # <remove @.ttf from domains list />

# <get domains white list from file, dedup and sort>

list8 = [line.strip() for line in open(file8_in_name, encoding='UTF-8')]        # <populate list; remove leading/trailing spaces />
list8 = [re.sub(r'^ *!.*', '', line) for line in list8]                         # <remove ! comments' />
list8 = [line for line in list8 if line.strip() != '']                          # <remove empty lines />

list3 = sorted(set(list3) - set(list8))

# </get domains white list from file, dedup and sort>

print(
    '{:,}'.format(len(list3)),
    'domains kept\n'
    )

# </remove #.@(.@) (numerical domains) and @.@ root domains from list>

if dom_sw == 'y' :

    # <remove redundant domains from list>

    print(
        'Domains deflating started; this operation could take long time, please wait\n',
        '---------------------------------------------------------------------------\n',
        sep = ''
    )

    list3r = [line for line in list3 if re.search(r'^[-_a-z0-9]+\.[a-z]+$', line)]  # <get @.@ domains />

    print(
        '{:,}'.format(len(list3r)),
        'elemental @.@ domains found; excluded from recursive domain deflating'
    )

    list3r3 = [line for line in list3 if re.search(r'^[-_a-z0-9]+\.[a-z0-9][-_a-z0-9]+\.[a-z]+$', line)]    # <@.@.@ domains items/>
    list3   = set(list3) - set(list3r) - set(list3r3)                           # < @.@ and @.@.@ domains removed for faster deflation; then added to final result />
    list3   = sorted(list3, key = lambda x: -len(x))                            # <sort by decreasing length for faster size reduction/>

    print(
        'recursive domain deflating (@.@.@ vs @.@)',
        '{:2.0f}'.format(1),
        '/',
        '2',
        ';',
        '{:,}'.format(len(list3) + len(list3r) + len(list3r3)),
        'domains kept'
    )
    list3r3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3r))) == 0) else '', tqdm.tqdm(list3r3)))
    list3r3 = [line for line in list3r3 if len(line) > 0]                       # <cleanup empty lines/>
    list3r  = sorted(set(list3r) | set(list3r3))                                # <compile deflated domains up to current stage/>
    del(list3r3)                                                                # <clean up; make sure list3r3 is not used anymore hereafter/>

    print(
        'recursive domain deflating (@.@.@.@+ vs @.@.@)',
        '{:2.0f}'.format(2),
        '/',
        '2',
        ';',
        '{:,}'.format(len(list3) + len(list3r)),
        'domains kept'
    )
    list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3r))) == 0) else '', tqdm.tqdm(list3)))
    list3 = sorted(set(list3r) | set(list3))                                    # <compile deflated domains up to current stage/>
    list3 = [line for line in list3 if len(line) > 0]                           # <cleanup empty lines/>
    del(list3r)                                                                 # <clean up; make sure list3r is not used anymore hereafter/>

    #list3_filter = list3
    #print(
    #    'recursive domain deflating',
    #    '{:2.0f}'.format(3),
    #    '/',
    #    '3',
    #    ';',
    #    '{:,}'.format(len(list3)),
    #    'domains kept'
    #    )
    ## <filter() + map() option>
    #list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3_filter))) == 0) else '', tqdm.tqdm(list3)))
    #list3 = [line for line in list3 if len(line) > 0]    # <cleanup empty lines/>
    ## </filter() + map() option>

    ## <filter() + list comprehension option; may worth it a benchmark vs map()?>
    ##list3 = [line for line in list3 if len(list(filter(lambda substring: ('.' + substring) in line, tqdm.tqdm(list3_filter[:n])))) == 0]
    ## </filter() + list comprehension option>

    #print(
    #    'removing urls redundant with domains;'
    #    '{:,}'.format(len(list3)),
    #    'domains kept after deflating',
    #    '\n'
    #)
    #list2 = list(map(lambda line: line if (line[1:] not in list3) else '', tqdm.tqdm(list2)))   # <remove urls redundant with domains/>
#list2 = [line for line in list2 if len(line) > 0]                              # <cleanup empty lines/>

    # </remove redundant domains from list>

list2 = sorted(set(list2) | set(list3))                                         # <rebuild full list with elemetal domains and shrinked domains part/>

print(
    '\n',
    '{:,}'.format(len(list2)),
    'filters remaining after compilation\n'
)

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

print('added filter to block numerical domains #.@(.@) filters and exceptions')

list2.append('/^([-\.\w]+\.)?[-_0-9]+\.[a-z]+(\.[a-z]+)?/')                     # <add filter to block [-_/\.0-9]+\.[a-z]+ domains />

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
list2.append('@@||ikea.com^$inline-script,1p')
list2.append('@@||ikea.com/*/header-footer/menu-products.html$xhr,1p')
list2.append('@@||ikea.es^$inline-script,1p')
list2.append('@@||licdn.com^$xhr,domain=linkedin.com')
list2.append('@@||linkedin.com^$inline-script,1p')
list2.append('@@||linkedin.com^$removeparam=/redir/')
list2.append('@@||mail.google.com^$removeparam=view')
list2.append('@@||mail.google.com^$xhr,1p')
list2.append('@@||meteoblue.com^$inline-script,xhr,1p')
list2.append('@@||meteoblue.com^$removeparam=/callback/i')
list2.append('@@||meteoblue.com^$removeparam=/metric/i')
list2.append('@@/[_\W]adunits?[_\W]/$domain=youtube.com')
list2.append('@@||worldbank.org^$inline-script,1p')
list2.append('@@||www.linkedin.com^$inline-script,xhr,1p')
list2.append('@@||youtube.com^$inline-script,xhr,1p')

list2 = sorted(set(list2))

file2_out = open(file2_out_name, 'w')

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
    '! *$popup,3p avoided (impedes ctrl&click open in another tab)\n' +
    '! attribute css selector : ##[]\n' +
    '! class css selector     : ##.\n' +
    '! id css selector        : ###\n' +
    '! \w = [a-zA-Z0-9_]      : ###\n' +
    '! \W = [^a-zA-Z0-9_]     : ###\n' +
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

file3_out = open(file3_out_name, 'w', encoding='UTF-8')

file3_out.write(
      '! description: personal domain filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_domain_block_list\n'
    + '! title: domain block list\n'
    )

# <\open file3_out file and write header />

list3 = set(list3)
list3 = sorted(list3, key = lambda x: (re.sub(r'^.*\.(?=[^\.]+\.[^\.]+\Z)', '', x)))    # <sort by a-z @(.@) />
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

file4_out = open(file4_out_name, 'w', encoding='UTF-8')

file4_out.write(
      '! description: personal url filters for ipfire and ublock_origin\n'
    + '! expires: 1 day\n'
    + '! homepage: https://raw.githubusercontent.com/mipiticuenta/ublock_live/main/ipfire_url_block_list\n'
    + '! title: url block list\n'
)

# </open file4_out file and write header>

list4 = set(list2) - set(list3) - set(list5)
list4 = [re.sub(r'\$important$', '', line) for line in list4]                   # <remove ''$important'' tag at the end (if present)/>
list4 = [line for line in list4 if re.search(r'^[-/\.\w]+$', line)]             # <keep url items/>
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

file7_out = open(file7_out_name, 'w', encoding='UTF-8')

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

'''
Compile a single deduplicated block list from url sources
'''

# <product backlog>

# <sprint #1: dedup urls/>
# <sprint #2: apply multicore/>

# </product backlog>

import math                                                                     # <math functions />
import os                                                                       # <operating system interfaces />
import re                                                                       # <regular expression operations />
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

list1 = [line.strip() for line in open(file1_in_name, encoding='UTF-8')]        # <populate source lists; remove leading/trailing spaces />
list1 = [re.sub(r'(^| +)!.*', '', line) for line in list1]                      # <remove comments' />
list1 = [line for line in list1 if line.strip() != '']                          # <discard empty lines />

list1 = sorted(list1)

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
            '                         ',
            '{:,}'.format(len(list2)),
            'cumulated filters'
        )

# </dump sources to list>

list2 = [re.sub(r'^/([-\.\w]+/[-\./\w]+)/$', r'/\1/*', line) for line in list2]    # <fix /@/@/ url filters adding trailing * />

# <segregate regex filters>

list5 = [line for line in list2 if re.search(r'^/.+/(\$[,a-z]+)?$', line)]
list2  = set(list2) - set(list5)

# <segregate regex filters>

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
file5_out.writelines('.*' + re.sub(r'\$important$', '', line)[1:-1] + '.*' + '\n' for line in list5)
file5_out.close()

print(
    '\n',
    '{:,}'.format(len(list5)),
    ' regex filters written to ',
    file5_out_name,
    sep = ''
)

# </write extracted regex type filters>

# <process filter list>

print(
    '\n',
    'Transforming filters\n',
    '--------------------\n'
)

# <transforming loop>

print(' 1/20 : remove leading/trailing/dup spaces ')

list2 = [re.sub(r'\t', ' ', line).strip() for line in list2]                    # <replace tab with space  />
list2 = [re.sub(r' +', ' ', line).strip() for line in list2]                    # <dedup spaces and remove leading/trailing spaces />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 2/20 : remove comments ')

list2 = [re.sub(r'(^| +)!+.*', '', line) for line in list2]                     # <remove ! comment />
list2 = [re.sub(r'(^| +)#(?!(\?|@|#\:|#\.|##|#\[)).*', '', line) for line in list2]     # <remove # comment; preserve cosmetics and exceptions />
list2 = [re.sub(r'^\[.*', '', line) for line in list2]                          # <remove [comment] line />
list2 = [re.sub(r'^\{.*', '', line) for line in list2]                          # <remove {comment} line />
list2 = [re.sub(r'^[^a-z0-9]+$', '', line) for line in list2]                   # <remove lines comprised only by simbols />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 3/20 : keep domains from dns || #[] style filters ')

list2 = [re.sub(r'^0\.0\.0\.0 ', '', line) for line in list2]                   # <remove leading   0.0.0.0 (dns style filter) />
list2 = [re.sub(r'^127\.0\.0\.1 ', '', line) for line in list2]                 # <remove leading 127.0.0.1 (dns style filter) />
list2 = [re.sub(r'^\:\:1 ', '', line) for line in list2]                        # <remove leading ::1 (dns style filter) />
list2 = [re.sub(r'^\|+', '', line) for line in list2]                           # <remove leading domain mark (||) />

list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 4/20 : remove items containing % about: $badfilter localhost /wp-content/uploads/; remove http: IP4 IP6 :port/ www')

list2 = [re.sub(r'^[^a-z]+$', '', line) for line in list2]                      # <remove lines comprised only by simbols and numbers />
list2 = [line for line in list2 if not(re.search(r'[,\$]badfilter', line))]     # <remove items comprising $badfilter />
list2 = [line for line in list2 if not(re.search(r'about\:', line))]            # <remove items comprising about: >
list2 = [line for line in list2 if not(re.search(r'\%', line))]                 # <remove items comprising % >
list2 = [re.sub(r'http.?\:(/+)?', '', line) for line in list2]                  # <replace http:/+ with / />
list2 = [re.sub(r'^/?([0-9]+\.)+([0-9]+)?', '', line).strip() for line in list2]    # <remove IP4 addresses (d.)+ />
list2 = [line for line in list2 if not(re.search(r'\:\:', line))]               # <remove IP6 addresses :: />
list2 = [re.sub(r'^\:[0-9]+/', '', line) for line in list2]                     # <remove leading :port/ />
list2 = [re.sub(r'www[0-9]*\.', '', line) for line in list2]                    # <remove www. />
list2 = [line for line in list2 if not(re.search(r'localhost', line))]          # <remove items containing localhost />
list2 = [re.sub(r'^.*/wp\-content/uploads/?.*', '', line) for line in list2]    # <remove items containing /wp-content/uploads/' />
list2 = [re.sub(r'(?<=[a-z])\^\*', '/*', line) for line in list2]               # <replace ^* with / />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 5/20 : keep case for cosmetic filters; apply lower case for the remaining ')
list2 = (
    [line         for line in list2 if     re.search(r'[#\\]', line) ] + 
    [line.lower() for line in list2 if not(re.search(r'[#\\]', line))]          # <lower case for all except cosmetics and regex />
)
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 6/20 : generalize cosmetic filters (*##) and exceptions (*#@ *#? *@@) ')
list2 = [re.sub(r'^.*(?=\#[\#\?])', '*', line) for line in list2]               # <generalize cosmetic (*##) (*#?) />
list2 = [re.sub(r'^.*(?=[\#\@]\@)', '*', line) for line in list2]               # <generalize exception (*#@) (*@@) />
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 7/20 : remove cosmetic filters (##) and exceptions (@@) except *##:')   # <currently discarded; consider processing (future sprints?)/>

list2 = [re.sub(r'^\*?\#\#(?!\:).*', '', line) for line in list2]               # <remove cosmetic filters except ##: />
list2 = [re.sub(r'^\*?\#\@.*', '', line) for line in list2]                     # <remove #@ exceptions />
list2 = [re.sub(r'^\*?\#\?.*', '', line) for line in list2]                     # <remove #? exceptions />
list2 = [re.sub(r'^\*?\@\@.*', '', line) for line in list2]                     # <remove @@ exceptions />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
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
list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
del(list2s)
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print(' 9/20 : remove domain= denyallow= filters and keep the related domains')

list2s = (
    [line for line in list2 if re.search(r'.*domain=', line)] +                 # <select *$ filters />
    [line for line in list2 if re.search(r'.*denyallow=', line)]                # <select denyallow filters />
)

list2 = set(list2) - set(list2s)                                                # <segregate selected filters'/>

list2s = [re.sub(r'.*domain=', '', line).strip() for line in list2s]            # <remove leading .*domain=/>
list2s = [re.sub(r'.*denyallow=', '', line).strip() for line in list2s]         # <remove leading .*denyallow=/>
list2s = [re.sub(r'\,.*$', '', line).strip() for line in list2s]                # <remove trailing .*,.*/>

list2s = [line.split('|') for line in list2s if len(line) > 0]                  # <flatten list'/>
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
del(list2s)
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('10/20 : split , separated domains ')

list2 = [re.sub(r'^,', '', line).strip() for line in list2]                     # <remove leading , />
list2 = [re.sub(r',$', '', line).strip() for line in list2]                     # <remove trailing , />
list2s = [line for line in list2 if re.search(r'\,', line) and not(re.search(r'[\$\&]', line))]    # <remove , separated domains />

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = [line.split(',') for line in list2s]                                   # <flatten list'/>
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
del(list2s)
list2 = sorted(list2)
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

    list2 = [re.sub(r'^[_\W0-9]+[/\.]', '', line) for line in list2]            # <remove leading symbols and numbers preceding / . />
    list2 = [re.sub(r'^[_\W0-9]+(?=\$)', '', line) for line in list2]           # <remove leading symbols and numbers preceding $ />
    list2 = [re.sub(r'^[/\.]?[-\w\*](?=[/\.])', '', line).strip() for line in list2]    # <remove leading single -_a-z0-9\* preceding / . />
    list2 = [re.sub(r'^[/\.]?[a-z][0-9](?=[/\.])', '', line).strip() for line in list2] # <remove leading single char number preceding / . />
    list2 = [re.sub(r'^[/\.]\*', '*', line).strip() for line in list2]          # <remove leading / . if followed by * />
    list2 = [re.sub(r'^/\.', '/', line) for line in list2]                      # <remove leading /. with / />
    list2 = [re.sub(r'^\$', '*$', line).strip() for line in list2]              # <fix leading $ with *$ />
    list2 = [re.sub(r'^[/\.\=\?]\$', '*$', line).strip() for line in list2]     # <fix leading /$ .$ =$ ?$ with *$ />
    list2 = [re.sub(r'^\.?[-_a-z0-9\*]+/', '/', line) for line in list2]        # <replace leading @/ with / />
    list2 = [re.sub(r'^[/\.]?ajax\*?(?=[/\.])', '', line) for line in list2]    # <remove leading ajax />
    list2 = [re.sub(r'^[/\.]?api\*?(?=[/\.])', '', line) for line in list2]     # <remove leading api />
    list2 = [re.sub(r'^[/\.]?apple\*?(?=[/\.])', '', line) for line in list2]   # <remove leading apple />
    list2 = [re.sub(r'^[/\.]?app\*?(?=[/\.])', '', line) for line in list2]     # <remove leading app />
    list2 = [re.sub(r'^[/\.]?assets?\*?(?=[/\.])', '', line) for line in list2] # <remove leading asset />
    list2 = [re.sub(r'^[/\.]?attachments?\*?(?=[/\.])', '', line) for line in list2]    # <remove leading attachment />
    list2 = [re.sub(r'^[/\.]?brands?\*?(?=[/\.])', '', line) for line in list2] # <remove leading brand(s) />
    list2 = [re.sub(r'^[/\.]?build\*?(?=[/\.])', '', line) for line in list2]   # <remove leading build />
    list2 = [re.sub(r'^[/\.]?business\*?(?=[/\.])', '', line) for line in list2]        # <remove leading business />
    list2 = [re.sub(r'^[/\.]?catalog\*?(?=[/\.])', '', line) for line in list2] # <remove leading catalog />
    list2 = [re.sub(r'^[/\.]?cdn(\-cgi)?(?=[/\.])', '', line) for line in list2]        # <remove leading cdn(-cgi) />
    list2 = [re.sub(r'^[/\.]?center\*?(?=[/\.])', '', line) for line in list2]  # <remove leading center />
    list2 = [re.sub(r'^[/\.]?cgi\-bin\*?(?=[/\.])', '', line) for line in list2]        # <remove leading cgi-bin />
    list2 = [re.sub(r'^[/\.]?comm?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading com(m) />
    list2 = [re.sub(r'^[/\.]?common\*?(?=[/\.])', '', line) for line in list2]  # <remove leading common />
    list2 = [re.sub(r'^[/\.]?contents?\*?(?=[/\.])', '', line) for line in list2]       # <remove leading content(s) />
    list2 = [re.sub(r'^[/\.]?core\*?(?=[/\.])', '', line) for line in list2]    # <remove leading core />
    list2 = [re.sub(r'^[/\.]?creatives?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading creative(s) />
    list2 = [re.sub(r'^[/\.]?css\*?(?=[/\.])', '', line) for line in list2]     # <remove leading css />
    list2 = [re.sub(r'^[/\.]?custom\*?(?=[/\.])', '', line) for line in list2]  # <remove leading custom />
    list2 = [re.sub(r'^[/\.]?data\*?(?=[/\.])', '', line) for line in list2]    # <remove leading data />
    list2 = [re.sub(r'^[/\.]?default\*?(?=[/\.])', '', line) for line in list2] # <remove leading default />
    list2 = [re.sub(r'^[/\.]?ebay\*?(?=[/\.])', '', line) for line in list2]    # <remove leading ebay />
    list2 = [re.sub(r'^[/\.]?ext\*?(?=[/\.])', '', line) for line in list2]     # <remove leading ext />
    list2 = [re.sub(r'^[/\.]?files?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading file(s) />
    list2 = [re.sub(r'^[/\.]?forum\*?(?=[/\.])', '', line) for line in list2]   # <remove leading forum />
    list2 = [re.sub(r'^[/\.]?home?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading home />
    list2 = [re.sub(r'^[/\.]?html?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading html />
    list2 = [re.sub(r'^[/\.]?ima?ge?(ne)?s?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading image />
    list2 = [re.sub(r'^[/\.]?jquery\*?(?=[/\.])', '', line) for line in list2]  # <remove leading jquery />
    list2 = [re.sub(r'^[/\.]?js\*?(?=[/\.])', '', line) for line in list2]      # <remove leading js />
    list2 = [re.sub(r'^[/\.]?libs?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading lib(s) />
    list2 = [re.sub(r'^[/\.]?modules?\*?(?=[/\.])', '', line) for line in list2]    # <remove leading module(s) />
    list2 = [re.sub(r'^[/\.]?(multi)?media\*?(?=[/\.])', '', line) for line in list2]   # <remove leading (multi)media />
    list2 = [re.sub(r'^[/\.]?news?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading new(s) /
    list2 = [re.sub(r'^[/\.]?pics?\*?(?=[/\.])', '', line) for line in list2]   # <remove leading pic(s) /
    list2 = [re.sub(r'^[/\.]?plugins?\*?(?=[/\.])', '', line) for line in list2]        # <remove leading plugin(s) /
    list2 = [re.sub(r'^[/\.]?public\*?(?=[/\.])', '', line) for line in list2]  # <remove leading public />
    list2 = [re.sub(r'^[/\.]?resources?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading resource(s) />
    list2 = [re.sub(r'^[/\.]?scripts?\*?(?=[/\.])', '', line) for line in list2]        # <remove leading script(s) />
    list2 = [re.sub(r'^[/\.]?scr\*?(?=[/\.])', '', line) for line in list2]     # <remove leading src />
    list2 = [re.sub(r'^[/\.]?sdk\*?(?=[/\.])', '', line) for line in list2]     # <remove leading sdk />
    list2 = [re.sub(r'^[/\.]?sites?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading site(s) />
    list2 = [re.sub(r'^[/\.]?source\*?(?=[/\.])', '', line) for line in list2]  # <remove leading source />
    list2 = [re.sub(r'^[/\.]?_?statics?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading static />
    list2 = [re.sub(r'^[/\.]?styles?\*?(?=[/\.])', '', line) for line in list2] # <remove leading style(s) />
    list2 = [re.sub(r'^[/\.]?temp\*?(?=[/\.])', '', line) for line in list2]    # <remove leading temp />
    list2 = [re.sub(r'^[/\.]?themes?\*?(?=[/\.])', '', line) for line in list2] # <remove leading theme(s) />
    list2 = [re.sub(r'^[/\.]?uploads?.?\*?(?=[/\.])', '', line) for line in list2]      # <remove leading uploads />
    list2 = [re.sub(r'^[/\.]?videos?\*?(?=[/\.])', '', line) for line in list2] # <remove leading video(s) />
    list2 = [re.sub(r'^[/\.]?v.?\*?(?=[/\.])', '', line) for line in list2]     # <remove leading v />
    list2 = [re.sub(r'^[/\.]?web(resource)?\*?(?=[/\.])', '', line) for line in list2]  # <remove leading web(resource) />
    list2 = [re.sub(r'^[/\.]?wp\-content\*?(?=[/\.])', '', line) for line in list2]     # <remove leading wp-content />
    list2 = [re.sub(r'^[/\.]?www\*?(?=[/\.])', '', line) for line in list2]     # <remove leading www />
    list2 = [re.sub(r'^\.?aspx?\??(?![a-z0-9])', '*', line).strip() for line in list2]  # <replace leading asp with * >
    list2 = [re.sub(r'^\.?cgi\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading cgi with * >
    list2 = [re.sub(r'^\.?cfm\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading cfm with * >
    list2 = [re.sub(r'^\.?gif\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading gif with * >
    list2 = [re.sub(r'^\.?html?\??(?![a-z0-9])', '*', line).strip() for line in list2]  # <replace leading htm with * >
    list2 = [re.sub(r'^\.?jpg\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading jpg with * >
    list2 = [re.sub(r'^[/\.]?js/', '/', line) for line in list2]                # <replace leading js/ with / />
    list2 = [re.sub(r'^\.?js\??(?![a-z0-9])', '*', line).strip() for line in list2]     # <replace leading js with * >
    list2 = [re.sub(r'^\.?mp[0-9]\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading mp* with * >
    list2 = [re.sub(r'^\.?php\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading php with * >
    list2 = [re.sub(r'^\.?png\??(?![a-z0-9])', '*', line).strip() for line in list2]    # <replace leading png with * >
    list2 = [re.sub(r'^\.?tiff\??(?![a-z0-9])', '*', line).strip() for line in list2]   # <replace leading tiff with * >

    list2 = [line for line in list2 if len(line) > 1]                           # <remove items if length < 2 />
    list2 = sorted(list2)
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

    print('12/20 : clean up trailing symbols numbers prefix $filters etc')
    list2 = [re.sub(r'[\^\|\=]\$', '$', line).strip() for line in list2]        # <replace ^$ |$ =$ with $/>
    list2 = [re.sub(r'\|+\$', '$', line).strip() for line in list2]             # <replace |$ with $/>
    list2 = [re.sub(r'[#,\~\|\^\?\=\&]+$', '', line).strip() for line in list2] # <remove trailing # , ~ | ^ ? = & />
    list2 = [re.sub(r'(?<!/)\*$', '', line).strip() for line in list2]          # <remove trailing * except not-regex markup //*/>
    list2 = [re.sub(r'\.\*$', '.', line).strip() for line in list2]             # <replace trailing .* with ./>
    list2 = [re.sub(r'\*\.$', '', line).strip() for line in list2]              # <remove trailing *. />
    list2 = [re.sub(r'\.cgi\??$', '.', line) for line in list2]                 # <remove trailing .cgi?/>
    list2 = [re.sub(r'\.ashx\??$', '.', line) for line in list2]                # <remove trailing .ashx?/>
    list2 = [re.sub(r'\.asp\??$', '.', line) for line in list2]                 # <remove trailing .asp?/>
    list2 = [re.sub(r'\.?html?\??$', '.', line) for line in list2]              # <remove trailing .html?/>
    list2 = [re.sub(r'\.js(?![a-z0-9/]).*$', '.js', line) for line in list2]    # <clean up trailing .js />
    list2 = [re.sub(r'\.jpe?g\??$', '.', line) for line in list2]               # <remove trailing .jp(e)g?/>
    list2 = [re.sub(r'\.php\??$', '.', line) for line in list2]                 # <remove trailing .php?/>
    list2 = [re.sub(r'\.png\??$', '.', line) for line in list2]                 # <remove trailing .png?/>
    list2 = [re.sub(r'\.svg\??$', '.', line) for line in list2]                 # <remove trailing .svg?/>
    list2 = [re.sub(r'(^[^#]{2,})\$[-~,=a-z0-9]*$(?<!/)(?<!important)', r'\1', line) for line in list2]    # <remove specific trailing $ filters except *$ or ending with important />
    list2 = [re.sub(r'\??\*\=.*(^/)$', '', line).strip() for line in list2]     # <remove trailing ?*=... />

    list2 = [line for line in list2 if len(line) > 1]                           # <remove items if length < 2 />
    list2 = sorted(list2)
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

    print('13/20 : split domain and url ')

    list2s = [line for line in list2 if re.search(r'^[-\.\w]+\.[a-z]+/.*', line)]   # <get domains with url'/>

    list2 = set(list2) - set(list2s)                                            # <segregate removed filters'/>

    list2s = (
        [re.sub(r'^[-\.\w]+/', '/', line) for line in list2s] +                 # <isolate url part/>
        [re.sub(r'/.*$', '', line) for line in list2s]                          # <isolate domains part/>
    )

    list2 = sorted(set(list2) | set(list2s))                                    # <join retrieved domains to main list'/>
    list2 = [line for line in list2 if len(line) > 1]                           # <remove items if length < 2 />
    del(list2s)
    list2 = sorted(list2)
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

    print('14/20 : simplify urls; keep just last /* part ')

    list2 = [re.sub(r'\*+', '*', line).strip() for line in list2]               # <dedup * />
    list2 = [re.sub(r'\.+', '.', line).strip() for line in list2]               # <dedup . />
    list2 = [re.sub(r'/+', '/', line).strip() for line in list2]                # <dedup / />
    list2 = [re.sub(r'^[^a-z]+$', '', line).strip() for line in list2]          # <remove lines comprised only by simbols and numbers />
    list2 = [re.sub(r'^[^a-z]+x[^a-z]+$', '', line) for line in list2]          # <remove lines comrpised by [^a-z]+x[^a-z]+ combinations />
    list2 = [re.sub(r'^[a-z]{1,3}$', '', line) for line in list2]               # <remove ^[a-z]{1,3}$ filters />
    list2 = [re.sub(r'^[_\W]?[^ap]?[^dx]?[_\W]?\*?$', '', line) for line in list2]       # <remove 2 chars max [a-z][0-9] sequence filter excluding ad px />
    list2 = [re.sub(r'^[_\W]?a?[^d]?[_\W]?\*?$', '', line) for line in list2]   # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[_\W]?p?[^x]?[_\W]?\*?$', '', line) for line in list2]   # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[_\W]?[^a]?d?[_\W]?\*?$', '', line) for line in list2]   # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[_\W]?[^p]?x?\*?$', '', line) for line in list2]         # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[^a-z]+x[^a-z]+[/\.](?!(com|net))', '', line) for line in list2]  # <remove leading [^a-z]+x[^a-z]+ combinations />
    list2 = [re.sub(r'^[-/\.\w]+(?=/[-\.\w]+$)', '', line) for line in list2]   # <simplify urls keeping last /* part />
    list2 = [re.sub(r'^.*/\*/', '/', line) for line in list2]                   # <replace any url preceded by /*/ (included) with / />
    list2 = [re.sub(r'^[-/\.\w]*(\*[-/\.\w]*)+$(?<!/\*)', '', line).strip() for line in list2]    # <remove url filters using * wildcard except ending with /* />
    list2 = [re.sub(r'^[-/\.\w]*(\*[-/\.\w]*)+/\*$', '', line).strip() for line in list2]         # <remove //* url filters using * wildcard />
    list2 = [re.sub(r'^\.(?=[a-z]*\.(com|edu|gob|gou?v|net|org))', '', line).strip() for line in list2]     # <remove leading . preceded by domain com edu gob go(u)v net org />

    list2 = [line for line in list2 if len(line) > 1]                           # <remove items if length < 2 />
    list2 = sorted(list2)
    print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('15/20 : split space separated domains ')

list2s = [line for line in list2 if re.search(r' ', line) and not(re.search(r'[\$\&\#]', line))]    # <remove space separated domains />

list2 = set(list2) - set(list2s)                                                # <segregate removed filters'/>

list2s = [line.split(' ') for line in list2s]                                   # <flatten list'/>
list2s = [item for line in list2s for item in line if line !=[''] and item != '']   # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                        # <join retrieved domains to main list'/>
del(list2s)
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('16/20 : remove lines leaded by ! # + & ? ^ : ; @ and @.exe @.gif @.rar @.zip')

list2 = [re.sub(r'^\|\|', '', line) for line in list2]                          # <remove leading || />
list2 = [re.sub(r'^\!.*', '', line) for line in list2]                          # <remove ! leaded lines />
list2 = [re.sub(r'^#.*', '', line) for line in list2]                           # <remove # leaded lines />
list2 = [re.sub(r'^[/\*]?\+.*', '', line) for line in list2]                    # <remove + leaded lines />
list2 = [re.sub(r'^\*?\&.*', '', line) for line in list2]                       # <remove & leaded lines />
list2 = [re.sub(r'^\*?\?.*', '', line) for line in list2]                       # <remove ? leaded lines />
list2 = [re.sub(r'^\*?\^.*', '', line) for line in list2]                       # <remove ^ leaded lines />
list2 = [re.sub(r'^\*?\:.*', '', line) for line in list2]                       # <remove : leaded lines />
list2 = [re.sub(r'^\*?\;.*', '', line) for line in list2]                       # <remove ; leaded lines />
list2 = [re.sub(r'^\*?\".*', '', line) for line in list2]                       # <remove " leaded lines />
list2 = [re.sub(r'^[/\*]?\@.*', '', line) for line in list2]                    # <remove @ leaded lines />
list2 = [re.sub(r'^.*\.gif$', '.gif', line) for line in list2]                  # <ensure .gif filter />
list2 = [re.sub(r'^.*\.rar$', '', line) for line in list2]                      # <remove @.rar filters />
list2 = [re.sub(r'^.*\.zip$', '', line) for line in list2]                      # <remove @.zip filters />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
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
list2 = [re.sub(r'^\*\$\~?xmlhttprequest.*', '', line) for line in list2]       # <enforce *$xhr />
list2 = [re.sub(r'^\*\$important.*', '', line) for line in list2]               # <remove *$important filters />
list2 = [re.sub(r'^\*\$.*\.js$', '', line) for line in list2]                   # <remove *$...js filters />
list2 = [re.sub(r'^[_\W]?api\.js$', '', line) for line in list2]                # <remove api.js filter />
list2 = [re.sub(r'^[_\W]?base\.js$', '', line) for line in list2]               # <remove base.js filter />
list2 = [re.sub(r'^[_\W]?main\.js$', '', line) for line in list2]               # <remove main.js filter />
list2 = [re.sub(r'^[_\W]?(bootstrap\.)?min\.js$', '', line) for line in list2]  # <remove bootstrap.min.js filter />
list2 = [re.sub(r'^[_\W]?(lazyload\.)?min\.js$', '', line) for line in list2]   # <remove lazyload.min.js filter />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('18/20 : remove spurious url filters ')

# <get regex white list from file, dedup, sort and clean up filters>

list9 = [line.strip() for line in open(file9_in_name, encoding='UTF-8')]        # <populate list; remove leading/trailing spaces />
list9 = [re.sub(r'(^| +)!.*', '', line) for line in list9]                      # <remove comments' />
list9 = [line for line in list9 if line.strip() != '']                          # <discard empty lines />

for item in tqdm.tqdm(list9) :
    list2 = [re.sub(item, '', line) for line in list2]                          # <remove spurious filter from main list based on regex-white_list/>
    list5 = [re.sub(item, '', line) for line in list5]                          # <remove spurious filter from regex list based on regex-white_list />

# </get regex white list from file, dedup, sort and clean up filters>


#list2 = [re.sub(r'^[_\W]?abc[_\W]*$', '', line) for line in list2]              # <remove spurious abc filter />
#list2 = [re.sub(r'^[_\W]?about[_\W]*$', '', line) for line in list2]            # <remove spurious about filter />
#list2 = [re.sub(r'^[_\W]?account[_\W]*$', '', line) for line in list2]          # <remove spurious account filter />
#list2 = [re.sub(r'^[_\W]?(accu)weather[_\W]*$', '', line) for line in list2]    # <remove spurious (accu)weather filter />
#list2 = [re.sub(r'^[_\W]?action[_\W]*$', '', line) for line in list2]           # <remove spurious action filter />
#list2 = [re.sub(r'^[_\W]?activity[_\W]*$', '', line) for line in list2]         # <remove spurious activity filter />
#list2 = [re.sub(r'^[_\W]?adc[_\W]*$', '', line) for line in list2]              # <remove spurious adc filter />
#list2 = [re.sub(r'^[_\W]?add(ons?)?[_\W]*$', '', line) for line in list2]       # <remove spurious add(on(s)) filter />
#list2 = [re.sub(r'^[_\W]?admin[_\W]*$', '', line) for line in list2]            # <remove spurious admin filter />
#list2 = [re.sub(r'^[_\W]?afr[_\W]*$', '', line) for line in list2]              # <remove spurious afr filter />
#list2 = [re.sub(r'^[_\W]?agent[_\W]*$', '', line) for line in list2]            # <remove spurious agent filter />
#list2 = [re.sub(r'^[_\W]?airbnb[_\W]*$', '', line) for line in list2]           # <remove spurious airbnb filter />
#list2 = [re.sub(r'^[_\W]?ajax[_\W]*$', '', line) for line in list2]             # <remove spurious ajax filter />
#list2 = [re.sub(r'^[_\W]?akamai(hd|zed)?[_\W]*$', '', line) for line in list2]  # <remove spurious akamai(hd|zed) filter />
#list2 = [re.sub(r'^[_\W]?all[_\W]*$', '', line) for line in list2]              # <remove spurious all filter />
#list2 = [re.sub(r'^[_\W]?amazon[_\W]*$', '', line) for line in list2]           # <remove spurious amazon filter />
#list2 = [re.sub(r'^[_\W]?anchor[_\W]*$', '', line) for line in list2]           # <remove spurious anchor filter />
#list2 = [re.sub(r'^[_\W]?apis?[0-9]?[_\W]*$', '', line) for line in list2]      # <remove spurious api(s(0-9) filter />
#list2 = [re.sub(r'^[_\W]?app(le)?[_\W]*$', '', line) for line in list2]         # <remove spurious app(le) filter />
#list2 = [re.sub(r'^[_\W]?archi(ve)[_\W]*$', '', line) for line in list2]        # <remove spurious archi(ve) filter />
#list2 = [re.sub(r'^[_\W]?archivo[_\W]*$', '', line) for line in list2]          # <remove spurious archivo filter />
#list2 = [re.sub(r'^[_\W]?arriba[_\W]*$', '', line) for line in list2]           # <remove spurious arriba filter />
#list2 = [re.sub(r'^[_\W]?art(icle)?s?[_\W]*$', '', line) for line in list2]     # <remove spurious art(icle)(s) filter />
#list2 = [re.sub(r'^[_\W]?assets?[_\W]*$', '', line) for line in list2]          # <remove spurious base filter />
#list2 = [re.sub(r'^[_\W]?(a)?sync[_\W]*$', '', line) for line in list2]         # <remove spurious (a)sync filter />
#list2 = [re.sub(r'^[_\W]?audience[_\W]*$', '', line) for line in list2]         # <remove spurious audience filter />
#list2 = [re.sub(r'^[_\W]?audio[_\W]*$', '', line) for line in list2]            # <remove spurious audio filter />
#list2 = [re.sub(r'^[_\W]?(auto)?optimize[_\W]*$', '', line) for line in list2]  # <remove spurious (auto)optimize filter />
#list2 = [re.sub(r'^[_\W]?auto[_\W]*$', '', line) for line in list2]             # <remove spurious auto filter />
#list2 = [re.sub(r'^[_\W]?avatar[_\W]*$', '', line) for line in list2]           # <remove spurious avatar filter />
#list2 = [re.sub(r'^[_\W]?back(grounds?)?[_\W]*$', '', line) for line in list2]  # <remove spurious back(ground) filter />
#list2 = [re.sub(r'^[_\W]?bank[_\W]*$', '', line) for line in list2]             # <remove spurious bank filter />
#list2 = [re.sub(r'^[_\W]?bar[_\W]*$', '', line) for line in list2]              # <remove spurious bar filter />
#list2 = [re.sub(r'^[_\W]?base[_\W]*$', '', line) for line in list2]             # <remove spurious base filter />
#list2 = [re.sub(r'^[_\W]?basic[_\W]*$', '', line) for line in list2]            # <remove spurious basic filter />
#list2 = [re.sub(r'^[_\W]?batch[_\W]*$', '', line) for line in list2]            # <remove spurious batch filter />
#list2 = [re.sub(r'^[_\W]?bbc[_\W]*$', '', line) for line in list2]              # <remove spurious bbc filter />
#list2 = [re.sub(r'^[_\W]?bcn[_\W]*$', '', line) for line in list2]              # <remove spurious bcn filter />
#list2 = [re.sub(r'^[_\W]?below[_\W]*$', '', line) for line in list2]            # <remove spurious below filter />
#list2 = [re.sub(r'^[_\W]?bestbuy[_\W]*$', '', line) for line in list2]          # <remove spurious bestbuy filter />
#list2 = [re.sub(r'^[_\W]?beta[_\W]*$', '', line) for line in list2]             # <remove spurious beta filter />
#list2 = [re.sub(r'^[_\W]?bi[g|n][_\W]*$', '', line) for line in list2]          # <remove spurious bi(g|n) filter />
#list2 = [re.sub(r'^[_\W]?billboard[_\W]*$', '', line) for line in list2]        # <remove spurious billboard filter />
#list2 = [re.sub(r'^[_\W]?bing[_\W]*$', '', line) for line in list2]             # <remove spurious bing filter />
#list2 = [re.sub(r'^[_\W]?bla[cn]k[_\W]*$', '', line) for line in list2]         # <remove spurious bla(c|n)k filter />
#list2 = [re.sub(r'^[_\W]?blocks?[_\W]*$', '', line) for line in list2]          # <remove spurious block(s) filter />
#list2 = [re.sub(r'^[_\W]?blog(spot)?s?[_\W]*$', '', line) for line in list2]    # <remove spurious blog(spot)(s) filter />
#list2 = [re.sub(r'^[_\W]?blue[_\W]*$', '', line) for line in list2]             # <remove spurious blue filter />
#list2 = [re.sub(r'^[_\W]?bmw[_\W]*$', '', line) for line in list2]              # <remove spurious bmw filter />
#list2 = [re.sub(r'^[_\W]?bnn[_\W]*$', '', line) for line in list2]              # <remove spurious bnn filter />
#list2 = [re.sub(r'^[_\W]?body[_\W]*$', '', line) for line in list2]             # <remove spurious body filter />
#list2 = [re.sub(r'^[_\W]?bootstrap(\.min)?[_\W]*$', '', line) for line in list2]    # <remove spurious bootstrap(.min) filter />
#list2 = [re.sub(r'^[_\W]?bottom[_\W]*$', '', line) for line in list2]           # <remove spurious bottom filter />
#list2 = [re.sub(r'^[_\W]?box[_\W]*$', '', line) for line in list2]              # <remove spurious box filter />
#list2 = [re.sub(r'^[_\W]?brand(ing)?[_\W]*$', '', line) for line in list2]      # <remove spurious brand(ing) filter />
#list2 = [re.sub(r'^[_\W]?braze[_\W]*$', '', line) for line in list2]            # <remove spurious braze filter />
#list2 = [re.sub(r'^[_\W]?bridge[_\W]*$', '', line) for line in list2]           # <remove spurious bridge filter />
#list2 = [re.sub(r'^[_\W]?browser[_\W]*$', '', line) for line in list2]          # <remove spurious browser filter />
#list2 = [re.sub(r'^[_\W]?btn[_\W]*$', '', line) for line in list2]              # <remove spurious btn filter />
#list2 = [re.sub(r'^[_\W]?build(er)?[_\W]*$', '', line) for line in list2]       # <remove spurious build(er) filter />
#list2 = [re.sub(r'^[_\W]?bundle[_\W]*$', '', line) for line in list2]           # <remove spurious bundle filter />
#list2 = [re.sub(r'^[_\W]?buttons?[_\W]*$', '', line) for line in list2]         # <remove spurious buttons(s) filter />
#list2 = [re.sub(r'^[_\W]?cache[_\W]*$', '', line) for line in list2]            # <remove spurious cache filter />
#list2 = [re.sub(r'^[_\W]?call[_\W]*$', '', line) for line in list2]             # <remove spurious call filter />
#list2 = [re.sub(r'^[_\W]?candy[_\W]*$', '', line) for line in list2]            # <remove spurious candy filter />
#list2 = [re.sub(r'^[_\W]?can[_\W]*$', '', line) for line in list2]              # <remove spurious can filter />
#list2 = [re.sub(r'^[_\W]?caos[_\W]*$', '', line) for line in list2]             # <remove spurious caos filter />
#list2 = [re.sub(r'^[_\W]?capture[_\W]*$', '', line) for line in list2]          # <remove spurious capture filter />
#list2 = [re.sub(r'^[_\W]?cash[_\W]*$', '', line) for line in list2]             # <remove spurious cash filter />
#list2 = [re.sub(r'^[_\W]?cdn[_\W]*$', '', line) for line in list2]              # <remove spurious cdn filter />
#list2 = [re.sub(r'^[_\W]?center[_\W]*$', '', line) for line in list2]           # <remove spurious center filter />
#list2 = [re.sub(r'^[_\W]?c_fill[_\W]*$', '', line) for line in list2]           # <remove spurious c_fill filter />
#list2 = [re.sub(r'^[_\W]?channels?[_\W]*$', '', line) for line in list2]        # <remove spurious channel(s) filter />
#list2 = [re.sub(r'^[_\W]?charts?[_\W]*$', '', line) for line in list2]          # <remove spurious chart(s) filter />
#list2 = [re.sub(r'^[_\W]?check[_\W]*$', '', line) for line in list2]            # <remove spurious check filter />
#list2 = [re.sub(r'^[_\W]?chevron[_\W]*$', '', line) for line in list2]          # <remove spurious chevron filter />
#list2 = [re.sub(r'^[_\W]?china[_\W]*$', '', line) for line in list2]            # <remove spurious china filter />
#list2 = [re.sub(r'^[_\W]?clear[_\W]*$', '', line) for line in list2]            # <remove spurious clear filter />
#list2 = [re.sub(r'^[_\W]?client[_\W]*$', '', line) for line in list2]           # <remove spurious client filter />
#list2 = [re.sub(r'^[_\W]?close[_\W]*$', '', line) for line in list2]            # <remove spurious close filter />
#list2 = [re.sub(r'^[_\W]?cloud[_\W]*$', '', line) for line in list2]            # <remove spurious cloud filter />
#list2 = [re.sub(r'^[_\W]?code[_\W]*$', '', line) for line in list2]             # <remove spurious code filter />
#list2 = [re.sub(r'^[_\W]?cols?[_\W]*$', '', line) for line in list2]            # <remove spurious col(s) filter />
#list2 = [re.sub(r'^[_\W]?combined[_\W]*$', '', line) for line in list2]         # <remove spurious combined filter />
#list2 = [re.sub(r'^[_\W]?common[_\W]*$', '', line) for line in list2]           # <remove spurious common filter />
#list2 = [re.sub(r'^[_\W]?community[_\W]*$', '', line) for line in list2]        # <remove spurious community filter />
#list2 = [re.sub(r'^[_\W]?company[_\W]*$', '', line) for line in list2]          # <remove spurious company filter />
#list2 = [re.sub(r'^[_\W]?components?[_\W]*$', '', line) for line in list2]      # <remove spurious component(s) filter />
#list2 = [re.sub(r'^[_\W]?compress[_\W]*$', '', line) for line in list2]         # <remove spurious compress filter />
#list2 = [re.sub(r'^[_\W]?com[_\W]*$', '', line) for line in list2]              # <remove spurious com filter />
#list2 = [re.sub(r'^[_\W]?config[_\W]*$', '', line) for line in list2]           # <remove spurious config filter />
#list2 = [re.sub(r'^[_\W]?connect[_\W]*$', '', line) for line in list2]          # <remove spurious connect filter />
#list2 = [re.sub(r'^[_\W]?conte[nx]t[_\W]*$', '', line) for line in list2]       # <remove spurious conte(n|x)t filter />
#list2 = [re.sub(r'^[_\W]?control[_\W]*$', '', line) for line in list2]          # <remove spurious control filter />
#list2 = [re.sub(r'^[_\W]?copy(right)[_\W]*$', '', line) for line in list2]      # <remove spurious copy(right) filter />
#list2 = [re.sub(r'^[_\W]?core[_\W]*$', '', line) for line in list2]             # <remove spurious core filter />
#list2 = [re.sub(r'^[_\W]?count[_\W]*$', '', line) for line in list2]            # <remove spurious count filter />
#list2 = [re.sub(r'^[_\W]?cover[_\W]*$', '', line) for line in list2]            # <remove spurious cover filter />
#list2 = [re.sub(r'^[_\W]?cps[_\W]*$', '', line) for line in list2]              # <remove spurious cps filter />
#list2 = [re.sub(r'^[_\W]?create[_\W]*$', '', line) for line in list2]           # <remove spurious create filter />
#list2 = [re.sub(r'^[_\W]?creative[_\W]*$', '', line) for line in list2]         # <remove spurious creative filter />
#list2 = [re.sub(r'^[_\W]?crop[_\W]*$', '', line) for line in list2]             # <remove spurious crop filter />
#list2 = [re.sub(r'^[_\W]?cross[_\W]*$', '', line) for line in list2]            # <remove spurious cross filter />
#list2 = [re.sub(r'^[_\W]?css[_\W]*$', '', line) for line in list2]              # <remove spurious css filter />
#list2 = [re.sub(r'^[_\W]?cta[_\W]*$', '', line) for line in list2]              # <remove spurious cta filter />
#list2 = [re.sub(r'^[_\W]?currency[_\W]*$', '', line) for line in list2]         # <remove spurious currency filter />
#list2 = [re.sub(r'^[_\W]?custom(er)?[_\W]*$', '', line) for line in list2]      # <remove spurious custorm(er) filter />
#list2 = [re.sub(r'^[_\W]?daily[_\W]*$', '', line) for line in list2]            # <remove spurious daily filter />
#list2 = [re.sub(r'^[_\W]?data[_\W]*$', '', line) for line in list2]             # <remove spurious data filter />
#list2 = [re.sub(r'^[_\W]?default[_\W]*$', '', line) for line in list2]          # <remove spurious default filter />
#list2 = [re.sub(r'^[_\W]?delivery[_\W]*$', '', line) for line in list2]         # <remove spurious delivery filter />
#list2 = [re.sub(r'^[_\W]?delo[_\W]*$', '', line) for line in list2]             # <remove spurious delo filter />
#list2 = [re.sub(r'^[_\W]?design[_\W]*$', '', line) for line in list2]           # <remove spurious design filter />
#list2 = [re.sub(r'^[_\W]?desktop[_\W]*$', '', line) for line in list2]          # <remove spurious desktop filter />
#list2 = [re.sub(r'^[_\W]?detail[_\W]*$', '', line) for line in list2]           # <remove spurious detail filter />
#list2 = [re.sub(r'^[_\W]?dev(ices?)?[_\W]*$', '', line) for line in list2]      # <remove spurious dev(ice(s)) filter />
#list2 = [re.sub(r'^[_\W]?digital(ocean)[_\W]*$', '', line) for line in list2]   # <remove spurious digital(ocean) filter />
#list2 = [re.sub(r'^[_\W]?direct[_\W]*$', '', line) for line in list2]           # <remove spurious direct filter />
#list2 = [re.sub(r'^[_\W]?(dis)?play[_\W]*$', '', line) for line in list2]       # <remove spurious (dis)play filter />
#list2 = [re.sub(r'^[_\W]?do[ct][_\W]*$', '', line) for line in list2]           # <remove spurious do(c|t) filter />
#list2 = [re.sub(r'^[_\W]?dollar[_\W]*$', '', line) for line in list2]           # <remove spurious dollar filter />
#list2 = [re.sub(r'^[_\W]?domains?[_\W]*$', '', line) for line in list2]         # <remove spurious domain(s) filter />
#list2 = [re.sub(r'^[_\W]?(down|up)?load(er|s)?[_\W]*$', '', line) for line in list2]  # <remove spurious (down|up)load(er|s) filter />
#list2 = [re.sub(r'^[_\W]?down[_\W]*$', '', line) for line in list2]             # <remove spurious down filter />
#list2 = [re.sub(r'^[_\W]?duckduckgo[_\W]*$', '', line) for line in list2]       # <remove spurious duckduckgo filter />
#list2 = [re.sub(r'^[_\W]?dynamic[_\W]*$', '', line) for line in list2]          # <remove spurious dynamic filter />
#list2 = [re.sub(r'^[_\W]?ebay[_\W]*$', '', line) for line in list2]             # <remove spurious ebay filter />
#list2 = [re.sub(r'^[_\W]?editorial[_\W]*$', '', line) for line in list2]        # <remove spurious editorial filter />
#list2 = [re.sub(r'^[_\W]?elm[_\W]*$', '', line) for line in list2]              # <remove spurious elm filter />
#list2 = [re.sub(r'^[_\W]?e?mail[_\W]*$', '', line) for line in list2]           # <remove spurious (e)mail filter />
#list2 = [re.sub(r'^[_\W]?embed[_\W]*$', '', line) for line in list2]            # <remove spurious embed filter />
#list2 = [re.sub(r'^[_\W]?encart[_\W]*$', '', line) for line in list2]           # <remove spurious encart filter />
#list2 = [re.sub(r'^[_\W]?entry[_\W]*$', '', line) for line in list2]            # <remove spurious entry filter />
#list2 = [re.sub(r'^[_\W]?en.?us[_\W]*$', '', line) for line in list2]           # <remove spurious en(*)us filter />
#list2 = [re.sub(r'^[_\W]?error[_\W]*$', '', line) for line in list2]            # <remove spurious error filter />
#list2 = [re.sub(r'^[_\W]?europa[_\W]*$', '', line) for line in list2]           # <remove spurious europa filter />
#list2 = [re.sub(r'^[_\W]?euro[_\W]*$', '', line) for line in list2]             # <remove spurious euro filter />
#list2 = [re.sub(r'^[_\W]?(ex)?changes?[_\W]*$', '', line) for line in list2]    # <remove spurious (ex)change(s) filter />
#list2 = [re.sub(r'^[_\W]?exe[_\W]*$', '', line) for line in list2]              # <remove spurious exe filter />
#list2 = [re.sub(r'^[_\W]?export[_\W]*$', '', line) for line in list2]           # <remove spurious export filter />
#list2 = [re.sub(r'^[_\W]?express[_\W]*$', '', line) for line in list2]          # <remove spurious express filter />
#list2 = [re.sub(r'^[_\W]?ext(ernal)?[_\W]*$', '', line) for line in list2]      # <remove spurious ext(ernal) filter />
#list2 = [re.sub(r'^[_\W]?extras?[_\W]*$', '', line) for line in list2]          # <remove spurious extra(s)filter />
#list2 = [re.sub(r'^[_\W]?fab[_\W]*$', '', line) for line in list2]              # <remove spurious fab filter />
#list2 = [re.sub(r'^[_\W]?fancybox[_\W]*$', '', line) for line in list2]         # <remove spurious fancybox filter />
#list2 = [re.sub(r'^[_\W]?favicon(\.ico)?[_\W]*$', '', line) for line in list2]  # <remove spurious favicon(.ico) filter />
#list2 = [re.sub(r'^[_\W]?features?[_\W]*$', '', line) for line in list2]        # <remove spurious feature(s) filter />
#list2 = [re.sub(r'^[_\W]?feed(back)[_\W]*$', '', line) for line in list2]       # <remove spurious feed(back) filter />
#list2 = [re.sub(r'^[_\W]?feed[_\W]*$', '', line) for line in list2]             # <remove spurious feed filter />
#list2 = [re.sub(r'^[_\W]?files?[_\W]*$', '', line) for line in list2]           # <remove spurious file(s) filter />
#list2 = [re.sub(r'^[_\W]?film[_\W]*$', '', line) for line in list2]             # <remove spurious film filter />
#list2 = [re.sub(r'^[_\W]?filters?[_\W]*$', '', line) for line in list2]         # <remove spurious filter(s) filter />
#list2 = [re.sub(r'^[_\W]?final[_\W]*$', '', line) for line in list2]            # <remove spurious final filter />
#list2 = [re.sub(r'^[_\W]?fi[tx][_\W]*$', '', line) for line in list2]           # <remove spurious fi(t|x) filter />
#list2 = [re.sub(r'^[_\W]?flash[_\W]*$', '', line) for line in list2]            # <remove spurious flash filter />
#list2 = [re.sub(r'^[_\W]?flipboard[_\W]*$', '', line) for line in list2]        # <remove spurious flipboard filter />
#list2 = [re.sub(r'^[_\W]?follow[_\W]*$', '', line) for line in list2]           # <remove spurious follow filter />
#list2 = [re.sub(r'^[_\W]?fond[_\W]*$', '', line) for line in list2]             # <remove spurious fond filter />
#list2 = [re.sub(r'^[_\W]?font.?awesome[_\W]*$', '', line) for line in list2]    # <remove spurious font(*)awesome filter />
#list2 = [re.sub(r'^[_\W]?fonts?[_\W]*$', '', line) for line in list2]           # <remove spurious font(s) filter />
#list2 = [re.sub(r'^[_\W]?foot(er)?[_\W]*$', '', line) for line in list2]        # <remove spurious foot(er) filter />
#list2 = [re.sub(r'^[_\W]?forum[_\W]*$', '', line) for line in list2]            # <remove spurious forum filter />
#list2 = [re.sub(r'^[_\W]?fotos?[_\W]*$', '', line) for line in list2]           # <remove spurious foto(s) filter />
#list2 = [re.sub(r'^[_\W]?frame[_\W]*$', '', line) for line in list2]            # <remove spurious frame filter />
#list2 = [re.sub(r'^[_\W]?free[_\W]*$', '', line) for line in list2]             # <remove spurious free filter />
#list2 = [re.sub(r'^[_\W]?front(end)?[_\W]*$', '', line) for line in list2]      # <remove spurious front(end) filter />
#list2 = [re.sub(r'^[_\W]?(full)?pages?[_\W]*$', '', line) for line in list2]    # <remove spurious (full)page(s) filter />
#list2 = [re.sub(r'^[_\W]?fullscreen[_\W]*$', '', line) for line in list2]       # <remove spurious fullscreen filter />
#list2 = [re.sub(r'^[_\W]?functions?[_\W]*$', '', line) for line in list2]       # <remove spurious function(s) filter />
#list2 = [re.sub(r'^[_\W]?gallery[_\W]*$', '', line) for line in list2]          # <remove spurious gallery filter />
#list2 = [re.sub(r'^[_\W]?g[ao][_\W]*$', '', line) for line in list2]            # <remove spurious g(a|o) filter />
#list2 = [re.sub(r'^[_\W]?gen(eric)?[_\W]*$', '', line) for line in list2]       # <remove spurious gen(eric) filter />
#list2 = [re.sub(r'^[_\W]?get[_\W]*$', '', line) for line in list2]              # <remove spurious get filter />
#list2 = [re.sub(r'^[_\W]?girls?[_\W]*$', '', line) for line in list2]           # <remove spurious girl(s) filter />
#list2 = [re.sub(r'^[_\W]?github(usercontent)[_\W]*$', '', line) for line in list2]   # <remove spurious github(usercontent) filter />
#list2 = [re.sub(r'^[_\W]?global[_\W]*$', '', line) for line in list2]           # <remove spurious global filter />
#list2 = [re.sub(r'^[_\W]?gomez[_\W]*$', '', line) for line in list2]            # <remove spurious gomez filter />
#list2 = [re.sub(r'^[_\W]?google(apis)?[_\W]*$', '', line) for line in list2]    # <remove spurious google(apis) filter />
#list2 = [re.sub(r'^[_\W]?groups?[_\W]*$', '', line) for line in list2]          # <remove spurious group(s) filter />
#list2 = [re.sub(r'^[_\W]?grupos?[_\W]*$', '', line) for line in list2]          # <remove spurious grupo(s) filter />
#list2 = [re.sub(r'^[_\W]?gstatic[_\W]*$', '', line) for line in list2]          # <remove spurious gstatic filter />
#list2 = [re.sub(r'^[_\W]?head(er)?[_\W]*$', '', line) for line in list2]        # <remove spurious head(er) filter />
#list2 = [re.sub(r'^[_\W]?hero[_\W]*$', '', line) for line in list2]             # <remove spurious hero filter />
#list2 = [re.sub(r'^[_\W]?history[_\W]*$', '', line) for line in list2]          # <remove spurious history filter />
#list2 = [re.sub(r'^[_\W]?home[_\W]*$', '', line) for line in list2]             # <remove spurious home filter />
#list2 = [re.sub(r'^[_\W]?hospital[_\W]*$', '', line) for line in list2]         # <remove spurious hospital filter />
#list2 = [re.sub(r'^[_\W]?html[_\W]*$', '', line) for line in list2]             # <remove spurious html filter />
#list2 = [re.sub(r'^[_\W]?huffingtonpost[_\W]*$', '', line) for line in list2]   # <remove spurious huffingtonpost filter />
#list2 = [re.sub(r'^[_\W]?icons?[_\W]*$', '', line) for line in list2]           # <remove spurious icon(s) filter />
#list2 = [re.sub(r'^[_\W]?icp[_\W]*$', '', line) for line in list2]              # <remove spurious icp filter />
#list2 = [re.sub(r'^[_\W]?iframe[_\W]*$', '', line) for line in list2]           # <remove spurious iframe filter />
#list2 = [re.sub(r'^[_\W]?ima?ge?(ne)?s?[_\W]*$', '', line) for line in list2]   # <remove spurious im(a)g(e)(s) filter />
#list2 = [re.sub(r'^[_\W]?imp[_\W]*$', '', line) for line in list2]              # <remove spurious imp filter />
#list2 = [re.sub(r'^[_\W]?includes?[_\W]*$', '', line) for line in list2]        # <remove spurious include(s) filter />
#list2 = [re.sub(r'^[_\W]?(inc?|out|left|right)[_\W]*$', '', line) for line in list2]  # <remove spurious (in|out|left|right) filter />
#list2 = [re.sub(r'^[_\W]?index[_\W]*$', '', line) for line in list2]            # <remove spurious index filter />
#list2 = [re.sub(r'^[_\W]?infinity[_\W]*$', '', line) for line in list2]         # <remove spurious infinity filter />
#list2 = [re.sub(r'^[_\W]?info[_\W]*$', '', line) for line in list2]             # <remove spurious info filter />
#list2 = [re.sub(r'^[_\W]?init[_\W]*$', '', line) for line in list2]             # <remove spurious init filter />
#list2 = [re.sub(r'^[_\W]?inline[_\W]*$', '', line) for line in list2]           # <remove spurious inline filter />
#list2 = [re.sub(r'^[_\W]?inner[_\W]*$', '', line) for line in list2]            # <remove spurious inner filter />
#list2 = [re.sub(r'^[_\W]?(in|out)put[_\W]*$', '', line) for line in list2]      # <remove spurious (in|out)put filter />
#list2 = [re.sub(r'^[_\W]?instagram[_\W]*$', '', line) for line in list2]        # <remove spurious instagram filter />
#list2 = [re.sub(r'^[_\W]?instant[_\W]*$', '', line) for line in list2]          # <remove spurious instant filter />
#list2 = [re.sub(r'^[_\W]?integration[_\W]*$', '', line) for line in list2]      # <remove spurious integration filter />
#list2 = [re.sub(r'^[_\W]?intelligence[_\W]*$', '', line) for line in list2]     # <remove spurious intelligence filter />
#list2 = [re.sub(r'^[_\W]?intent[_\W]*$', '', line) for line in list2]           # <remove spurious intent filter />
#list2 = [re.sub(r'^[_\W]?inter[_\W]*$', '', line) for line in list2]            # <remove spurious inter filter />
#list2 = [re.sub(r'^[_\W]?intro[_\W]*$', '', line) for line in list2]            # <remove spurious intro filter />
#list2 = [re.sub(r'^[_\W]?i?phone[_\W]*$', '', line) for line in list2]          # <remove spurious (i)phone filter />
#list2 = [re.sub(r'^[_\W]?island[_\W]*$', '', line) for line in list2]           # <remove spurious island filter />
#list2 = [re.sub(r'^[_\W]?items?[_\W]*$', '', line) for line in list2]           # <remove spurious item(s) filter />
#list2 = [re.sub(r'^[_\W]?java(script)?[_\W]*$', '', line) for line in list2]    # <remove spurious java(script) filter />
#list2 = [re.sub(r'^[_\W]?jpe?g[_\W]*$', '', line) for line in list2]            # <remove spurious jpg filter />
#list2 = [re.sub(r'^[_\W]?jquery(\.min)?(\.js)?[_\W]*$', '', line) for line in list2]    # <remove spurious jquery(.min)(.js) filter />
#list2 = [re.sub(r'^[_\W]?js(on)?[_\W]*$', '', line) for line in list2]          # <remove spurious js(on) filter />
#list2 = [re.sub(r'^[_\W]?keyboard[_\W]*$', '', line) for line in list2]         # <remove spurious keyboard filter />
#list2 = [re.sub(r'^[_\W]?labels?[_\W]*$', '', line) for line in list2]          # <remove spurious label(s) filter />
#list2 = [re.sub(r'^[_\W]?landing(.?page)?[_\W]*$', '', line) for line in list2] # <remove spurious landing(page) filter />
#list2 = [re.sub(r'^[_\W]?lang(uage)s?[_\W]*$', '', line) for line in list2]     # <remove spurious lang(uage)(s) filter />
#list2 = [re.sub(r'^[_\W]?large[_\W]*$', '', line) for line in list2]            # <remove spurious large filter />
#list2 = [re.sub(r'^[_\W]?latest[_\W]*$', '', line) for line in list2]           # <remove spurious latest filter />
#list2 = [re.sub(r'^[_\W]?launch[_\W]*$', '', line) for line in list2]           # <remove spurious launch filter />
#list2 = [re.sub(r'^[_\W]?leaderboard[_\W]*$', '', line) for line in list2]      # <remove spurious leaderboard filter />
#list2 = [re.sub(r'^[_\W]?leon?[_\W]*$', '', line) for line in list2]            # <remove spurious leo(n) filter />
#list2 = [re.sub(r'^[_\W]?libraries[_\W]*$', '', line) for line in list2]        # <remove spurious libraries filter />
#list2 = [re.sub(r'^[_\W]?library[_\W]*$', '', line) for line in list2]          # <remove spurious libraryfilter />
#list2 = [re.sub(r'^[_\W]?libs?[_\W]*$', '', line) for line in list2]            # <remove spurious lib(s) filter />
#list2 = [re.sub(r'^[_\W]?li[f|k]e[_\W]*$', '', line) for line in list2]         # <remove spurious li(f|k)e filter />
#list2 = [re.sub(r'^[_\W]?lightbox[_\W]*$', '', line) for line in list2]         # <remove spurious lightbox filter />
#list2 = [re.sub(r'^[_\W]?linkedin[_\W]*$', '', line) for line in list2]         # <remove spurious linkedin filter />
#list2 = [re.sub(r'^[_\W]?links?[_\W]*$', '', line) for line in list2]           # <remove spurious link(s) filter />
#list2 = [re.sub(r'^[_\W]?linux[_\W]*$', '', line) for line in list2]            # <remove spurious linux filter />
#list2 = [re.sub(r'^[_\W]?lists?[_\W]*$', '', line) for line in list2]           # <remove spurious list(s) filter />
#list2 = [re.sub(r'^[_\W]?live[_\W]*$', '', line) for line in list2]             # <remove spurious live filter />
#list2 = [re.sub(r'^[_\W]?loc(al)?[_\W]*$', '', line) for line in list2]         # <remove spurious loc(al) filter />
#list2 = [re.sub(r'^[_\W]?login[_\W]*$', '', line) for line in list2]            # <remove spurious login filter />
#list2 = [re.sub(r'^[_\W]?logo[s0-9]?[_\W]*$', '', line) for line in list2]      # <remove spurious logo(s|0-9) filter />
#list2 = [re.sub(r'^[_\W]?lookup[_\W]*$', '', line) for line in list2]           # <remove spurious lookup filter />
#list2 = [re.sub(r'^[_\W]?lotus[_\W]*$', '', line) for line in list2]            # <remove spurious lotus filter />
#list2 = [re.sub(r'^[_\W]?l?ubuntu[_\W]*$', '', line) for line in list2]         # <remove spurious (l)ubuntu filter />
#list2 = [re.sub(r'^[_\W]?magazin[_\W]*$', '', line) for line in list2]          # <remove spurious magazin filter />
#list2 = [re.sub(r'^[_\W]?main[_\W]*$', '', line) for line in list2]             # <remove spurious main filter />
#list2 = [re.sub(r'^[_\W]?manifest[_\W]*$', '', line) for line in list2]         # <remove spurious manifest filter />
#list2 = [re.sub(r'^[_\W]?maps?[_\W]*$', '', line) for line in list2]            # <remove spurious map(s) filter />
#list2 = [re.sub(r'^[_\W]?mark(et(ing)?)?[_\W]*$', '', line) for line in list2]  # <remove spurious mark(et(ing)) filter />
#list2 = [re.sub(r'^[_\W]?marketplace?[_\W]*$', '', line) for line in list2]     # <remove spurious marketplace filter />
#list2 = [re.sub(r'^[_\W]?master[_\W]*$', '', line) for line in list2]           # <remove spurious master filter />
#list2 = [re.sub(r'^[_\W]?ma[sx][_\W]*$', '', line) for line in list2]           # <remove spurious ma(s|x) filter />
#list2 = [re.sub(r'^[_\W]?measure(ments?)?[_\W]*$', '', line) for line in list2] # <remove spurious measure(ment(s)) filter />
#list2 = [re.sub(r'^[_\W]?menu[_\W]*$', '', line) for line in list2]             # <remove spurious menu filter />
#list2 = [re.sub(r'^[_\W]?message[_\W]*$', '', line) for line in list2]          # <remove spurious message filter />
#list2 = [re.sub(r'^[_\W]?meteoblue[_\W]*$', '', line) for line in list2]        # <remove spurious meteoblue filter />
#list2 = [re.sub(r'^[_\W]?microsoft[_\W]*$', '', line) for line in list2]        # <remove spurious microsoft filter />
#list2 = [re.sub(r'^[_\W]?middle[_\W]*$', '', line) for line in list2]           # <remove spurious middle filter />
#list2 = [re.sub(r'^[_\W]?mini?[_\W]*$', '', line) for line in list2]            # <remove spurious min(i) filter />
#list2 = [re.sub(r'^[_\W]?misc[_\W]*$', '', line) for line in list2]             # <remove spurious misc filter />
#list2 = [re.sub(r'^[_\W]?mobile[_\W]*$', '', line) for line in list2]           # <remove spurious mobile filter />
#list2 = [re.sub(r'^[_\W]?modal[_\W]*$', '', line) for line in list2]            # <remove spurious modal filter />
#list2 = [re.sub(r'^[_\W]?modules?[_\W]*$', '', line) for line in list2]         # <remove spurious module(s) filter />
#list2 = [re.sub(r'^[_\W]?money[_\W]*$', '', line) for line in list2]            # <remove spurious money filter />
#list2 = [re.sub(r'^[_\W]?mon[_\W]*$', '', line) for line in list2]              # <remove spurious mon filter />
#list2 = [re.sub(r'^[_\W]?more[_\W]*$', '', line) for line in list2]             # <remove spurious more filter />
#list2 = [re.sub(r'^[_\W]?mozilla[_\W]*$', '', line) for line in list2]          # <remove spurious mozilla filter />
#list2 = [re.sub(r'^[_\W]?mp[0-9[_\W]*$', '', line) for line in list2]           # <remove spurious mpx filter />
#list2 = [re.sub(r'^[_\W]?(multi)?media[_\W]*$', '', line) for line in list2]    # <remove spurious (multi)media filter />
#list2 = [re.sub(r'^[_\W]?names?[_\W]*$', '', line) for line in list2]           # <remove spurious name(s) filter />
#list2 = [re.sub(r'^[_\W]?native[_\W]*$', '', line) for line in list2]           # <remove spurious native filter />
#list2 = [re.sub(r'^[_\W]?nav[_\W]*$', '', line) for line in list2]              # <remove spurious nav filter />
#list2 = [re.sub(r'^[_\W]?net(work)?[_\W]*$', '', line) for line in list2]       # <remove spurious net(work) filter />
#list2 = [re.sub(r'^[_\W]?news?letter[_\W]*$', '', line) for line in list2]      # <remove spurious new(s)(letter) filter />
#list2 = [re.sub(r'^[_\W]?next[_\W]*$', '', line) for line in list2]             # <remove spurious next filter />
#list2 = [re.sub(r'^[_\W]?nodes?[_\W]*$', '', line) for line in list2]           # <remove spurious node(s) filter />
#list2 = [re.sub(r'^[_\W]?normal[_\W]*$', '', line) for line in list2]           # <remove spurious normal filter />
#list2 = [re.sub(r'^[_\W]?notes?[_\W]*$', '', line) for line in list2]           # <remove spurious note(s) filter />
#list2 = [re.sub(r'^[_\W]?noticias?[_\W]*$', '', line) for line in list2]        # <remove spurious noticia(s) filter />
#list2 = [re.sub(r'^[_\W]?nytimes[_\W]*$', '', line) for line in list2]          # <remove spurious nytimes filter />
#list2 = [re.sub(r'^[_\W]?oil[_\W]*$', '', line) for line in list2]              # <remove spurious oil filter />
#list2 = [re.sub(r'^[_\W]?online[_\W]*$', '', line) for line in list2]           # <remove spurious online filter />
#list2 = [re.sub(r'^[_\W]?open[_\W]*$', '', line) for line in list2]             # <remove spurious open filter />
#list2 = [re.sub(r'^[_\W]?opinions?[_\W]*$', '', line) for line in list2]        # <remove spurious opinion(s) filter />
#list2 = [re.sub(r'^[_\W]?org[_\W]*$', '', line) for line in list2]              # <remove spurious org filter />
#list2 = [re.sub(r'^[_\W]?original[_\W]*$', '', line) for line in list2]         # <remove spurious original filter />
#list2 = [re.sub(r'^[_\W]?orion[_\W]*$', '', line) for line in list2]            # <remove spurious orion filter />
#list2 = [re.sub(r'^[_\W]?overlay[_\W]*$', '', line) for line in list2]          # <remove spurious overlay filter />
#list2 = [re.sub(r'^[_\W]?owa[_\W]*$', '', line) for line in list2]              # <remove spurious owa filter />
#list2 = [re.sub(r'^[_\W]?panels?[_\W]*$', '', line) for line in list2]          # <remove spurious panel(s) filter />
#list2 = [re.sub(r'^[_\W]?parse[_\W]*$', '', line) for line in list2]            # <remove spurious parse filter />
#list2 = [re.sub(r'^[_\W]?particles?[_\W]*$', '', line) for line in list2]       # <remove spurious particle(s) filter />
#list2 = [re.sub(r'^[_\W]?pause[_\W]*$', '', line) for line in list2]            # <remove spurious pause filter />
#list2 = [re.sub(r'^[_\W]?pdp[_\W]*$', '', line) for line in list2]              # <remove spurious pdp filter />
#list2 = [re.sub(r'^[_\W]?photos?[_\W]*$', '', line) for line in list2]          # <remove spurious photo(s) filter />
#list2 = [re.sub(r'^[_\W]?pic(ture)?s?[_\W]*$', '', line) for line in list2]     # <remove spurious pic(ture)(s) filter />
#list2 = [re.sub(r'^[_\W]?pinterest[_\W]*$', '', line) for line in list2]        # <remove spurious pinterest filter />
#list2 = [re.sub(r'^[_\W]?place(holder)?[_\W]*$', '', line) for line in list2]   # <remove spurious place(holder) filter />
#list2 = [re.sub(r'^[_\W]?plan[_\W]*$', '', line) for line in list2]             # <remove spurious plan filter />
#list2 = [re.sub(r'^[_\W]?platform[_\W]*$', '', line) for line in list2]         # <remove spurious platform filter />
#list2 = [re.sub(r'^[_\W]?playas?[_\W]*$', '', line) for line in list2]          # <remove spurious playa(s) filter />
#list2 = [re.sub(r'^[_\W]?player[_\W]*$', '', line) for line in list2]           # <remove spurious player filter />
#list2 = [re.sub(r'^[_\W]?plugins?[_\W]*$', '', line) for line in list2]         # <remove spurious plugin(s) filter />
#list2 = [re.sub(r'^[_\W]?png[_\W]*$', '', line) for line in list2]              # <remove spurious png filter />
#list2 = [re.sub(r'^[_\W]?polls?[_\W]*$', '', line) for line in list2]           # <remove spurious poll(s) filter />
#list2 = [re.sub(r'^[_\W]?portal[_\W]*$', '', line) for line in list2]           # <remove spurious portal filter />
#list2 = [re.sub(r'^[_\W]?positions?[_\W]*$', '', line) for line in list2]       # <remove spurious position(s) filter />
#list2 = [re.sub(r'^[_\W]?post?[_\W]*$', '', line) for line in list2]            # <remove spurious post filter />
#list2 = [re.sub(r'^[_\W]?premium[_\W]*$', '', line) for line in list2]          # <remove spurious premium filter />
#list2 = [re.sub(r'^[_\W]?pre[_\W]*$', '', line) for line in list2]              # <remove spurious pre filter />
#list2 = [re.sub(r'^[_\W]?price[_\W]*$', '', line) for line in list2]            # <remove spurious price filter />
#list2 = [re.sub(r'^[_\W]?primary[_\W]*$', '', line) for line in list2]          # <remove spurious primary filter />
#list2 = [re.sub(r'^[_\W]?process(or)?[_\W]*$', '', line) for line in list2]     # <remove spurious process(or) filter />
#list2 = [re.sub(r'^[_\W]?prod(uct(ion)?s?)?[_\W]*$', '', line) for line in list2]     # <remove spurious prod(uct(ion)(s)) filter />
#list2 = [re.sub(r'^[_\W]?profile[_\W]*$', '', line) for line in list2]          # <remove spurious profile filter />
#list2 = [re.sub(r'^[_\W]?profit[_\W]*$', '', line) for line in list2]           # <remove spurious profit filter />
#list2 = [re.sub(r'^[_\W]?projects?[_\W]*$', '', line) for line in list2]        # <remove spurious project(s) filter />
#list2 = [re.sub(r'^[_\W]?promotion[_\W]*$', '', line) for line in list2]        # <remove spurious promotion filter />
#list2 = [re.sub(r'^[_\W]?proxy[_\W]*$', '', line) for line in list2]            # <remove spurious proxy filter />
#list2 = [re.sub(r'^[_\W]?public[_\W]*$', '', line) for line in list2]           # <remove spurious public filter />
#list2 = [re.sub(r'^[_\W]?publisher[_\W]*$', '', line) for line in list2]        # <remove spurious publisher filter />
#list2 = [re.sub(r'^[_\W]?pulse[_\W]*$', '', line) for line in list2]            # <remove spurious pulse filter />
#list2 = [re.sub(r'^[_\W]?pum[_\W]*$', '', line) for line in list2]              # <remove spurious pum filter />
#list2 = [re.sub(r'^[_\W]?pure[_\W]*$', '', line) for line in list2]             # <remove spurious pure filter />
#list2 = [re.sub(r'^[_\W]?random[_\W]*$', '', line) for line in list2]           # <remove spurious random filter />
#list2 = [re.sub(r'^[_\W]?raw(github)?[_\W]*$', '', line) for line in list2]     # <remove spurious raw(github) filter />
#list2 = [re.sub(r'^[_\W]?react[_\W]*$', '', line) for line in list2]            # <remove spurious react filter />
#list2 = [re.sub(r'^[_\W]?re[cfsv][_\W]*$', '', line) for line in list2]         # <remove spurious re(c|f|s|v) filter />
#list2 = [re.sub(r'^[_\W]?red[_\W]*$', '', line) for line in list2]              # <remove spurious red filter />
#list2 = [re.sub(r'^[_\W]?related[_\W]*$', '', line) for line in list2]          # <remove spurious related filter />
#list2 = [re.sub(r'^[_\W]?render(er)?[_\W]*$', '', line) for line in list2]      # <remove spurious render(er) filter />
#list2 = [re.sub(r'^[_\W]?reporting[_\W]*$', '', line) for line in list2]        # <remove spurious reporting filter />
#list2 = [re.sub(r'^[_\W]?reports?[_\W]*$', '', line) for line in list2]         # <remove spurious report(s) filter />
#list2 = [re.sub(r'^[_\W]?request[_\W]*$', '', line) for line in list2]          # <remove spurious request filter />
#list2 = [re.sub(r'^[_\W]?reset[_\W]*$', '', line) for line in list2]            # <remove spurious reset filter />
#list2 = [re.sub(r'^[_\W]?resizer?[_\W]*$', '', line) for line in list2]         # <remove spurious resize(r) filter />
#list2 = [re.sub(r'^[_\W]?resources?[_\W]*$', '', line) for line in list2]       # <remove spurious resource(s) filter />
#list2 = [re.sub(r'^[_\W]?right[_\W]*$', '', line) for line in list2]            # <remove spurious right filter />
#list2 = [re.sub(r'^[_\W]?rokbox[_\W]*$', '', line) for line in list2]           # <remove spurious rokbox filter />
#list2 = [re.sub(r'^[_\W]?rotate[_\W]*$', '', line) for line in list2]           # <remove spurious rotate filter />
#list2 = [re.sub(r'^[_\W]?rss[_\W]*$', '', line) for line in list2]              # <remove spurious rss filter />
#list2 = [re.sub(r'^[_\W]?rum[_\W]*$', '', line) for line in list2]              # <remove spurious rum filter />
#list2 = [re.sub(r'^[_\W]?s10[_\W]*$', '', line) for line in list2]              # <remove spurious s10 filter />
#list2 = [re.sub(r'^[_\W]?safari[_\W]*$', '', line) for line in list2]           # <remove spurious safari filter />
#list2 = [re.sub(r'^[_\W]?samsung[_\W]*$', '', line) for line in list2]          # <remove spurious samsung filter />
#list2 = [re.sub(r'^[_\W]?screen[_\W]*$', '', line) for line in list2]           # <remove spurious screen filter />
#list2 = [re.sub(r'^[_\W]?scripts?[_\W]*$', '', line) for line in list2]         # <remove spurious script(s) filter />
#list2 = [re.sub(r'^[_\W]?sdk[_\W]*$', '', line) for line in list2]              # <remove spurious sdk filter />
#list2 = [re.sub(r'^[_\W]?search[_\W]*$', '', line) for line in list2]           # <remove spurious search filter />
#list2 = [re.sub(r'^[_\W]?section[_\W]*$', '', line) for line in list2]          # <remove spurious section filter />
#list2 = [re.sub(r'^[_\W]?server?[_\W]*$', '', line) for line in list2]          # <remove spurious serve(r) filter />
#list2 = [re.sub(r'^[_\W]?services?[_\W]*$', '', line) for line in list2]        # <remove spurious service(s) filter />
#list2 = [re.sub(r'^[_\W]?session[_\W]*$', '', line) for line in list2]          # <remove spurious session filter />
#list2 = [re.sub(r'^[_\W]?set[_\W]*$', '', line) for line in list2]              # <remove spurious set filter />
#list2 = [re.sub(r'^[_\W]?shared?[_\W]*$', '', line) for line in list2]          # <remove spurious share(d) filter />
#list2 = [re.sub(r'^[_\W]?show[_\W]*$', '', line) for line in list2]             # <remove spurious show filter />
#list2 = [re.sub(r'^[_\W]?side(bar)[_\W]*$', '', line) for line in list2]        # <remove spurious side(bar) filter />
#list2 = [re.sub(r'^[_\W]?simple[_\W]*$', '', line) for line in list2]           # <remove spurious simple filter />
#list2 = [re.sub(r'^[_\W]?si[tz]es?[_\W]*$', '', line) for line in list2]        # <remove spurious si(t|z)e(s)) filter />
#list2 = [re.sub(r'^[_\W]?skins?[_\W]*$', '', line) for line in list2]           # <remove spurious skin(s)filter />
#list2 = [re.sub(r'^[_\W]?sky[_\W]*$', '', line) for line in list2]              # <remove spurious sky filter />
#list2 = [re.sub(r'^[_\W]?slick[_\W]*$', '', line) for line in list2]            # <remove spurious slick filter />
#list2 = [re.sub(r'^[_\W]?slider[_\W]*$', '', line) for line in list2]           # <remove spurious slider filter />
#list2 = [re.sub(r'^[_\W]?snippets?[_\W]*$', '', line) for line in list2]        # <remove spurious snippet(s)filter />
#list2 = [re.sub(r'^[_\W]?social[_\W]*$', '', line) for line in list2]           # <remove spurious social filter />
#list2 = [re.sub(r'^[_\W]?sources?[_\W]*$', '', line) for line in list2]         # <remove spurious source(s) filter />
#list2 = [re.sub(r'^[_\W]?sp(acer?)?[_\W]*$', '', line) for line in list2]       # <remove spurious sp(ace(r)) filter />
#list2 = [re.sub(r'^[_\W]?specials?[_\W]*$', '', line) for line in list2]        # <remove spurious special(s) filter />
#list2 = [re.sub(r'^[_\W]?speed[_\W]*$', '', line) for line in list2]            # <remove spurious speed filter />
#list2 = [re.sub(r'^[_\W]?split[_\W]*$', '', line) for line in list2]            # <remove spurious split filter />
#list2 = [re.sub(r'^[_\W]?sports?[_\W]*$', '', line) for line in list2]          # <remove spurious sport(s) filter />
#list2 = [re.sub(r'^[_\W]?spotify(cdn)?[_\W]*$', '', line) for line in list2]    # <remove spurious spotify(cdn) filter />
#list2 = [re.sub(r'^[_\W]?sprites?[_\W]*$', '', line) for line in list2]         # <remove spurious sprite(s) filter />
#list2 = [re.sub(r'^[_\W]?sprite[_\W]*$', '', line) for line in list2]           # <remove spurious sprite filter />
#list2 = [re.sub(r'^[_\W]?square[_\W]*$', '', line) for line in list2]           # <remove spurious square filter />
#list2 = [re.sub(r'^[_\W]?src[_\W]*$', '', line) for line in list2]              # <remove spurious src filter />
#list2 = [re.sub(r'^[_\W]?ssl[_\W]*$', '', line) for line in list2]              # <remove spurious ssl filter />
#list2 = [re.sub(r'^[_\W]?start[_\W]*$', '', line) for line in list2]            # <remove spurious start filter />
#list2 = [re.sub(r'^[_\W]?static[_\W]*$', '', line) for line in list2]           # <remove spurious static filter />
#list2 = [re.sub(r'^[_\W]?stats?(istics?)?[_\W]*$', '', line) for line in list2] # <remove spurious stat(s)(istic(s)) filter />
#list2 = [re.sub(r'^[_\W]?status[_\W]*$', '', line) for line in list2]           # <remove spurious status filter />
#list2 = [re.sub(r'^[_\W]?stock[_\W]*$', '', line) for line in list2]            # <remove spurious stock filter />
#list2 = [re.sub(r'^[_\W]?storage[_\W]*$', '', line) for line in list2]          # <remove spurious storage filter />
#list2 = [re.sub(r'^[_\W]?stream[_\W]*$', '', line) for line in list2]           # <remove spurious stream filter />
#list2 = [re.sub(r'^[_\W]?stripe[_\W]*$', '', line) for line in list2]           # <remove spurious stripe filter />
#list2 = [re.sub(r'^[_\W]?studio[_\W]*$', '', line) for line in list2]           # <remove spurious studio filter />
#list2 = [re.sub(r'^[_\W]?styles?[_\W]*$', '', line) for line in list2]          # <remove spurious style(s) filter />
#list2 = [re.sub(r'^[_\W]?submit[_\W]*$', '', line) for line in list2]           # <remove spurious submit filter />
#list2 = [re.sub(r'^[_\W]?support[_\W]*$', '', line) for line in list2]          # <remove spurious support filter />
#list2 = [re.sub(r'^[_\W]?surveys?[_\W]*$', '', line) for line in list2]         # <remove spurious survey(s) filter />
#list2 = [re.sub(r'^[_\W]?sustainability[_\W]*$', '', line) for line in list2]   # <remove spurious sustainability filter />
#list2 = [re.sub(r'^[_\W]?sv[cg][_\W]*$', '', line) for line in list2]           # <remove spurious sv(c|g) filter />
#list2 = [re.sub(r'^[_\W]?symbol[_\W]*$', '', line) for line in list2]           # <remove spurious symbol filter />
#list2 = [re.sub(r'^[_\W]?tab[_\W]*$', '', line) for line in list2]              # <remove spurious tab filter />
#list2 = [re.sub(r'^[_\W]?teams?[_\W]*$', '', line) for line in list2]           # <remove spurious team(s) filter />
#list2 = [re.sub(r'^[_\W]?teaser[_\W]*$', '', line) for line in list2]           # <remove spurious teaser filter />
#list2 = [re.sub(r'^[_\W]?templates?[_\W]*$', '', line) for line in list2]       # <remove spurious template(s)filter />
#list2 = [re.sub(r'^[_\W]?texas[_\W]*$', '', line) for line in list2]            # <remove spurious texas filter />
#list2 = [re.sub(r'^[_\W]?te?xt[_\W]*$', '', line) for line in list2]            # <remove spurious t(e)xt filter />
#list2 = [re.sub(r'^[_\W]?themes?[_\W]*$', '', line) for line in list2]          # <remove spurious theme(s) filter />
#list2 = [re.sub(r'^[_\W]?third[_\W]*$', '', line) for line in list2]            # <remove spurious third filter />
#list2 = [re.sub(r'^[_\W]?thumbs?[_\W]*$', '', line) for line in list2]          # <remove spurious thumb(s) filter />
#list2 = [re.sub(r'^[_\W]?timeline[_\W]*$', '', line) for line in list2]         # <remove spurious timeline filter />
#list2 = [re.sub(r'^[_\W]?timer?[_\W]*$', '', line) for line in list2]           # <remove spurious timer filter />
#list2 = [re.sub(r'^[_\W]?tiny[_\W]*$', '', line) for line in list2]             # <remove spurious tiny filter />
#list2 = [re.sub(r'^[_\W]?tools?[_\W]*$', '', line) for line in list2]           # <remove spurious tool(s) filter />
#list2 = [re.sub(r'^[_\W]?top[_\W]*$', '', line) for line in list2]              # <remove spurious top filter />
#list2 = [re.sub(r'^[_\W]?touch[_\W]*$', '', line) for line in list2]            # <remove spurious touch filter />
#list2 = [re.sub(r'^[_\W]?traffic[_\W]*$', '', line) for line in list2]          # <remove spurious traffic filter />
#list2 = [re.sub(r'^[_\W]?tr(ai)?[_\W]*$', '', line) for line in list2]          # <remove spurious tr(ai) filter />
#list2 = [re.sub(r'^[_\W]?tree[_\W]*$', '', line) for line in list2]             # <remove spurious tree filter />
#list2 = [re.sub(r'^[_\W]?ttf[_\W]*$', '', line) for line in list2]              # <remove spurious ttf filter />
#list2 = [re.sub(r'^[_\W]?twitter[_\W]*$', '', line) for line in list2]          # <remove spurious twitter filter />
#list2 = [re.sub(r'^[_\W]?unblock[_\W]*$', '', line) for line in list2]          # <remove spurious unblock filter />
#list2 = [re.sub(r'^[_\W]?une[_\W]*$', '', line) for line in list2]              # <remove spurious une filter />
#list2 = [re.sub(r'^[_\W]?unique[_\W]*$', '', line) for line in list2]           # <remove spurious unique filter />
#list2 = [re.sub(r'^[_\W]?units?[_\W]*$', '', line) for line in list2]           # <remove spurious unit(s) filter />
#list2 = [re.sub(r'^[_\W]?url[_\W]*$', '', line) for line in list2]              # <remove spurious url filter />
#list2 = [re.sub(r'^[_\W]?users?[_\W]*$', '', line) for line in list2]           # <remove spurious user(s) filter />
#list2 = [re.sub(r'^[_\W]?vam[_\W]*$', '', line) for line in list2]              # <remove spurious vam filter />
#list2 = [re.sub(r'^[_\W]?variations?[_\W]*$', '', line) for line in list2]      # <remove spurious variation(s) filter />
#list2 = [re.sub(r'^[_\W]?vectors?[_\W]*$', '', line) for line in list2]         # <remove spurious vector(s) filter />
#list2 = [re.sub(r'^[_\W]?vendors?[_\W]*$', '', line) for line in list2]         # <remove spurious vendor(s) filter />
#list2 = [re.sub(r'^[_\W]?video(js)?(playblack)?[_\W]*$', '', line) for line in list2] # <remove spurious video(js)(playback) filter />
#list2 = [re.sub(r'^[_\W]?videoplayer[_\W]*$', '', line) for line in list2]      # <remove spurious videoplayer filter />
#list2 = [re.sub(r'^[_\W]?views?[_\W]*$', '', line) for line in list2]           # <remove spurious view(s) filter />
#list2 = [re.sub(r'^[_\W]?vimeo(cdn)?[_\W]*$', '', line) for line in list2]      # <remove spurious vimeo(cdn) filter />
#list2 = [re.sub(r'^[_\W]?vinted[_\W]*$', '', line) for line in list2]           # <remove spurious vinted filter />
#list2 = [re.sub(r'^[_\W]?wait[_\W]*$', '', line) for line in list2]             # <remove spurious wait filter />
#list2 = [re.sub(r'^[_\W]?wall[_\W]*$', '', line) for line in list2]             # <remove spurious wall filter />
#list2 = [re.sub(r'^[_\W]?webp[_\W]*$', '', line) for line in list2]             # <remove spurious webp filter />
#list2 = [re.sub(r'^[_\W]?webresource[_\W]*$', '', line) for line in list2]      # <remove spurious webresource filter />
#list2 = [re.sub(r'^[_\W]?web(site)?[_\W]*$', '', line) for line in list2]       # <remove spurious web(site) filter />
#list2 = [re.sub(r'^[_\W]?whatsapp[_\W]*$', '', line) for line in list2]         # <remove spurious whatsapp filter />
#list2 = [re.sub(r'^[_\W]?widgets?[_\W]*$', '', line) for line in list2]         # <remove spurious widget(s) filter />
#list2 = [re.sub(r'^[_\W]?wiki[pm]edia[_\W]*$', '', line) for line in list2]     # <remove spurious wiki(p|m)edia filter />
#list2 = [re.sub(r'^[_\W]?windows?[_\W]*$', '', line) for line in list2]         # <remove spurious window(s) filter />
#list2 = [re.sub(r'^[_\W]?woff[0-9[?_\W]*$', '', line) for line in list2]        # <remove spurious woff(0-9) filter />
#list2 = [re.sub(r'^[_\W]?word(press)?[_\W]*$', '', line) for line in list2]     # <remove spurious word(press) filter />
#list2 = [re.sub(r'^[_\W]?work(er)?[_\W]*$', '', line) for line in list2]        # <remove spurious work(er) filter />
#list2 = [re.sub(r'^[_\W]?world[_\W]*$', '', line) for line in list2]            # <remove spurious world filter />
#list2 = [re.sub(r'^[_\W]?wp(\-content)?[_\W]*$', '', line) for line in list2]   # <remove spurious wp(-content) filter />
#list2 = [re.sub(r'^[_\W]?www[_\W]*$', '', line) for line in list2]              # <remove spurious www filter />
#list2 = [re.sub(r'^[_\W]?xml[_\W]*$', '', line) for line in list2]              # <remove spurious xml filter />
#list2 = [re.sub(r'^[_\W]?youtube[_\W]*$', '', line) for line in list2]          # <remove spurious youtube filter />
#list2 = [re.sub(r'^[_\W]?zaf[_\W]*$', '', line) for line in list2]              # <remove spurious zaf filter />
#list2 = [re.sub(r'^[_\W]?zalando[_\W]*$', '', line) for line in list2]          # <remove spurious zalando filter />

list2 = [line for line in list2 if len(line) > 1]                               # <remove items if length < 2 />
list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

print('19/20 : add filter to block numerical domains #.@(.@) filters')

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

print('20/20 : add exceptions')

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

list2 = sorted(list2)
print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

# <transforming loop/>

# <remove url filters covered by regex filters>

print('\n', 'Deflating url filters redundant with regex filters', sep = '')

for string in tqdm.tqdm(list5):
    list2 = [line for line in list2 if (re.search(r'(\#|removeparam)', line) or not(re.search(re.sub(r'^/', '', re.sub(r'/(\$important)?$', '', string)), ' ' + line + ' ')))]

print('       ', '{:,}'.format(len(list2) + len(list5)), 'filters kept')

# </remove url filters covered by regex filters>

# <aggregate regex filters>

list2 = sorted(set(list2) | set(list5))

# </aggregate regex filters>

# <extract domains from list>

print('\n', 'Listing domain filters; ', end = '', sep = '')

list3 = [line for line in list2 if re.search(r'^[-\.\w]+\.[a-z]+(\.[a-z]+)?(\$important)?$', line)]
list3 = [line for line in list3 if not(re.search(r'^.*\.js(\$important)?$', line))] # <remove @.js from domains list />
list3 = [line for line in list3 if line[0] != '-']                              # <remove -@.@ from domains list />
list2 = set(list2) - set(list3)                                                 # <only domains part are processed in this section; @.js are kept in list2 />

# </extract domains from list>

# <remove #.@(.@) (numerical domains) and @.@ root domains from list>

print('removing #.@(.@) numerical domain filters, root @.@ and key domains (google.com etc) domains: ', end = '')

list3 = [re.sub(r'^\.', '', line)  for line in list3]                           # <remove leading . preceding domain />
list3 = [re.sub('r\$important$', '', line) for line in list3]                   # <remove trailing $important from domains/>
list3 = [line for line in list3 if not(re.search(r'^([-\.\w]+\.)?[-_0-9]+\.[a-z]+(\.[a-z]+)?$', line))]    # <remove #.@(.@) numerical domains/>
list3 = [line for line in list3 if not(re.search(r'^(com|edu|gob|gou?v|net|org|[a-z]{2})\.(com|edu|gob|gou?v|net|org|[a-z]{2})$', line))]   # <remove @.@ root domains />

# <get domains white list from file, dedup and sort>

list8 = [line.strip() for line in open(file8_in_name, encoding='UTF-8')]        # <populate list; remove leading/trailing spaces />
list8 = [re.sub(r'(^| +)!.*', '', line) for line in list8]                      # <remove comments' />
list8 = [line for line in list8 if line.strip() != '']                          # <discard empty lines />

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
    list3 = [line for line in list3 if len(line) > 0]                           # <cleanup empty lines/>
    list3 = sorted(set(list3r) | set(list3))                                    # <compile deflated domains up to current stage/>
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
del(list3)                                                                      # <clean up; make sure list3 is not used anymore hereafter/>

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

list3 = [line for line in list2 if re.search(r'^[-_\.a-z0-9]+\.[a-z]+(\.[a-z]+)?(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]                   # <remove trailing $important from domain list/>
list3 = [line for line in list3 if not(re.search(r'.*\.js$', line))]            # <remove .*\.js$ from domain list />
list3 = [line for line in list3 if line[0] != '-']                              # <remove -@.@ from domains list />
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

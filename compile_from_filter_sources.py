''' Compile a single deduplicated lock list from url sources '''

# <product backlog>

# <next sprint: dedup urls/>

# </product backlog>

import os                   # Miscellaneous operating system interfaces
import re                   # Regular expression operations
import requests             # Get files using url
import tqdm                 # Progress bar
import math                 # Math functions

# <settings>

file1_in_name    = 'filter_sources'
file2_out_name   = 'compiled_block_list'
file3r3_out_name = '3words_domain_list'
proxy_servers    = {'https': 'http://fw:8080'}

# </settings>

print(
                                                                      '\n',
    '# ============================================================', '\n',
    '# Compile a single deduplicated block list from url sources',    '\n',
    '# ============================================================', '\n',
    '# input : <filter_sources> textfile',                            '\n',
    '# output: <3words_domain_list> textfile, A-Z by @.@',            '\n',
    '# output: <compiled_block_list> textfile, sorted, deduplicated', '\n',
    '# ============================================================', '\n',
    )

# <get filter url sources from file, dedup and sort>

list1 = [line.strip() for line in open(file1_in_name, encoding='UTF-8')]    # <populate lists from sources/>
list1 = [line.strip()               for line in list1 if line != '']        # <remove leading/trailing spaces and discard empty lines/>
list1 = [line                       for line in list1 if line[0] != '!']    # <discard commented lines (leading !)/>
list1 = [re.sub(r'\ !.*', '', line) for line in list1]                      # <remove trailing comments'/>
list1 = sorted(list1)

# </get filter url sources from file, dedup and sort>

# <dump sources to list>

list2 = set()    # <populating list2 as set type ensures no duplication/>
i     = 1        # <counter for uncommented sources/>

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
    response = requests.get(line, proxies=proxy_servers)
    if (response.status_code) :
        list2.update(response.text.split('\n'))

print(
    '\n',
    '{:,}'.format(len(list2)),
    'lines gathered from sources',
    '\n'
    )

del(list1)    # <clean up; make sure list1 is not used anymore hereafter/>

# </dump sources to list>

# <process filter list>

print('Transforming filters (3 pass)')
print('--------------------')

# <transforming loop>

print(' 1/24 : remove leading/trailing/dup spaces')
list2 = [re.sub(r' +', ' ', line).strip() for line in list2]                         # <dedup spaces and remove leading/trailing spaces />
list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />

print(' 2/24 : remove comments')
list2 = [line for line in list2 if line[0] != '!']                                   # <remove uBO style comments />
list2 = [line for line in list2 if line[0] != '[']                                   # <remove not uBO style comments [] />
list2 = [line for line in list2 if line[0] != '#']                                   # <remove not uBO style trailing comments />
list2 = [re.sub(r'#(?!##?).*', '', line) for line in list2]                          # <remove not uBO style trailing comments />
list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />

print(' 3/24 : keep case for cosmetic filters; apply lower case for the remaining')
list2 = (
        [line         for line in list2 if     re.search(r'#', line) ] + 
        [line.lower() for line in list2 if not(re.search(r'#', line))]               # <lower case for all except cosmetics />
        )

print(' 4/24 : keep domains from dns style filters')
list2 = [re.sub(r'^0\.0\.0\.0 ', '', line).strip() for line in list2]                # <remove leading   0.0.0.0 (dns style filter) />
list2 = [re.sub(r'^127\.0\.0\.1 ', '', line).strip() for line in list2]              # <remove leading 127.0.0.1 (dns style filter) />
list2 = [re.sub(r'^\:\:1 ', '', line).strip() for line in list2]                     # <remove leading ::1 (dns style filter) />

print(' 5/24 : remove items containing % about: $badfilter localhost; remove IP4/6')
list2 = [line for line in list2 if not(re.search(r'[,\$]badfilter', line))]          # <remove items with $badfilter />
list2 = [line for line in list2 if not(re.search(r'about\:', line))]                 # <remove items with about: >
list2 = [line for line in list2 if not(re.search(r'\%', line))]                      # <remove items with % >
list2 = [re.sub(r'^([0-9]+\.)+', '', line) for line in list2]                        # <remove IP4 addresses (d.)+ />
list2 = [line for line in list2 if not(re.search(r'\:\:', line))]                    # <remove IP6 addresses :: />
list2 = [line for line in list2 if not(re.search(r'localhost', line))]               # <remove items containing localhost />
list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />

print(' 6/24 : generalize cosmetic filters (*##)')
list2 = [re.sub(r'^.*(?=##)', '*', line) for line in list2]                          # <generalize cosmetic filters (*##) />

print(' 7/24 : remove cosmetic filters (##) and exceptions (@@)')                    # <currently discarded; consider processing (future sprints?)/>
list2 = [re.sub(r'^\*?##(?!\:).*', '', line) for line in list2]                      # <remove cosmetic filters except ##: />
list2 = [re.sub(r'^\*?\@\@.*', '', line) for line in list2]                          # <remove exceptions />

for i in [1,2,3]:                                                                    # <recursive 3 pass loop />

    print(' 8/24 : remove leading http :/+ www. |+ :port ; replace leading .gif .htm . jpg .js .php .png .tiff with * ')
    list2 = [re.sub(r'^\|?http.?\:/+', '/', line).strip() for line in list2]            # <remove leading |http:/+ >
    list2 = [re.sub(r'^\:?/+', '/', line).strip() for line in list2]                    # <remove leading :/+ >
    list2 = [re.sub(r'www\.', '', line).strip() for line in list2]                      # <remove www. />
    list2 = [re.sub(r'^\:[0-9]+/', '', line).strip() for line in list2]                 # <remove leading :port />
    list2 = [re.sub(r'^\|+', '', line).strip() for line in list2]                       # <remove leading |+ >
    list2 = [re.sub(r'^\$', '*$', line).strip() for line in list2]                      # <replace leading $ with *$ />
    list2 = [re.sub(r'^/\$', '*$', line).strip() for line in list2]                     # <replace leading /$ with *$ />
    list2 = [re.sub(r'\.?gif\??', '*', line).strip() for line in list2]                 # <replace leading .gif with * >
    list2 = [re.sub(r'\.?html?\??', '*', line).strip() for line in list2]               # <replace leading .htm with * >
    list2 = [re.sub(r'\.?jpg\??', '*', line).strip() for line in list2]                 # <replace leading .jpg with * >
    list2 = [re.sub(r'\.?js\??', '*', line).strip() for line in list2]                  # <replace leading .js with * >
    list2 = [re.sub(r'\.?php\??', '*', line).strip() for line in list2]                 # <replace leading .php with * >
    list2 = [re.sub(r'\.?png\??', '*', line).strip() for line in list2]                 # <replace leading .png with * >
    list2 = [re.sub(r'\.?tiff\??', '*', line).strip() for line in list2]                # <replace leading .tiff with * >
    list2 = [re.sub(r'\*+', '*', line).strip() for line in list2]                       # <dedup * />
    list2 = [re.sub(r'\*(?=[-\.])', '', line).strip() for line in list2]                # <remove unnecesary leading * />
    list2 = [re.sub(r'\*(?=[a-z0-9])', '', line).strip() for line in list2]             # <remove unnecesary leading * />

    print(' 9/24 : remove $ filters denyallow and ghide exceptions combined with domain=')

    list2s = (
        [line for line in list2 if re.search(r'^/?\*?\$popup.*domain=', line)] +         # <remove popup filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$popunder.*domain=', line)] +      # <remove popunder filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$xhr.*domain=', line)] +           # <remove xhr filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$script.*domain=', line)] +        # <remove script filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$webrtc.*domain=', line)] +        # <remove webrtc filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$image.*domain=', line)] +         # <remove image filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$media.*domain=', line)] +         # <remove media filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$object.*domain=', line)] +        # <remove object filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$websocket.*domain=', line)] +     # <remove websocket filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$redirect.*domain=', line)] +      # <remove redirect filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$(sub)?doc.*domain=', line)] +     # <remove doc filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$1p.*domain=', line)] +            # <remove 1p filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$3p.*domain=', line)] +            # <remove 3p filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$third\-party.*domain=', line)] +  # <remove 3p filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$ping.*domain=', line)] +          # <remove ping filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$refirect.*domain=', line)] +      # <remove redirect filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$.*denyallow', line)] +            # <remove denyallow filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\$.*frame.*domain=', line)] +       # <remove frame filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\&?expire.*domain=', line)] +       # <remove expires filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\&?pre\-?rroll.*domain=', line)] +  # <remove prerroll filters and add domains/>
        [line for line in list2 if re.search(r'^/?\*?\&token.*domain=', line)] +         # <remove token filters and add domains/>
        [line for line in list2 if re.search(r'^/?\@\@\*\$ghide.*domain=', line)]        # <remove ghise exceptions and add domains/>
        )

    list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

    list2s = [re.sub(r'.*domain=', '', line).strip() for line in list2s]                 # <remove leading .*domain=/>
    list2s = [re.sub(r'.*denyallow=', '', line).strip() for line in list2s]              # <remove leading .*denyallow=/>
    list2s = [re.sub(r'\,.*$', '', line).strip() for line in list2s]                     # <remove trailing .*,.*/>
    list2s = [line.split('|') for line in list2s if len(line) > 0]                       # <flatten list'/>
    list2s = [item[0] for line in list2s for item in line]                               # <flatten list'/>

    list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
    del(list2s)

    print('10/24 : remove trailing $ all third-party 3p popup image doc filters')
    list2 = [re.sub(r'\^\$', '$', line).strip() for line in list2]                       # <fix: replace ^$ with $/>
    list2 = [re.sub(r'\|\$', '$', line).strip() for line in list2]                       # <fix: replace |$ with $/>
    list2 = [re.sub(r'\$all$', '', line).strip() for line in list2]                      # <remove trailing $all/>
    list2 = [re.sub(r'\$\~?3p$', '', line).strip() for line in list2]                    # <remove trailing $3p/>
    list2 = [re.sub(r'\$\~?third-party$', '', line).strip() for line in list2]           # <remove trailing $third-party/>
    list2 = [re.sub(r'(?<=.)\$popup$', '', line).strip() for line in list2]              # <remove trailing $popup/>
    list2 = [re.sub(r'(?<=.)\$image$', '', line) for line in list2]                      # <remove trailing $image/>
    list2 = [re.sub(r'\$\~?doc$', '', line).strip() for line in list2]                   # <remove trailing $doc/>
    list2 = [re.sub(r'\$\~?script$', '', line).strip() for line in list2]                # <remove trailing $script/>
    list2 = [re.sub(r'\$\~?xhr$', '', line).strip() for line in list2]                   # <remove trailing $xhr/>
    list2 = [re.sub(r'\$\~?xmlhttprequest$', '', line).strip() for line in list2]        # <remove trailing $xmlhttprequest/>

    print('11/24 : trailing ^ | # *')
    list2 = [re.sub(r'\^$', '', line).strip() for line in list2]                         # <remove trailing ^/>
    list2 = [re.sub(r'\|$', '', line).strip() for line in list2]                         # <remove trailing |/>
    list2 = [re.sub(r'#$', '', line).strip() for line in list2]                          # <remove trailing #/>
    list2 = [re.sub(r'(?<!/)\*$', '', line).strip() for line in list2]                   # <remove trailing */>

    print('12/24 : split domains with urls')

    list2s = [line for line in list2 if re.search(r'^[-_\.a-z0-9]+\.[a-z]+/.*', line)]   # <remove domains with url'/>

    list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

    list2s = (
            [re.sub(r'^[-_\.a-z0-9]+\.[a-z]+/', '/', line) for line in list2s] +         # <isolate url part/>
            [re.sub(r'(?<=\w)/.*', '', line) for line in list2s]                         # <isolate domains part/>
            )

    list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
    del(list2s)

    print('13/24 : split urls with $domains=')

    list2s = [line for line in list2 if re.search(r'^[-_\.\*\/a-z0-9]+\$domain=', line)] # <remove domains with url'/>

    list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

    list2s = (
            [re.sub(r'^.*domain=', '', line) for line in list2s] +                       # <isolate domain list part/>
            [re.sub(r'\$domain=.*', '', line) for line in list2s]                        # <isolate url part/>
            )

    list2s = [line.split('|') for line in list2s]                                        # <flatten list'/>
    list2s = [item[0] for line in list2s for item in line]                               # <flatten list'/>

    list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
    del(list2s)

    print('14/24 : simplify urls keeping just last /* part')

    list2 = [re.sub(r'^(/[\*_])+', '', line) for line in list2]                          # <remove leading reperated /[*_] />
    list2 = [re.sub(r'^[-_\.a-z0-9/]+(?=/[-_\.a-z0-9]+$)', '', line) for line in list2]  # <simplify urls keeping last /* part />

    print('15/24 : replace leading/trailing * ~ , trailing , ,php?')
    list2 = [re.sub(r'^\(?\*\.', '.', line).strip() for line in list2]                   # <replace leading *. with . />
    list2 = [re.sub(r'^\*/', '/', line).strip() for line in list2]                       # <replace leading */ with / />
    list2 = [re.sub(r'^~', '', line) for line in list2]                                  # <remove leading ~ />
    list2 = [re.sub(r'\.\*$', '.', line).strip() for line in list2]                      # <replace trailing .* with ./>
    list2 = [re.sub(r'\*\.$', '*', line).strip() for line in list2]                      # <replace trailing *. with .* />
    list2 = [re.sub(r'[~,]+$', '', line).strip() for line in list2]                      # <remove trailing ~ , />
    list2 = [re.sub(r'\.php\??$', '.', line) for line in list2]                          # <remove trailing .php?/>
    list2 = [re.sub(r'\.ashx\??$', '.', line) for line in list2]                         # <remove trailing .ashx?/>
    list2 = [re.sub(r'\.asp\??$', '.', line) for line in list2]                          # <remove trailing .asp?/>
    list2 = [re.sub(r'\.gif\??$', '.', line) for line in list2]                          # <remove trailing .gif?/>
    list2 = [re.sub(r'\.cgi\??$', '.', line) for line in list2]                          # <remove trailing .cgi?/>
    list2 = [re.sub(r'\.?html?\??$', '.', line) for line in list2]                       # <remove trailing .html?/>

    print('16/24 : remove /api /app /js /*/ lines ')
    list2 = [re.sub(r'^/js$', '', line) for line in list2]                               # <remove /js lines />
    list2 = [re.sub(r'^/api$', '', line) for line in list2]                              # <remove /api lines />
    list2 = [re.sub(r'^/app$', '', line) for line in list2]                              # <remove /app lines />
    list2 = [re.sub(r'^/?[a-z0-9]?/?$', '', line) for line in list2]                     # <remove /*/ lines />
    list2 = [re.sub(r'^[js/\*\.]+$', '', line) for line in list2]                        # <remove lines with combinations of js/*. />
    list2 = [re.sub(r'^[-_\./][0-9]+[-_x\.][0-9]+[-_\./]', '', line) for line in list2]  # <remove dxd and similar />
    list2 = [re.sub(r'^[-_\./x0-9]+$', '', line) for line in list2]                      # <remove [-_\./x0-9] combinations />

    print('17/24 : remove /wp-content/uploads/.*')
    list2 = [re.sub(r'(?<=\w)/wp\-content/uploads/.*', '', line) for line in list2]      # <remove /wp-content/uploads/.*' />

    print('18/24 : remove trailing .php ; cleanup trailing .js')
    list2 = [re.sub(r'domain=$', '', line) for line in list2]                            # <remove trailing $domain= />
    list2 = [re.sub(r'\.js(?![a-z0-9]).*', '.js', line) for line in list2]               # <clean up trailing .js />

    print('19/24 : fix leading .@/ com image net static ')
    list2 = [re.sub(r'^\.?[-_a-z0-9\*]+/', '/', line) for line in list2]                 # <remove leading .?@+/ />
    list2 = [re.sub(r'^com\*?\.?$', '', line) for line in list2]                         # <remove com />
    list2 = [re.sub(r'^/?ima?ge?s?\*?(?=[-_\./])', '', line) for line in list2]          # <remove leading ./image? />
    list2 = [re.sub(r'^net\*?\.?$', '', line) for line in list2]                         # <remove net />
    list2 = [re.sub(r'^/?static\*?(?=[-_\./])', '', line) for line in list2]             # <remove leading ./static? />

    print('20/24 : remove key domains (google.com , etc)')
    list2 = [re.sub(r'^cloudflare.com$', '', line) for line in list2]                    # <remove cloudflare.com />
    list2 = [re.sub(r'^duckduckgo.com$', '', line) for line in list2]                    # <remove duckduckgo.com />
    list2 = [re.sub(r'^google.com$', '', line) for line in list2]                        # <remove google.com />
    list2 = [re.sub(r'^googleapis.com$', '', line) for line in list2]                    # <remove googleapis.com />
    list2 = [re.sub(r'^googlevideo.com$', '', line) for line in list2]                   # <remove googlevideo.com />
    list2 = [re.sub(r'^microsoft.com$', '', line) for line in list2]                     # <remove microsoft.com />
    list2 = [re.sub(r'^mozilla.org$', '', line) for line in list2]                       # <remove mozilla.org />
    list2 = [re.sub(r'^wikipedia.org$', '', line) for line in list2]                     # <remove wikipedia.org />
    list2 = [re.sub(r'^youtube.com$', '', line) for line in list2]                       # <remove youtube.com />

    list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />

    print('21/24 : split , separated domains')

    list2s = [line for line in list2 if re.search(r'\,', line) and not(re.search(r'[\$\&]', line))]    # <remove , separated domains />

    list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

    list2s = [line.split(',') for line in list2s]                                        # <flatten list'/>
    list2s = [item[0] for line in list2s for item in line]                               # <flatten list'/>

    list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
    del(list2s)

print('22/24 : fix /@/ url filters adding trailing *')
list2 = [re.sub(r'(?<=/\w)/$', '/*', line) for line in list2]                        # < fix /@/ ending url filters adding trailing * />

print('23/24 : remove *$ 1p 3p doc frame image media object filters; enforce *$ ping script xhr ')
list2 = [re.sub(r'^\*\$\~?1p.*', '', line) for line in list2]                        # <remove *$1p filters />
list2 = [re.sub(r'^\*\$\~?3p.*', '', line) for line in list2]                        # <remove *$3p filters />
list2 = [re.sub(r'^\*\$\~?(sub)?doc(ument)?.*', '', line) for line in list2]         # <remove *$doc filters />
list2 = [re.sub(r'^\*\$\~?frame.*', '', line) for line in list2]                     # <remove *$frame filters />
list2 = [re.sub(r'^\*\$\~?image.*', '', line) for line in list2]                     # <remove *$image filters />
list2 = [re.sub(r'^\*\$\~?media.*', '', line) for line in list2]                     # <remove *$media filters />
list2 = [re.sub(r'^\*\$\~?object.*', '', line) for line in list2]                    # <remove *$object filters />
list2 = [re.sub(r'^\*\$\~?third\-party.*', '', line) for line in list2]              # <remove *$3p filters />
list2 = [re.sub(r'.*\$csp.*', '*$csp=all', line) for line in list2]                  # <enforce *$csp=all />
list2 = [re.sub(r'^\*\$\~?ping.*', '*$ping', line) for line in list2]                # <enforce *$ping />
list2 = [re.sub(r'^\*\$\~?script.*', '*$script', line) for line in list2]            # <enforce *$script />
list2 = [re.sub(r'^\*\$\~?xhr.*', '*$xhr', line) for line in list2]                  # <enforce general *$xhr />
list2 = [re.sub(r'^\*\$\~?xmlhttprequest.*', '', line) for line in list2]            # <enforce general *$xhr />

list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />

# <transforming loop/>

print(
    '\n',
    '{:,}'.format(len(list2)),
    'filters remaining after transformation',
    '\n'
    )

# <extract domains from list>

print('Listing domain filters: ', end = '')

list3 = [line for line in list2 if re.search(r'^[a-z0-9[-_\.a-z0-9]+\.[a-z]+\.[a-z]+(\$important)?$', line) or re.search(r'^[a-z0-9][-_\.a-z0-9]+\.[a-z]+(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]    # <remove trailing $important from domains/>

print(
    '{:,}'.format(len(list3)),
    'found',
    '\n'
    )

# </extract domains from list>

# <remove redundant domains from list>

print('Dedup domains; this operation could take long time, please wait')
print('---------------------------------------------------------------')

list2  = set(list2) - set(list3)    # <only domains part are processed in this section/>º
list3r = [line for line in list3 if re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z]+$', line)]    # <@.@ domains are elemental items/>

print(
    '{:,}'.format(len(list3r)),
    'elemental @.@ domains found; excluded from recursive domain downsizing'
    )

list3r3 = [line for line in list3 if re.search(r'^[a-z0-9][-_a-z0-9]+\.[a-z0-9][-_a-z0-9]+\.[a-z]+$', line)]    # <@.@.@ domains items/>
list3   = set(list3) - set(list3r) - set(list3r3)    # <elemental domains removed for faster size reduction, and added to final result/>
list3   = sorted(list3, key = lambda x: -len(x))     # <sort by decreasing length for faster size reduction/>

print(
    'recursive domain downsizing',
    '{:2.0f}'.format(1),
    '/',
    '?',
    ';',
    '{:,}'.format(len(list3) + len(list3r3)),
    'domains kept'
    )
list3r3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3r))) == 0) else '', tqdm.tqdm(list3r3)))
list3r3 = [line for line in list3r3 if len(line) > 0]    # <cleanup empty lines/>
list3r  = sorted(set(list3r) | set(list3r3))             # <compile deduplicated domains up to current stage/>

# <write output>

list3r3     = set(list3r3)
list3r3     = sorted(list3r3, key = lambda x: (re.sub(r'^[a-z0-9][-_a-z0-9]+\.', '', x)))    # <sort by a-z @.@/>
file3r3_out = open(file3r3_out_name, 'w')
file3r3_out.writelines(line + '\n' for line in list3r3)
file3r3_out.close()

print(
    'deduplicated 3 words domains (@.@.@) sorted by @.@ saved to textfile <' + file3r3_out_name + '>',
    )

del(list3r3)    # <clean up; make sure list3r3 is not used anymore hereafter/>

# </write output>

i_max = round(math.log((len(list3) + len(list3r)) / 1e5) / math.log(2))
for i in range(i_max, -1, -1) :
    list3_filter = list(set(list3) | set(list3r))
    n = round(len(list3_filter) / (2**i))
    print(
        'recursive domain downsizing',
        '{:2.0f}'.format(i_max + 1 - i + 1),
        '/',
        i_max + 1 + 1,
        ';',
        '{:,}'.format(len(list3)),
        'domains kept'
        )
    # <filter() + map() option>
    list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3_filter[:n]))) == 0) else '', tqdm.tqdm(list3)))
    list3 = [line for line in list3 if len(line) > 0]    # <cleanup empty lines/>
    # </filter() + map() option>
    
    # <filter() + list comprehension option; may worth it a benchmark vs map()?>
    #list3 = [line for line in list3 if len(list(filter(lambda substring: ('.' + substring) in line, tqdm.tqdm(list3_filter[:n])))) == 0]
    # </filter() + list comprehension option>

list2 = sorted(set(list2) | set(list3r) | set(list3))    # <rebuild full list with elemetal domains and shrinked domains part/>

print(
    '\n',
    '{:,}'.format(len(list2)),
    'lines remaining after compilation',
    '\n'
    )

# </remove redundant domains from list>

# <process filter list>

# <save a backup renamed *_old; overwrite if exists>

filelist = os.listdir('.')

if file2_out_name + '_old' in filelist :
    os.remove(file2_out_name + '_old')
    os.rename(file2_out_name, file2_out_name + '_old')

print(
    'Backup saved:',
    file2_out_name + '_old',
    '\n'
    )

# </save a backup renamed *_old; overwrite if exists>

# <write output>

file2_out = open(file2_out_name, 'w')
file2_out.writelines(line + '\n' for line in list2)
file2_out.close()

print(
    'Results saved to textfile <' + file2_out_name + '>',
    '\n'
    )

# </write output>


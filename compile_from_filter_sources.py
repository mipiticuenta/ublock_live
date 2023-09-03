''' Compile a single deduplicated lock list from url sources '''

# <product backlog>

# <next sprint: dedup urls/>

# </product backlog>

import os                   # <miscellaneous operating system interfaces />
import re                   # <regular expression operations />
import requests             # <get files using url />
import tqdm                 # <progress bar />
import math                 # <math functions />

# <settings>

file1_in_name    = 'filter_sources'
file2_out_name   = 'compiled_block_list'
file3r_out_name  = '3words_domain_list'
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

list1 = [line.strip() for line in open(file1_in_name, encoding='UTF-8')]        # <populate source lists; remove leading/trailing spaces />
list1 = [re.sub(r'(^| +)!.*', '', line) for line in list1]                      # <remove comments' />
list1 = [line for line in list1 if line.strip() != '']                          # <discard empty lines />

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
            '                         ',
            '{:,}'.format(len(list2)),
            'cumulated filters'
        )

del(list1)    # <clean up; make sure list1 is not used anymore hereafter/>

# </dump sources to list>

# <process filter list>

print(
    '\n',
    'Transforming filters',
    '--------------------'
    )

# <transforming loop>

print(' 1/20 : remove leading/trailing/dup spaces ')
list2 = [re.sub(r' +', ' ', line).strip() for line in list2]                            # <dedup spaces and remove leading/trailing spaces />
list2 = [line for line in list2 if len(line) > 1]                                       # <remove items if length < 2 />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 2/20 : remove comments ')
list2 = [re.sub(r'(^| +)!.*', '', line) for line in list2]                              # <remove ! comment />
list2 = [re.sub(r'(^| +)#(?!(\?|@|#\:|#\.|##|#\[)).*', '', line) for line in list2]     # <remove # comment; preserve cosmetics and exceptions />
list2 = [re.sub(r'^\[.*', '', line) for line in list2]                                  # <remove [comment] line />
list2 = [re.sub(r'^\{.*', '', line) for line in list2]                                  # <remove {comment} line />
list2 = [re.sub(r'^[^a-z0-9]+$', '', line) for line in list2]                           # <remove lines comprised only by simbols />
list2 = [line for line in list2 if len(line) > 1]                                       # <remove items if length < 2 />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 3/20 : keep domains from dns || #[] style filters ')
list2 = [re.sub(r'^0\.0\.0\.0 ', '', line) for line in list2]                           # <remove leading   0.0.0.0 (dns style filter) />
list2 = [re.sub(r'^127\.0\.0\.1 ', '', line) for line in list2]                         # <remove leading 127.0.0.1 (dns style filter) />
list2 = [re.sub(r'^\:\:1 ', '', line) for line in list2]                                # <remove leading ::1 (dns style filter) />
list2 = [re.sub(r'^\|+', '', line) for line in list2]                                   # <remove leading domain mark (||) />
list2 = (                                                                               # <keep domain from #[] style filter />
    [line[2:-1].strip() for line in list2 if line[0:1] == '#[' and line[-1] == ']'] +
    [line for line in list2 if not(line[0:1] == '#[' and line[-1] == ']')]
    )
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 4/20 : remove items containing % about: $badfilter localhost /wp-content/uploads/; remove http: IP4 IP6 :port/ www')
list2 = [re.sub(r'^[^a-z]+$', '', line) for line in list2]                          # <remove lines comprised only by simbols and numbers />
list2 = [line for line in list2 if not(re.search(r'[,\$]badfilter', line))]         # <remove items comprising $badfilter />
list2 = [line for line in list2 if not(re.search(r'about\:', line))]                # <remove items comprising about: >
list2 = [line for line in list2 if not(re.search(r'\%', line))]                     # <remove items comprising % >
list2 = [re.sub(r'http.?\:/+', '/', line).strip() for line in list2]                # <replace |+http:/+ with / />
list2 = [re.sub(r'^/?([0-9]+\.)+([0-9]+)?', '', line).strip() for line in list2]    # <remove IP4 addresses (d.)+ />
list2 = [line for line in list2 if not(re.search(r'\:+', line))]                    # <remove IP6 addresses :: />
list2 = [re.sub(r'^\:[0-9]+/', '', line).strip() for line in list2]                 # <remove leading :port/ />
list2 = [re.sub(r'www\.', '', line).strip() for line in list2]                      # <remove www. />
list2 = [line for line in list2 if not(re.search(r'localhost', line))]              # <remove items containing localhost />
list2 = [re.sub(r'^.*/wp\-content/uploads/?.*', '', line) for line in list2]        # <remove items containing /wp-content/uploads/' />
list2 = [line for line in list2 if len(line) > 1]                                   # <remove items if length < 2 />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 5/20 : keep case for cosmetic filters; apply lower case for the remaining ')
list2 = (
        [line         for line in list2 if     re.search(r'[#\\]', line) ] + 
        [line.lower() for line in list2 if not(re.search(r'[#\\]', line))]          # <lower case for all except cosmetics and regex />
        )
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 6/20 : generalize cosmetic filters (*##) and exceptions (*#@ *#? *@@) ')
list2 = [re.sub(r'^.*(?=\#[\#\?])', '*', line) for line in list2]                   # <generalize cosmetic (*##) (*#?) />
list2 = [re.sub(r'^.*(?=[\#\@]\@)', '*', line) for line in list2]                   # <generalize exception (*#@) (*@@) />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 7/20 : remove cosmetic filters (##) and exceptions (@@) except *##:')       # <currently discarded; consider processing (future sprints?)/>
list2 = [re.sub(r'^\*?\#\#(?!\:).*', '', line) for line in list2]                   # <remove cosmetic filters except ##: />
list2 = [re.sub(r'^\*?\#\@.*', '', line) for line in list2]                         # <remove #@ exceptions />
list2 = [re.sub(r'^\*?\#\?.*', '', line) for line in list2]                         # <remove #? exceptions />
list2 = [re.sub(r'^\*?\@\@.*', '', line) for line in list2]                         # <remove @@ exceptions />
list2 = [line for line in list2 if len(line) > 1]                                   # <remove items if length < 2 />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 8/20 : split urls with $ domain= ')

list2s = [line for line in list2 if re.search(r'\$.*domain=', line)]                # <gest urls with $ domain= '/>

list2 = set(list2) - set(list2s)                                                    # <segregate removed filters'/>

list2s = (
        [re.sub(r',.*', '', re.sub(r'^.*domain=', '', line)) for line in list2s] +  # <isolate domain list part/>
        [re.sub(r'\$.*', '', line) for line in list2s]                              # <isolate url part/>
        )

list2s = [line.split('|') for line in list2s]                                           # <flatten list'/>
list2s = [item[0] for line in list2s for item in line if line !=[''] and item != '']    # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                            # <join retrieved domains to main list'/>
list2 = [line for line in list2 if len(line) > 1]                                   # <remove items if length < 2 />
del(list2s)

print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print(' 9/20 : remove domain= denyallow= filters and keep the related domains')

list2s = (
    [line for line in list2 if re.search(r'.*domain=', line)] +                     # <select *$ filters />
    [line for line in list2 if re.search(r'.*denyallow=', line)]                    # <select denyallow filters />
    )

list2 = set(list2) - set(list2s)                                                    # <segregate selected filters'/>

list2s = [re.sub(r'.*domain=', '', line).strip() for line in list2s]                # <remove leading .*domain=/>
list2s = [re.sub(r'.*denyallow=', '', line).strip() for line in list2s]             # <remove leading .*denyallow=/>
list2s = [re.sub(r'\,.*$', '', line).strip() for line in list2s]                    # <remove trailing .*,.*/>

list2s = [line.split('|') for line in list2s if len(line) > 0]                          # <flatten list'/>
list2s = [item[0] for line in list2s for item in line if line !=[''] and item != '']    # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                            # <join retrieved domains to main list'/>
list2 = [line for line in list2 if len(line) > 1]                                   # <remove items if length < 2 />
del(list2s)

print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('10/20 : split , separated domains ')

list2 = [re.sub(r'^,', '', line).strip() for line in list2]                                        # <remove leading , />
list2 = [re.sub(r',$', '', line).strip() for line in list2]                                        # <remove trailing , />
list2s = [line for line in list2 if re.search(r'\,', line) and not(re.search(r'[\$\&]', line))]    # <remove , separated domains />

list2 = set(list2) - set(list2s)                                                    # <segregate removed filters'/>

list2s = [line.split(',') for line in list2s]                                           # <flatten list'/>
list2s = [item[0] for line in list2s for item in line if line !=[''] and item != '']    # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                            # <join retrieved domains to main list'/>
del(list2s)

print('       ', '{:,}'.format(len(list2)), 'filters remaining')

n_1 = len(list2) + 1
i   = 0

while n_1 > len(list2):                                                             # <recursive loops up to no further length reduction for list2 />

    i   = i + 1
    n_1 = len(list2)

    print(
        'loop ', i, '\n',
        '-------',
        sep = ''
        )

    print('11/20 : clean up leading symbols numbers asset asp cgi cfm gif htm http image jpg js mp4 php png static tiff www')
    list2 = [re.sub(r'^[-_\:\=\+\~\|\*\!0-9]+[/\.]', '', line) for line in list2]               # <remove leading symbols and numbers preceding / ./>
    list2 = [re.sub(r'^[-_\:\=\+\~\|\!0-9]+(?=\$)', '', line) for line in list2]                # <remove leading symbols and numbers preceding $ />
    list2 = [re.sub(r'^[/\.]?[-_a-z0-9\*](?=[/\.])', '', line).strip() for line in list2]       # <remove leading single -_a-z0-9\* precedng / . />
    list2 = [re.sub(r'^[/\.]\*', '*', line).strip() for line in list2]                          # <remove leading / . if followed by * />
    list2 = [re.sub(r'^\$', '*$', line).strip() for line in list2]                              # <fix leading $ with *$ />
    list2 = [re.sub(r'^[/\.\=\?]\$', '*$', line).strip() for line in list2]                     # <fix leading /$ .$ =$ ?$ with *$ />
    list2 = [re.sub(r'^\.?[-_a-z0-9\*]+/', '/', line) for line in list2]                        # <replace leading @/ with / />
    list2 = [re.sub(r'^[/\.]?assets?\*?[/\.]', '', line) for line in list2]                     # <remove leading asset />
    list2 = [re.sub(r'^\.?aspx?\??(?![a-z0-9])', '*', line).strip() for line in list2]          # <replace leading asp with * >
    list2 = [re.sub(r'^\.?cgi\??(?![a-z0-9])', '*', line).strip() for line in list2]            # <replace leading cgi with * >
    list2 = [re.sub(r'^\.?cfm\??(?![a-z0-9])', '*', line).strip() for line in list2]            # <replace leading cfm with * >
    list2 = [re.sub(r'^\.?gif\??(?![a-z0-9])', '*', line).strip() for line in list2]            # <replace leading gif with * >
    list2 = [re.sub(r'^\.?html?\??(?![a-z0-9])', '*', line).strip() for line in list2]          # <replace leading htm with * >
    list2 = [re.sub(r'^[/\.]?ima?ge?s?\*?(?=[-_\./])', '*', line) for line in list2]            # <replace leading image with * />
    list2 = [re.sub(r'^\.?jpg\??(?![a-z0-9])', '*', line).strip() for line in list2]            # <replace leading jpg with * >
    list2 = [re.sub(r'^[/\.]?js/', '/', line) for line in list2]                                # <replace leading js/ with / />
    list2 = [re.sub(r'^\.?js\??(?![a-z0-9])', '*', line).strip() for line in list2]             # <replace leading js with * >
    list2 = [re.sub(r'^\.?mp[0-9]\??(?![a-z0-9])', '*', line).strip() for line in list2]        # <replace leading mp* with * >
    list2 = [re.sub(r'^\.?php\??(?![a-z0-9])', '*', line).strip() for line in list2]            # <replace leading php with * >
    list2 = [re.sub(r'^\.?png\??(?![a-z0-9])', '*', line).strip() for line in list2]            # <replace leading png with * >
    list2 = [re.sub(r'^[/\.]?static\*?[/\.])', '*', line) for line in list2]                    # <replace leading static with * />
    list2 = [re.sub(r'^\.?tiff\??(?![a-z0-9])', '*', line).strip() for line in list2]           # <replace leading tiff with * >
    list2 = [line for line in list2 if len(line) > 1]                                           # <remove items if length < 2 />
    print('       ', '{:,}'.format(len(list2)), 'filters remaining')

    print('12/20 : clean up trailing ^ | # ~ = ? * , .* ash asp cgi gif htm js php and $ all doc image popup script 3p xhr filters')
    list2 = [re.sub(r'[\^\|\=]\$', '$', line).strip() for line in list2]                 # <fix: replace ^$ |$ =$ with $/>
    list2 = [re.sub(r'\|+\$', '$', line).strip() for line in list2]                      # <fix: replace |$ with $/>
    list2 = [re.sub(r'[#,\~\|\^\?\=]+$', '', line).strip() for line in list2]            # <remove trailing # , ~ | ^ ? = />
    list2 = [re.sub(r'(?<!/)\*$', '', line).strip() for line in list2]                   # <remove trailing * except not-regex markup //*/>
    list2 = [re.sub(r'\.\*$', '.', line).strip() for line in list2]                      # <replace trailing .* with ./>
    list2 = [re.sub(r'\*\.$', '', line).strip() for line in list2]                       # <remove trailing *. />
    list2 = [re.sub(r'\.cgi\??$', '.', line) for line in list2]                          # <remove trailing .cgi?/>
    list2 = [re.sub(r'\.ashx\??$', '.', line) for line in list2]                         # <remove trailing .ashx?/>
    list2 = [re.sub(r'\.asp\??$', '.', line) for line in list2]                          # <remove trailing .asp?/>
    list2 = [re.sub(r'\.gif\??$', '.', line) for line in list2]                          # <remove trailing .gif?/>
    list2 = [re.sub(r'\.?html?\??$', '.', line) for line in list2]                       # <remove trailing .html?/>
    list2 = [re.sub(r'\.js(?![a-z0-9]).*$', '.js', line) for line in list2]              # <clean up trailing .js />
    list2 = [re.sub(r'\.php\??$', '.', line) for line in list2]                          # <remove trailing .php?/>
    list2 = [re.sub(r'(?<!\*)\$\~?\w.*$(?<!important)', '', line) for line in list2]     # <remove specific trailing $ filters except $important />
    list2 = [re.sub(r'\?\*\=.*', '', line).strip() for line in list2]                    # <remove trailing ?*=... />
    list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />
    print('       ', '{:,}'.format(len(list2)), 'filters remaining')

    print('13/20 : split domains with urls ')

    list2s = [line for line in list2 if re.search(r'^[-_\.a-z0-9]+\.[a-z]+/.*', line)]   # <remove domains with url'/>

    list2 = set(list2) - set(list2s)                                                     # <segregate removed filters'/>

    list2s = (
            [re.sub(r'^[-_\.a-z0-9]+\.[a-z]+/', '/', line) for line in list2s] +         # <isolate url part/>
            [re.sub(r'(?<=\w)/.*', '', line) for line in list2s]                         # <isolate domains part/>
            )

    list2 = sorted(set(list2) | set(list2s))                                             # <join retrieved domains to main list'/>
    list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />
    del(list2s)

    print('       ', '{:,}'.format(len(list2)), 'filters remaining')

    print('14/20 : simplify urls and keep just last /* part ')
    list2 = [re.sub(r'\*+', '*', line).strip() for line in list2]                        # <dedup * />
    list2 = [re.sub(r'\.+', '.', line).strip() for line in list2]                        # <dedup . />
    list2 = [re.sub(r'/+', '/', line).strip() for line in list2]                         # <dedup / />
    list2 = [re.sub(r'^[^a-z]+$', '', line).strip() for line in list2]                   # <remove lines comprised only by simbols and numbers />
    list2 = [re.sub(r'^[^a-z]+x[^a-z]+$', '', line) for line in list2]                   # <remove lines comrpised by [^a-z]+x[^a-z]+ combinations />
    list2 = [re.sub(r'^[_\Wjs]+$', '', line) for line in list2]                          # <remove lines comprised by j s symbols combinations />
    list2 = [re.sub(r'^[a-z]{1,3}$', '', line) for line in list2]                        # <remove ^[a-z]{1,3}$ filters />
    list2 = [re.sub(r'^[_\W]?[^ap]?[^dx]?[_\W]?\*?$', '', line) for line in list2]       # <remove 2 chars max [a-z][0-9] sequence filter excluding ad px />
    list2 = [re.sub(r'^[_\W]?a?[^d]?[_\W]?\*?$', '', line) for line in list2]            # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[_\W]?p?[^x]?[_\W]?\*?$', '', line) for line in list2]            # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[_\W]?[^a]?d?[_\W]?\*?$', '', line) for line in list2]            # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[_\W]?[^p]?x?\*?$', '', line) for line in list2]                  # <remove 2 ax pd sequence filter />
    list2 = [re.sub(r'^[^a-z]+x[^a-z]+[/\.]', '', line) for line in list2]               # <remove leading [^a-z]+x[^a-z]+ combinations />
    list2 = [re.sub(r'^[-_\.a-z0-9/]+(?=/[-_\.a-z0-9]+$)', '', line) for line in list2]  # <simplify urls keeping last /* part />
    list2 = [re.sub(r'^[-_/\.a-z0-9]*(\*[-_/\.a-z0-9]*)+$(?<!/\*)', '', line).strip() for line in list2]    # <remove url filters using * wildcard />
    list2 = [line for line in list2 if len(line) > 1]                                    # <remove items if length < 2 />
    print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('15/20 : fix /@/ url filters adding trailing * ')

list2 = [re.sub(r'(/[-_\*a-z0-9]+)/$', r'\1/*', line) for line in list2]            # < fix /word/ ending url filters adding trailing * />

#list2 = (
#    [re.sub(r'/$', '/*', line) for line in list2 if re.search(r'/[-_\*a-z0-9]+/$', line)] +    # < fix /word/ ending url filters adding trailing * />
#    [line for line in list2 if not(re.search(r'/[-_\*a-z0-9]+/$', line))]
#    )

print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('16/20 : split space separated domains ')

list2s = [line for line in list2 if re.search(r' ', line) and not(re.search(r'[\$\&]', line))]    # <remove space separated domains />

list2 = set(list2) - set(list2s)                                                    # <segregate removed filters'/>

list2s = [line.split(' ') for line in list2s]                                       # <flatten list'/>
list2s = [item[0] for line in list2s for item in line if line !=[''] and item != '']    # <flatten list'/>

list2 = sorted(set(list2) | set(list2s))                                            # <join retrieved domains to main list'/>
del(list2s)

print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('17/20 : remove lines leaded by ! # + & ? ^ : ; @ and @.exe @.gif @.jpg @.png @.rar @.zip')
list2 = [re.sub(r'^\|\|', '', line) for line in list2]                              # <remove leading || />
list2 = [re.sub(r'^\!.*', '', line) for line in list2]                              # <remove ! leaded lines />
list2 = [re.sub(r'^#.*', '', line) for line in list2]                               # <remove # leaded lines />
list2 = [re.sub(r'^[/\*]?\+.*', '', line) for line in list2]                        # <remove + leaded lines />
list2 = [re.sub(r'^\*?\&.*', '', line) for line in list2]                           # <remove & leaded lines />
list2 = [re.sub(r'^\*?\?.*', '', line) for line in list2]                           # <remove ? leaded lines />
list2 = [re.sub(r'^\*?\^.*', '', line) for line in list2]                           # <remove ^ leaded lines />
list2 = [re.sub(r'^\*?\:.*', '', line) for line in list2]                           # <remove : leaded lines />
list2 = [re.sub(r'^\*?\;.*', '', line) for line in list2]                           # <remove ; leaded lines />
list2 = [re.sub(r'^[/\*]?\@.*', '', line) for line in list2]                        # <remove @ leaded lines />
list2 = [re.sub(r'^.*\.exe$', '', line) for line in list2]                          # <remove @.exe filters />
list2 = [re.sub(r'^.*\.gif$', '', line) for line in list2]                          # <remove @.gif filters />
list2 = [re.sub(r'^.*\.jpe?g$', '', line) for line in list2]                        # <remove @.jp(e)g filters />
list2 = [re.sub(r'^.*\.png$', '', line) for line in list2]                          # <remove @.png filters />
list2 = [re.sub(r'^.*\.rar$', '', line) for line in list2]                          # <remove @.rar filters />
list2 = [re.sub(r'^.*\.zip$', '', line) for line in list2]                          # <remove @.zip filters />
list2 = [line for line in list2 if len(line) > 1]                                   # <remove items if length < 2 />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('18/20 : arrange *$ filters; keep beacon csp inline-font inline-script object other ping popunder script websocket xhr ')
list2 = [re.sub(r'^\*\$\~?1p.*', '', line) for line in list2]                               # <remove *$1p />
list2 = [re.sub(r'^\*\$\~?3p.*', '', line) for line in list2]                               # <remove *$3p />
list2 = [re.sub(r'^\*\$\~?third\-party.*', '', line) for line in list2]                     # <remove *$3p />
list2 = [re.sub(r'^\*\$\~?beacon.*', '*$beacon', line) for line in list2]                   # <enforce *$beacon />
list2 = [re.sub(r'.*\$csp.*', '*$csp=all', line) for line in list2]                         # <enforce *$csp=all />
list2 = [re.sub(r'^\*\$\~?(sub)?doc(ument)?.*', '', line) for line in list2]                # <remove *$(sub)doc />
list2 = [re.sub(r'^\*\$\~?image.*', '', line) for line in list2]                            # <remove *$image />
list2 = [re.sub(r'^\*\$\~?inline\-font.*', '*$inline-font', line) for line in list2]        # <enforce *$inline-font />
list2 = [re.sub(r'^\*\$\~?inline\-script.*', '*$inline-script', line) for line in list2]    # <enforce *$inline-script />
list2 = [re.sub(r'^\*\$\~?media.*', '', line) for line in list2]                            # <remove *$media />
list2 = [re.sub(r'^\*\$\~?object.*', '*$object', line) for line in list2]                   # <enforce *$object />
list2 = [re.sub(r'^\*\$\~?other.*', '*$other', line) for line in list2]                     # <enforce *$other />
list2 = [re.sub(r'^\*\$\~?ping.*', '*$ping', line) for line in list2]                       # <enforce *$ping />
list2 = [re.sub(r'^\*\$\~?popup.*', '', line) for line in list2]                            # <remove *$popup />
list2 = [re.sub(r'^\*\$\~?popunder.*', '*$popunder', line) for line in list2]               # <enforce *$popunder />
list2 = [re.sub(r'^\*\$\~?script.*', '*$script', line) for line in list2]                   # <enforce *$script />
list2 = [re.sub(r'^\*\$\~?rewrite.*', '', line) for line in list2]                          # <remove *$rewrite />
list2 = [re.sub(r'^\*\$\~?websocket.*', '*$websocket', line) for line in list2]             # <enforce *$websocket />
list2 = [re.sub(r'^\*\$\~?xhr.*', '*$xhr', line) for line in list2]                         # <enforce *$xhr />
list2 = [re.sub(r'^\*\$\~?xmlhttprequest.*', '', line) for line in list2]                   # <enforce *$xhr />
list2 = [re.sub(r'^\*\$important.*', '', line) for line in list2]                           # <remove *$important filters />
list2 = [re.sub(r'^\*\$.*\.js', '', line) for line in list2]                                # <remove *$...js filters />
list2 = [line for line in list2 if len(line) > 1]                                           # <remove items if length < 2 />

print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('19/20 : preserve key domains and urls (google.com , etc) from blocking ')
list2 = [re.sub(r'^[_\W]?ajax[_\W]?\*?$', '', line) for line in list2]              # <remove spurious ajax filter />
list2 = [re.sub(r'^[_\W]?api[_\W]?\*?$', '', line) for line in list2]               # <remove spurious api filter />
list2 = [re.sub(r'^[_\W]?app[_\W]?\*?$', '', line) for line in list2]               # <remove spurious app filter />
list2 = [re.sub(r'^[_\W]?art(icle)?[_\W]?\*?$', '', line) for line in list2]        # <remove spurious art(icle) filter />
list2 = [re.sub(r'^[_\W]?assets?[_\W]?\*?$', '', line) for line in list2]           # <remove spurious base filter />
list2 = [re.sub(r'^[_\W]?base[_\W]?\*?$', '', line) for line in list2]              # <remove spurious base filter />
list2 = [re.sub(r'^[_\W]?bbc[_\W]?\*?$', '', line) for line in list2]               # <remove spurious bbc filter />
list2 = [re.sub(r'^[_\W]?brand(ing)?[_\W]?\*?$', '', line) for line in list2]       # <remove spurious brand(ing) filter />
list2 = [re.sub(r'^[_\W]?cache[_\W]?\*?$', '', line) for line in list2]             # <remove spurious cache filter />
list2 = [re.sub(r'^[_\W]?client[_\W]?\*?$', '', line) for line in list2]            # <remove spurious client filter />
list2 = [re.sub(r'^[_\W]?code[_\W]?\*?$', '', line) for line in list2]              # <remove spurious code filter />
list2 = [re.sub(r'^[_\W]?core[_\W]?\*?$', '', line) for line in list2]              # <remove spurious core filter />
list2 = [re.sub(r'^[_\W]?common[_\W]?\*?$', '', line) for line in list2]            # <remove spurious common filter />
list2 = [re.sub(r'^[_\W]?css[_\W]?\*?$', '', line) for line in list2]               # <remove spurious css filter />
list2 = [re.sub(r'^[_\W]?com[_\W]?\*?$', '', line) for line in list2]               # <remove spurious com filter />
list2 = [re.sub(r'^[_\W]?down[_\W]?\*?$', '', line) for line in list2]              # <remove spurious down filter />
list2 = [re.sub(r'^[_\W]?editorial[_\W]?\*?$', '', line) for line in list2]         # <remove spurious editorial filter />
list2 = [re.sub(r'^[_\W]?embed[_\W]?\*?$', '', line) for line in list2]             # <remove spurious embed filter />
list2 = [re.sub(r'^[_\W]?entry[_\W]?\*?$', '', line) for line in list2]             # <remove spurious entry filter />
list2 = [re.sub(r'^[_\W]?exe[_\W]?\*?$', '', line) for line in list2]               # <remove spurious exe filter />
list2 = [re.sub(r'^[_\W]?ext(ernal)?[_\W]?\*?$', '', line) for line in list2]       # <remove spurious ext(ernal) filter />
list2 = [re.sub(r'^[_\W]?extras?[_\W]?\*?$', '', line) for line in list2]           # <remove spurious extra(s)filter />
list2 = [re.sub(r'^[_\W]?file[_\W]?\*?$', '', line) for line in list2]              # <remove spurious file filter />
list2 = [re.sub(r'^[_\W]?footer[_\W]?\*?$', '', line) for line in list2]            # <remove spurious footer filter />
list2 = [re.sub(r'^[_\W]?front(end)?[_\W]?\*?$', '', line) for line in list2]       # <remove spurious front(end) filter />
list2 = [re.sub(r'^[_\W]?go[_\W]?\*?$', '', line) for line in list2]                # <remove spurious go filter />
list2 = [re.sub(r'^[_\W]?gogle[_\W]?\*?$', '', line) for line in list2]             # <remove spurious gogle filter />
list2 = [re.sub(r'^[_\W]?head(er)?[_\W]?\*?$', '', line) for line in list2]         # <remove spurious head(er) filter />
list2 = [re.sub(r'^[_\W]?home[_\W]?\*?$', '', line) for line in list2]              # <remove spurious home filter />
list2 = [re.sub(r'^[_\W]?ima?ge?s?[_\W]?\*?$', '', line) for line in list2]         # <remove spurious im(a)g(e)(s) filter />
list2 = [re.sub(r'^[_\W]?index[_\W]?\*?$', '', line) for line in list2]             # <remove spurious index filter />
list2 = [re.sub(r'^[_\W]?info[_\W]?\*?$', '', line) for line in list2]              # <remove spurious info filter />
list2 = [re.sub(r'^[_\W]?init[_\W]?\*?$', '', line) for line in list2]              # <remove spurious init filter />
list2 = [re.sub(r'^[_\W]?instagram[_\W]?\*?$', '', line) for line in list2]         # <remove spurious instagram filter />
list2 = [re.sub(r'^[_\W]?javascript[_\W]?\*?$', '', line) for line in list2]        # <remove spurious javascript filter />
list2 = [re.sub(r'^[_\W]?jpe?g[_\W]?\*?$', '', line) for line in list2]             # <remove spurious jpg filter />
list2 = [re.sub(r'^[_\W]?jquery(\.min)?(\.js)?[_\W]?\*?$', '', line) for line in list2]    # <remove spurious jquery(.min) filter />
list2 = [re.sub(r'^[_\W]?jquery(\.js)?[_\W]?\*?$', '', line) for line in list2]     # <remove spurious jquery(.js) filter />
list2 = [re.sub(r'^[_\W]?js[_\W]?\*?$', '', line) for line in list2]                # <remove spurious js filter />
list2 = [re.sub(r'^[_\W]?lists?[_\W]?\*?$', '', line) for line in list2]            # <remove spurious list(s) filter />
list2 = [re.sub(r'^[_\W]?(up)?loads?[_\W]?\*?$', '', line) for line in list2]       # <remove spurious (up)load(s) filter />
list2 = [re.sub(r'^[_\W]?login[_\W]?\*?$', '', line) for line in list2]             # <remove spurious login filter />
list2 = [re.sub(r'^[_\W]?logos?[_\W]?\*?$', '', line) for line in list2]            # <remove spurious logo(s) filter />
list2 = [re.sub(r'^[_\W]?libs?[_\W]?\*?$', '', line) for line in list2]             # <remove spurious lib filter />
list2 = [re.sub(r'^[_\W]?linkedin[_\W]?\*?$', '', line) for line in list2]          # <remove spurious linkedin filter />
list2 = [re.sub(r'^[_\W]?main[_\W]?\*?$', '', line) for line in list2]              # <remove spurious main filter />
list2 = [re.sub(r'^[_\W]?master[_\W]?\*?$', '', line) for line in list2]            # <remove spurious master filter />
list2 = [re.sub(r'^[_\W]?menu[_\W]?\*?$', '', line) for line in list2]              # <remove spurious menu filter />
list2 = [re.sub(r'^[_\W]?microsoft[_\W]?\*?$', '', line) for line in list2]         # <remove spurious microsoft filter />
list2 = [re.sub(r'^[_\W]?mobile[_\W]?\*?$', '', line) for line in list2]            # <remove spurious mobile filter />
list2 = [re.sub(r'^[_\W]?modules?[_\W]?\*?$', '', line) for line in list2]          # <remove spurious module(s) filter />
list2 = [re.sub(r'^[_\W]?mp[0-9[_\W]?\*?$', '', line) for line in list2]            # <remove spurious mpx filter />
list2 = [re.sub(r'^[_\W]?net[_\W]?\*?$', '', line) for line in list2]               # <remove spurious net filter />
list2 = [re.sub(r'^[_\W]?news?[_\W]?\*?$', '', line) for line in list2]             # <remove spurious new(s) filter />
list2 = [re.sub(r'^[_\W]?org[_\W]?\*?$', '', line) for line in list2]               # <remove spurious org filter />
list2 = [re.sub(r'^[_\W]?pages?[_\W]?\*?$', '', line) for line in list2]            # <remove spurious web filter />
list2 = [re.sub(r'^[_\W]?player[_\W]?\*?$', '', line) for line in list2]            # <remove spurious player filter />
list2 = [re.sub(r'^[_\W]?pics?[_\W]?\*?$', '', line) for line in list2]             # <remove spurious pic filter />
list2 = [re.sub(r'^[_\W]?(dis)?play[_\W]?\*?$', '', line) for line in list2]        # <remove spurious (dis)play filter />
list2 = [re.sub(r'^[_\W]?plugins??[_\W]?\*?$', '', line) for line in list2]         # <remove spurious plugin(s) filter />
list2 = [re.sub(r'^[_\W]?png[_\W]?\*?$', '', line) for line in list2]               # <remove spurious png filter />
list2 = [re.sub(r'^[_\W]?resources?[_\W]?\*?$', '', line) for line in list2]        # <remove spurious resource(s) filter />
list2 = [re.sub(r'^[_\W]?sp[_\W]?\*?$', '', line) for line in list2]                # <remove spurious sp filter />
list2 = [re.sub(r'^[_\W]?src[_\W]?\*?$', '', line) for line in list2]               # <remove spurious src filter />
list2 = [re.sub(r'^[_\W]?style[_\W]?\*?$', '', line) for line in list2]             # <remove spurious style filter />
list2 = [re.sub(r'^[_\W]?search[_\W]?\*?$', '', line) for line in list2]            # <remove spurious search filter />
list2 = [re.sub(r'^[_\W]?services?[_\W]?\*?$', '', line) for line in list2]         # <remove spurious service(s) filter />
list2 = [re.sub(r'^[_\W]?skins?[_\W]?\*?$', '', line) for line in list2]            # <remove spurious skin(s)filter />
list2 = [re.sub(r'^[_\W]?specials?[_\W]?\*?$', '', line) for line in list2]         # <remove spurious special(s) filter />
list2 = [re.sub(r'^[_\W]?speed[_\W]?\*?$', '', line) for line in list2]             # <remove spurious speed filter />
list2 = [re.sub(r'^[_\W]?templates?[_\W]?\*?$', '', line) for line in list2]        # <remove spurious template(s)filter />
list2 = [re.sub(r'^[_\W]?thumb[_\W]?\*?$', '', line) for line in list2]             # <remove spurious thumb filter />
list2 = [re.sub(r'^[_\W]?tr[_\W]?\*?$', '', line) for line in list2]                # <remove spurious tr filter />
list2 = [re.sub(r'^[_\W]?txt[_\W]?\*?$', '', line) for line in list2]               # <remove spurious txt filter />
list2 = [re.sub(r'^[_\W]?twitter[_\W]?\*?$', '', line) for line in list2]           # <remove spurious twitter filter />
list2 = [re.sub(r'^[_\W]?uploads[_\W]?\*?$', '', line) for line in list2]           # <remove spurious uploads filter />
list2 = [re.sub(r'^[_\W]?video[_\W]?\*?$', '', line) for line in list2]             # <remove spurious video filter />
list2 = [re.sub(r'^[_\W]?view[_\W]?\*?$', '', line) for line in list2]              # <remove spurious view filter />
list2 = [re.sub(r'^[_\W]?web[_\W]?\*?$', '', line) for line in list2]               # <remove spurious web filter />
list2 = [re.sub(r'^[_\W]?widgets?[_\W]?\*?$', '', line) for line in list2]          # <remove spurious widget(s) filter />
list2 = [re.sub(r'^[_\W]?wp[_\W]?\*?$', '', line) for line in list2]                # <remove spurious wp filter />
list2 = [re.sub(r'^[_\W]?wordpress[_\W]?\*?$', '', line) for line in list2]         # <remove spurious wordpress filter />
list2 = [re.sub(r'^akamai(zed)?\.com$', '', line) for line in list2]                # <remove akamai.com />
list2 = [re.sub(r'^akamai(zed)?(hd)?\.net$', '', line) for line in list2]           # <remove akamai.net />
list2 = [re.sub(r'^apple\.com$', '', line) for line in list2]                       # <remove apple.com />
list2 = [re.sub(r'^blogspot\.(com|net|org|[a-z]{2})$', '', line) for line in list2]     # <remove blogspot.(com|net|org|[a-z]{2}) />
list2 = [re.sub(r'^cloudflare\.(com|net)$', '', line) for line in list2]            # <remove cloudflare.(com|net) />
list2 = [re.sub(r'^cloudfront\.(com|net)$', '', line) for line in list2]            # <remove cloudfront..(com|net) />
list2 = [re.sub(r'^collinsdictionary\.com$', '', line) for line in list2]           # <remove collinsdictionary.com />
list2 = [re.sub(r'^(lite\.)?duckduckgo\.com$', '', line) for line in list2]         # <remove duckduckgo.com />
list2 = [re.sub(r'^elconfidencial\.com$', '', line) for line in list2]              # <remove elconfidencial.com />
list2 = [re.sub(r'^ecestaticos\.com$', '', line) for line in list2]                 # <remove ecestaticos.com />
list2 = [re.sub(r'^expansion\.com$', '', line) for line in list2]                   # <remove expansion.com />
list2 = [re.sub(r'^google\.(com|[a-z]{2})$', '', line) for line in list2]           # <remove google.(com|[a-z]{2}) />
list2 = [re.sub(r'^developper\.google\.com$', '', line) for line in list2]          # <remove google.com />
list2 = [re.sub(r'^apis\.google\.com$', '', line) for line in list2]                # <remove google.com />
list2 = [re.sub(r'^googleapis\.com$', '', line) for line in list2]                  # <remove googleapis.com />
list2 = [re.sub(r'^googlevideo\.com$', '', line) for line in list2]                 # <remove googlevideo.com />
list2 = [re.sub(r'^gstatic\.com$', '', line) for line in list2]                     # <remove googlevideo.com />
list2 = [re.sub(r'^microsoft\.com$', '', line) for line in list2]                   # <remove microsoft.com />
list2 = [re.sub(r'^(developer\.)?mozilla\.org$', '', line) for line in list2]       # <remove mozilla.org />
list2 = [re.sub(r'^tradingview\.com$', '', line) for line in list2]                 # <remove tradingview.com />
list2 = [re.sub(r'^uecdn\.es$', '', line) for line in list2]                        # <remove uecdn.es />
list2 = [re.sub(r'^wikimedia\.org$', '', line) for line in list2]                   # <remove wikimedia.org />
list2 = [re.sub(r'^wikipedia\.org$', '', line) for line in list2]                   # <remove wikipedia.org />
list2 = [re.sub(r'^wordpress\.com$', '', line) for line in list2]                   # <remove wordpress.com />
list2 = [re.sub(r'^/?wp\-content/?(themes/|plugins|uploads/)?\*?$', '', line) for line in list2]   # <remove /wp-content />
list2 = [re.sub(r'^(music\.)?youtube\.com$', '', line) for line in list2]           # <remove (music.)youtube.com />
list2 = [line for line in list2 if len(line) > 1]                                   # <remove items if length < 2 />
print('       ', '{:,}'.format(len(list2)), 'filters remaining')

print('20/20 : adding #.@(.@) filter to block numerical domains ')
list2.append('/^([-_\.a-z0-9]+\.)?[-_0-9]+\.[a-z]+(\.[a-z]+)/')                     # <add filter to block [-_/\.0-9]+\.[a-z]+ domains />

# <transforming loop/>

# <extract domains from list>

print('\n', 'Listing domain filters: ', end = '')

list3 = [line for line in list2 if re.search(r'^[-_\.a-z0-9]+\.[a-z]+(\.[a-z]+)?(\$important)?$', line)]
list3 = [re.sub('r\$important$', '', line) for line in list3]                       # <remove trailing $important from domains/>

print(
    '{:,}'.format(len(list3)),
    'found',
    '\n'
    )

# </extract domains from list>

# <remove #.@(.@) (numerical domains) from list>

print('\n', 'removing #.@(.@) (numerical domain) filters: ', end = '')

list3 = [line for line in list3 if not(re.search(r'^.*\.js$', line))]               # <remove @.js from domains list />
list3 = [line for line in list3 if not(re.search(r'blogspot\.[a-z]+$', line))]      # <remove ^blogspot\.[a-z]+$ from domain list to deflate />
list3 = [line for line in list3 if not(re.search(r'tumbl\.[a-z]+$', line))]         # <remove ^tumblr\.[a-z]+$ from domain list to deflate />
list2 = set(list2) - set(list3)                                                     # <only domains part are processed in this section; @.js are kept in list2 />

list3 = [line for line in list3 if not(re.search(r'^([-_\.a-z0-9]+\.)?[-_0-9]+\.[a-z]+(\.[a-z]+)?$', line))]    # <remove #.@(.@) numerical domains/>
list3 = [line for line in list3 if not(re.search(r'^(com|net|org|[a-z]{2})\.(com|net|org|[a-z]{2})$', line))]   # <remove ^(com|net|org|[a-z]{2})\.(com|net|org|[a-z]{2})$ root domains/>

print(
    '{:,}'.format(len(list3)),
    'domains kept',
    '\n'
    )

# <remove #.@(.@) (numerical domains) from list/>

# <remove redundant domains from list>

print('Domains deflating started; this operation could take long time, please wait')
print('------------------------------------------------------------------')

list3r = [line for line in list3 if re.search(r'^[-_a-z0-9]+\.[a-z]+$', line)]      # <@.@ domains are elemental items/>

print(
    '{:,}'.format(len(list3r)),
    'elemental @.@ domains found; excluded from recursive domain deflating'
    )

list3r3 = [line for line in list3 if re.search(r'^[-_a-z0-9]+\.[a-z0-9][-_a-z0-9]+\.[a-z]+$', line)]    # <@.@.@ domains items/>
list3   = set(list3) - set(list3r) - set(list3r3)                                   # <elemental domains removed for faster size reduction, and added to final result/>
list3   = sorted(list3, key = lambda x: -len(x))                                    # <sort by decreasing length for faster size reduction/>

print(
    'recursive domain deflating',
    '{:2.0f}'.format(1),
    '/',
    '3',
    ';',
    '{:,}'.format(len(list3) + len(list3r) + len(list3r3)),
    'domains kept'
    )
list3r3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3r))) == 0) else '', tqdm.tqdm(list3r3)))
list3r3 = [line for line in list3r3 if len(line) > 0]                               # <cleanup empty lines/>
list3r  = sorted(set(list3r) | set(list3r3))                                        # <compile deduplicated domains up to current stage/>
del(list3r3)    # <clean up; make sure list3r3 is not used anymore hereafter/>

# <write output>

list3r = set(list3r)
list3r = sorted(list3r, key = lambda x: (re.sub(r'^[-_a-z0-9]+\.', '', x)))       # <sort by a-z @.@/>
file3r_out = open(file3r_out_name, 'w')
file3r_out.writelines(line + '\n' for line in list3r)
file3r_out.close()

print(
    'deduplicated 3 words domains (@.@.@) sorted by @.@ saved to textfile <' + file3r_out_name + '>',
    )

# </write output>

print(
    'recursive domain deflating',
    '{:2.0f}'.format(2),
    '/',
    '3',
    ';',
    '{:,}'.format(len(list3) + len(list3r)),
    'domains kept'
    )
list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3r))) == 0) else '', tqdm.tqdm(list3)))
list3 = [line for line in list3 if len(line) > 0]                               # <cleanup empty lines/>
list3 = sorted(set(list3r) | set(list3))                                        # <compile deduplicated domains up to current stage/>
del(list3r)    # <clean up; make sure list3r is not used anymore hereafter/>

list3_filter = list3
print(
    'recursive domain deflating',
    '{:2.0f}'.format(3),
    '/',
    '3',
    ';',
    '{:,}'.format(len(list3)),
    'domains kept'
    )
# <filter() + map() option>
list3 = list(map(lambda line: line if (len(list(filter(lambda substring: ('.' + substring) in line, list3_filter))) == 0) else '', tqdm.tqdm(list3)))
list3 = [line for line in list3 if len(line) > 0]    # <cleanup empty lines/>
# </filter() + map() option>

# <filter() + list comprehension option; may worth it a benchmark vs map()?>
#list3 = [line for line in list3 if len(list(filter(lambda substring: ('.' + substring) in line, tqdm.tqdm(list3_filter[:n])))) == 0]
# </filter() + list comprehension option>

print(
    '{:,}'.format(len(list3)),
    'domains remaining after deflating',
    '\n'
    )

print('removing urls redundant with domains')
list2 = list(map(lambda line: line if (line[1:] not in list3) else '', tqdm.tqdm(list2)))    # <remove urls redundant with domains/>
list2 = [line for line in list2 if len(line) > 0]                                   # <cleanup empty lines/>

list2 = sorted(set(list2) | set(list3))                                             # <rebuild full list with elemetal domains and shrinked domains part/>
del(list3)    # <clean up; make sure list3 is not used anymore hereafter/>

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


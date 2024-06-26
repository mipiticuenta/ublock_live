'''
List links from url
'''

# <product backlog>

# <sprint #1: />
# <sprint #2: />

# </product backlog>

import os                                                                       # <operating system interfaces />
import re                                                                       # <regular expression operations />
import requests                                                                 # <get files using url />
import tqdm                                                                     # <progress bar />
from bs4 import BeautifulSoup                                                   # <handling for urls/>

# <settings>

file1_out_name = 'hrefs_found'
proxy_servers  = {'https': '', 'http': ''}
proxy_servers_alt  = {'https': 'http://fw:8080', 'http': 'http://fw:8080'}

# </settings>

print(
                                                                  '\n',
    '# ============================================================\n',
    '# List links from url                                         \n',
    '# ============================================================\n',
    '# input : url                                                 \n',
    '# output: <hrefs found> file                                  \n',
    '# ============================================================\n',
)

# <test direct connection to internet>

try:
    r = requests.get('https://google.com', timeout = 5, proxies=proxy_servers)
except:
    print('\nUsing alt proxy servers.')
    proxy_servers  = proxy_servers_alt

# </test direct connection to internet>

htmlpage = input('Enter url to examine : ')
response = requests.get(htmlpage, proxies=proxy_servers)
soup = BeautifulSoup(response.text, 'html.parser')

links = []
for link in soup.find_all(attrs={'href': re.compile("http")}):
    links.append(link.get('href'))

links = [re.sub(r'^.*//', '', line) for line in links]
links = [re.sub(r'^www\.', '', line) for line in links]
links = [re.sub(r'/.*$', '', line) for line in links]

links = sorted(set(links))

# <open file1_out file and write header and data>

file1_out = open(file1_out_name, 'w', encoding='UTF-8')

file1_out.write(
      '! hrefs found in ' + htmlpage + '\n'
)

file1_out.writelines(line + '\n' for line in links)
file1_out.close()

print(
    '\n',
    '{:,}'.format(len(links)),
    ' lines written to ',
    file1_out_name,
    '\n',
    sep = ''
)

# </open file1_out file and write header and data>

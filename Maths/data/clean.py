#
# Created by Lithops on 2021/10/5.
#

import os, re
import send2trash

i = (2021, 9, 9)

for f in os.listdir('.'):
    try:
        y, m, d = map(int, re.findall('\d+', f))
    except:
        continue

    if (y, m, d) < i:
        send2trash.send2trash(f)

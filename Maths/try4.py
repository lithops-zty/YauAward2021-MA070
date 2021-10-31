#
# Created by Lithops on 2021/8/24.
#
import json
import datetime

import numpy as np
import matplotlib.pyplot as plt


s = datetime.datetime.strptime('2020/03/30', '%Y/%m/%d') + datetime.timedelta(days=1)

print(s.strftime('%Y/%m/%d'))
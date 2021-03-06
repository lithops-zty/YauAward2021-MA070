#
# Created by Lithops on 2021/6/11.
#

import requests
import matplotlib.pyplot as plt

# https://data.gov.sg/dataset/taxi-availability?view_id=7534780c-e99f-4713-9d87-870071919734&resource_id=9d217820-1350-4032-a7a3-3cd83e222eb7


url = r'https://api.data.gov.sg/v1/transport/taxi-availability'
params = {
    'date_time':  '2019-11-30T04:30:00', #  YYYY-MM-DD[T]HH:mm:ss (SGT)
}

r = requests.get(url, params)

data = r.json()['features'][0]['geometry']['coordinates']

x, y = zip(*data)

plt.scatter(x, y, s=2)
plt.show()

print(x, y)
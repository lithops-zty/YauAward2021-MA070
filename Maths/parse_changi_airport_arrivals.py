#
# Created by Lithops on 2021/8/24.
#

import datetime
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd

from YauAward2021.Maths.util import interpolate
from YauAward2021.Maths.objective1.constants import psg_per_flight


def get_passenger_arrivals(bin_min='60Min'):

    def parse(date='2019/11/30'):
        with open(rf'D:\PyCharmProjects\HCICP\YauAward2021\Maths\changi airport flight arrival {date.replace("/", " ")}.json', 'r') as f:
            data = json.load(f)

        def parse_time(time24):
            return datetime.datetime.strptime(f'{date} {time24}', '%Y/%m/%d %H:%M')

        arrivals = pd.Series(1, index=[parse_time(flight['arrivalTime']['time24']) for flight in data['flights']])
        return arrivals

    # binning
    arrivals = pd.concat([parse('2019/11/29'), parse('2019/11/30'), parse('2019/12/1')])
    arrivals: pd.Series = arrivals.resample(bin_min).count() * psg_per_flight

    arrivals = arrivals.sort_index()

    x = pd.date_range(arrivals.index[0], arrivals.index[-1], freq='1Min')


    # add gaussian noise for model dependency analysis

    values = arrivals.values
    # values += np.random.normal(scale=900, size=values.size)

    return x, interpolate(arrivals.index, values)



if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')
    arrivals_x, arrivals_f = get_passenger_arrivals()
    # plotting

    fig, ax = plt.subplots()

    ax.plot(x, arrivals_f(x))

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('passengers per hour')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

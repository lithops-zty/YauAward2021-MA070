#
# Created by Lithops on 2021/8/24.
#

import datetime
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd

from Maths.util import interpolate, offset
from Maths.objective1.constants import psg_per_flight

data_path = r'D:\PyCharmProjects\HCICP\YauAward2021\Maths\data\\'

def get_passenger_arrivals(date='2019/11/30', bin_min='60Min'):

    def parse(date):
        with open(data_path +date.replace("/", "-") + ' arrival.json', 'r') as f:
            data = json.load(f)

        def parse_time(time24):
            return datetime.datetime.strptime(f'{date} {time24}', '%Y/%m/%d %H:%M')

        arrivals = pd.Series(1, index=[parse_time(flight['arrivalTime']['time24']) for flight in data['flights']])
        return arrivals

    # binning
    arrivals = pd.concat([parse(offset(date, -1)), parse(date), parse(offset(date, 1))])
    arrivals: pd.Series = arrivals.resample(bin_min).count() * psg_per_flight

    arrivals = arrivals.sort_index()

    x = pd.date_range(arrivals.index[0], arrivals.index[-1], freq='1Min')


    # add gaussian noise for model dependency analysis

    values = arrivals.values
    # values += np.random.normal(scale=900, size=values.size)

    return x, interpolate(arrivals.index, values)


begin = '2021/09/01'
end = offset(begin, 1)


if __name__ == '__main__':
    x = pd.date_range(begin, end, freq='1Min')
    arrivals_x, arrivals_f = get_passenger_arrivals(begin)
    # plotting

    fig, ax = plt.subplots()

    ax.plot(x, arrivals_f(x))

    ax.set_title('arrivals')

    ax.set_xlabel(f'time {begin}')
    ax.set_ylabel('passengers per hour')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

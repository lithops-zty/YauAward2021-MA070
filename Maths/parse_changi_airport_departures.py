#
# Created by Lithops on 2021/8/24.
#

import datetime
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd

from YauAward2021.Maths.util import interpolate, offset
from YauAward2021.Maths.objective1.constants import psg_per_flight

data_path = r'D:\PyCharmProjects\HCICP\YauAward2021\Maths\data\\'


def get_passenger_departures(date='2019/11/30', bin_min='60Min'):

    def parse(date='2019/11/30'):
        with open(data_path +date.replace("/", "-") + ' departure.json', 'r') as f:
            data = json.load(f)

        def parse_time(time24):
            return datetime.datetime.strptime(f'{date} {time24}', '%Y/%m/%d %H:%M')

        departures = pd.Series(1, index=[parse_time(flight['departureTime']['time24']) for flight in data['flights']])
        return departures

    # binning
    departures = pd.concat([parse(offset(date, -1)), parse(date), parse(offset(date, 1))])
    departures: pd.Series = departures.resample(bin_min).count() * psg_per_flight

    departures = departures.sort_index()

    x = pd.date_range(departures.index[0], departures.index[-1], freq='1Min')

    return x, interpolate(departures.index, departures.values)




begin = '2021/09/01'
end = offset(begin, 1)


if __name__ == '__main__':
    x = pd.date_range(begin, end, freq='1Min')
    _, departures_f = get_passenger_departures(begin)
    # plotting

    fig, ax = plt.subplots()

    ax.plot(x, departures_f(x))

    ax.set_title('departures')
    ax.set_xlabel(f'time {begin}')
    ax.set_ylabel('passengers per hour')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

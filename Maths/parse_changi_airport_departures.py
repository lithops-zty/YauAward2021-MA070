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


def get_passenger_departures(bin_min='60Min'):

    def parse(date='2019/11/30'):
        with open(rf'D:\PyCharmProjects\HCICP\YauAward2021\Maths\changi airport flight departure {date.replace("/", " ")}.json', 'r') as f:
            data = json.load(f)

        def parse_time(time24):
            return datetime.datetime.strptime(f'{date} {time24}', '%Y/%m/%d %H:%M')

        departures = pd.Series(1, index=[parse_time(flight['departureTime']['time24']) for flight in data['flights']])
        return departures

    # binning
    departures = pd.concat([parse('2019/11/29'), parse('2019/11/30'), parse('2019/12/1')])
    departures: pd.Series = departures.resample(bin_min).count() * psg_per_flight

    departures = departures.sort_index()

    x = pd.date_range(departures.index[0], departures.index[-1], freq='1Min')

    return x, interpolate(departures.index, departures.values)



if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')
    _, departures_f = get_passenger_departures()
    # plotting

    fig, ax = plt.subplots()

    ax.plot(x, departures_f(x))

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('passengers per hour')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

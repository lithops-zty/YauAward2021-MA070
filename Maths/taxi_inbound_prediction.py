#
# Created by Lithops on 2021/8/24.
#
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from YauAward2021.Maths.util import interpolate
from YauAward2021.Maths.parse_changi_airport_departures import get_passenger_departures
from YauAward2021.Maths.objective1.constants import dep_offset_hours, k_t_day, k_t_night, psg_per_taxi


def is_day(time: datetime.datetime):
    return datetime.time(5, 0, 0) <= time.time() < datetime.time(23, 0, 0)


def K(t):
    def r(x):
        return k * (1 - np.exp(-(x - 22) ** 2 / 16))

    k = 0.15
    if 5 < t < 22:
        return k
    elif 22 <= t <= 24:
        return k + r(t)
    else:
        return k + r(t + 24)


def get_taxi_inbounds(x, departures_f):
    new_x = x.map(lambda x: x - datetime.timedelta(hours=dep_offset_hours))

    def inbound_f(times):
        return times.map(lambda time: departures_f(time + datetime.timedelta(hours=dep_offset_hours)) * K(time.hour) / psg_per_taxi)

    sample_x = pd.date_range(new_x[0], new_x[-1], periods=24 * 3)

    return new_x, interpolate(sample_x, inbound_f(sample_x) / 2)


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    x_,  departures_f = get_passenger_departures()

    _, inbound_f = get_taxi_inbounds(x_, departures_f)

    fig, ax = plt.subplots()



    ax.plot(x, inbound_f(x), c='r')


    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('taxi inbound per hour')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()


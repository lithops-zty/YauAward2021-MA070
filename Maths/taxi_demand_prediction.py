#
# Created by Lithops on 2021/8/24.
#
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from Maths.util import interpolate
from Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from Maths.objective1.constants import arr_offset_hours, k_t_day, k_t_night, psg_per_taxi


def is_day(time: datetime.datetime):
    return datetime.time(5, 0, 0) <= time.time() < datetime.time(23, 0, 0)


def K(t):
    def r(x):
        return k * (1 - np.exp(-(x - 22) ** 2 / 16))

    k = 0.15
    if 6 < t < 22:
        return k
    elif 22 <= t <= 24:
        return k + r(t)
    else:
        return k + r(t + 24)


def get_taxi_demands(x, arrivals_f):
    #  formula: rho_r(t) =
    new_x = x.map(lambda x: x + datetime.timedelta(hours=arr_offset_hours))

    def demands_f(times):
        if isinstance(times, (float, int)):
            return demands_f(pd.Timestamp.utcfromtimestamp(times))
        elif isinstance(times, (pd.DatetimeIndex, pd.Index)):
            return pd.Series(times).apply(demands_f)
        elif isinstance(times, pd.Timestamp):
            return arrivals_f(times - datetime.timedelta(hours=arr_offset_hours)) * K(times.hour) / psg_per_taxi

    sample_x = pd.date_range(new_x[0], new_x[-1], periods=24 * 3)
    return new_x, interpolate(sample_x, demands_f(sample_x))


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals()

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)

    fig, ax = plt.subplots()

    ax.plot(x, demands_f(x), c='r')

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('taxi demand per hour')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

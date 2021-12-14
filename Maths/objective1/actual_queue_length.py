#
# Created by Lithops on 2021/8/25.
#
import datetime

import numpy as np
import pandas as pd
import scipy.integrate

from Maths.util import to_epoch
from Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from Maths.parse_changi_airport_departures import get_passenger_departures
from Maths.taxi_demand_prediction import get_taxi_demands
from Maths.taxi_inbound_prediction import get_taxi_inbounds
from Maths.objective1.constants import t_l, n0
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_actual_q_len(x, inbounds_f, demands_f):
    # filter away the last t_l minutes' data
    new_x = x[x + datetime.timedelta(minutes=t_l) < x[-1]]

    def actual_q_len_f(times):

        def f(time):
            return inbounds_f(time) / 2 - demands_f(time)

        #  note: need to divide by 3600 because x axis is epoch seconds while y axis is cars/hour.
        if isinstance(times, (float, int)):
            return actual_q_len_f(pd.Timestamp.utcfromtimestamp(times))
        elif isinstance(times, (pd.DatetimeIndex, np.ndarray)):
            # # sliding window speedup, still slow
            # window = (0, 0)
            # integral = 0
            # ret = []
            # for i, time in enumerate(times):
            #     print(i)
            #     new_window = (time, time + datetime.timedelta(minutes=t_l))
            #     left = (window[0], new_window[0])
            #     right = (window[1], new_window[1])
            #     left_aug = scipy.integrate.quad(f, to_epoch(left[0]), to_epoch(left[1]), epsrel=0.05)[0] / 3600 + n0
            #     right_aug = scipy.integrate.quad(f, to_epoch(right[0]), to_epoch(right[1]), epsrel=0.05)[0] / 3600 + n0
            #     integral = integral + right_aug - left_aug
            #     ret.append(integral)
            #     window = new_window
            # return pd.Series(ret)

            return pd.Series(times).apply(actual_q_len_f)

        elif isinstance(times, pd.Timestamp):
            start_time = times
            end_time = times + datetime.timedelta(minutes=t_l)
            sample_x = pd.date_range(start_time, end_time, freq='1Min')
            sample_y = f(sample_x)
            return max(0, scipy.integrate.simpson(sample_y, to_epoch(sample_x)) / 3600 + n0) / inbounds_f(times)

            # return scipy.integrate.quad(f,
            #                             to_epoch(times), to_epoch(times + datetime.timedelta(minutes=t_l)))[
            #            0] / 3600 + n0

    return new_x, actual_q_len_f


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals()
    departures_x, departures_f = get_passenger_departures()

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)
    inbounds_x, inbounds_f = get_taxi_inbounds(departures_x, departures_f)


    actual_q_len_x, actual_q_len_f = get_actual_q_len(x, inbounds_f, demands_f)

    fig, ax = plt.subplots()

    ax.plot(x, actual_q_len_f(x))

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('actual queue length')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

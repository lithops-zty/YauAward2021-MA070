#
# Created by Lithops on 2021/8/25.
#
import datetime

import pandas as pd
import scipy.integrate

from YauAward2021.Maths.util import to_epoch
from YauAward2021.Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from YauAward2021.Maths.taxi_demand_prediction import get_taxi_demands
from YauAward2021.Maths.objective1.constants import t_l
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_expected_q_len(x, demands_f):
    # filter away the last t_l minutes' data
    new_x = x[x + datetime.timedelta(minutes=t_l) < x[-1]]

    def expected_q_len_f(times):
        #  note: need to divide by 3600 because x axis is epoch seconds while y axis is cars/hour.
        if isinstance(times, (float, int)):
            return expected_q_len_f(pd.Timestamp.utcfromtimestamp(times))
        elif isinstance(times, pd.DatetimeIndex):
            # print(times)
            return pd.Series(times).apply(expected_q_len_f)

        elif isinstance(times, pd.Timestamp):
            start_time = times
            end_time = times + datetime.timedelta(minutes=t_l)
            sample_x = pd.date_range(start_time, end_time, freq='1Min')
            sample_y = demands_f(sample_x)
            return scipy.integrate.simpson(sample_y, to_epoch(sample_x)) / 3600

            # return scipy.integrate.quad(demands_f, to_epoch(times), to_epoch(times + datetime.timedelta(minutes=t_l)))[0] / 3600

    return new_x, expected_q_len_f





if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    _, arrivals_f = get_passenger_arrivals()
    _, demands_f = get_taxi_demands(x, arrivals_f)

    _, expected_q_len_f = get_expected_q_len(x, demands_f)

    fig, ax = plt.subplots()


    ax.plot(x, expected_q_len_f(x))

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('expected queue length')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

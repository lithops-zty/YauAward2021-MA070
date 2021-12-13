#
# Created by Lithops on 2021/8/26.
#

import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.integrate

from YauAward2021.Maths.util import to_epoch, get_intercepts, plot_intercepts
from YauAward2021.Maths.objective1.actual_queue_length import get_actual_q_len
from YauAward2021.Maths.objective3.constants import P_A_prime, psi, X_A, t_dA
from YauAward2021.Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from YauAward2021.Maths.parse_changi_airport_departures import get_passenger_departures
from YauAward2021.Maths.taxi_demand_prediction import get_taxi_demands
from YauAward2021.Maths.taxi_inbound_prediction import get_taxi_inbounds


def get_q_jump_pos(x, demands_f, *, gamma):
    new_x = x

    def q_jump_pos(times):

        t_l_prime = (P_A_prime + - 2 * gamma * psi * X_A) / (12.6 / 19 * (1 - psi / 1.26)) - 2 * gamma * t_dA

        if isinstance(times, (float, int)):
            return q_jump_pos(pd.Timestamp.utcfromtimestamp(times))
        elif isinstance(times, (pd.DatetimeIndex, np.ndarray)):
            return pd.Series(times).apply(q_jump_pos)

        elif isinstance(times, pd.Timestamp):
            start_time = times
            end_time = times + datetime.timedelta(minutes=t_l_prime)
            sample_x = pd.date_range(start_time, end_time, periods=50)
            sample_y = demands_f(sample_x)
            # print(sample_y)
            # print(scipy.integrate.simpson(sample_y, to_epoch(sample_x)) / 3600)
            return max(0, scipy.integrate.simpson(sample_y, to_epoch(sample_x)) / 3600)

    return new_x, q_jump_pos


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals()
    departures_x, departures_f = get_passenger_departures()

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)

    inbounds_x, inbounds_f = get_taxi_inbounds(departures_x, departures_f)

    actual_q_len_x, actual_q_len_f = get_actual_q_len(x, inbounds_f, demands_f)

    fig, ax = plt.subplots()

    q_jump_pos_x, q_jump_pos_f = get_q_jump_pos(x, demands_f, gamma=0.2)
    q_jump_pos_x, q_jump_pos_f2 = get_q_jump_pos(x, demands_f, gamma=0.4)

    actual_q_len = actual_q_len_f(x)
    q_jump_pos = q_jump_pos_f(x)
    q_jump_pos2 = q_jump_pos_f2(x)


    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    ax.plot(x, q_jump_pos, label='jump-in position when $\gamma$=0.2', linestyle='--')
    ax.plot(x, q_jump_pos2, label='jump-in position when $\gamma$=0.4', linestyle='--')
    ax.plot(x, actual_q_len, label='actual queue length')

    # plot_intercepts(ax, x, actual_q_len, q_jump_pos)
    # plot_intercepts(ax, x, actual_q_len, q_jump_pos2)

    sample_x = np.array(pd.date_range('2019/11/30 09:00', '2019/11/30 18:00', 4))
    print(sample_x)
    sample_ys = np.c_[actual_q_len_f(sample_x), q_jump_pos_f(sample_x), q_jump_pos_f2(sample_x)]
    print(str(sample_ys.astype(int).T).replace('[', '').replace(']', '').replace(' ', '\t'))

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('cars')

    ax.legend()


    plt.show()

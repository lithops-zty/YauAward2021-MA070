#
# Created by Lithops on 2021/10/29.
#
import pandas as pd
import scipy.integrate as si
import scipy.misc
from numpy import sin, tan, cos, log
import numpy as np
import scipy.interpolate

import matplotlib.dates as mdates

import matplotlib.pyplot as plt

from Maths.objective1.actual_queue_length import get_actual_q_len
from Maths.objective1.constants import t_di, t_dA, t_e, X_A, psi, P_A, P_i, X_i
from Maths.objective1.expected_queue_length import get_expected_q_len
from Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from Maths.parse_changi_airport_departures import get_passenger_departures
from Maths.taxi_demand_prediction import get_taxi_demands
from Maths.taxi_inbound_prediction import get_taxi_inbounds
from Maths.util import interpolate


def get_actual_waiting_time(x, actual_q_len_f, demands_f):
    x2 = np.array((x - x[0]).astype('int') / 1e9 / 3600).reshape(-1)  # h

    demands = demands_f(x)
    tmp_f = scipy.interpolate.interp1d(x2, demands, kind='cubic', bounds_error=False)

    demands_int = np.array(si.odeint(lambda yy, xx: tmp_f(xx), 0, x2)).reshape(-1)

    new_x = x[~np.isnan(demands_int)]
    demands_int = demands_int[~np.isnan(demands_int)]

    demands_intf = interpolate(new_x, demands_int)

    last = new_x[-1].timestamp()

    def actual_waiting_time_f(times):
        if isinstance(times, (float, int)):
            # binary search
            o = demands_intf(times)
            l = times
            r = last
            target = actual_q_len_f(times)
            while abs(r - l) > 0.1 and last - l > 0.1:
                m = (l + r) / 2
                v = demands_intf(m) - o
                if v > target:
                    r = m
                else:
                    l = m

            return l - times
        elif isinstance(times, (pd.DatetimeIndex, np.ndarray)):
            return pd.Series(times).apply(actual_waiting_time_f)
        elif isinstance(times, pd.Timestamp):
            return actual_waiting_time_f(times.timestamp())

    return new_x, actual_waiting_time_f


def get_n(x, actual_waiting_time_f):
    def n_f(times):
        if isinstance(times, (float, int)):
            return (actual_waiting_time_f(times) + t_dA * 60 - t_e * 60) / (t_di * 60)

        elif isinstance(times, (pd.DatetimeIndex, np.ndarray)):
            return pd.Series(times).apply(n_f)
        elif isinstance(times, pd.Timestamp):
            return n_f(times.timestamp())

    return x, n_f


# utility func
def get_choice(times):
    if isinstance(times, (float, int)):
        return 0 if actual_waiting_time_f(times) < expected_q_len_f(times) else 1

    elif isinstance(times, (pd.DatetimeIndex, np.ndarray)):
        return pd.Series(times).apply(get_choice)
    elif isinstance(times, pd.Timestamp):
        return get_choice(times.timestamp())


def extra_profit_f(times):
    if isinstance(times, (float, int)):
        # choice = get_choice(times)

        E_A = P_A - psi * X_A
        E_B = (P_i - psi * X_i) * n_f(times)

        if E_A > E_B:
            return (E_A - (E_A + E_B) / 2) / (actual_waiting_time_f(times) + t_dA * 60) * 3600
        else:
            return E_B - (E_A + E_B) / 2  / (actual_waiting_time_f(times) + t_dA * 60) * 3600

    elif isinstance(times, (pd.DatetimeIndex, np.ndarray)):
        return pd.Series(times).apply(extra_profit_f)
    elif isinstance(times, pd.Timestamp):
        return extra_profit_f(times.timestamp())


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals()
    departures_x, departures_f = get_passenger_departures()

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)
    inbounds_x, inbounds_f = get_taxi_inbounds(departures_x, departures_f)

    actual_q_len_x, actual_q_len_f = get_actual_q_len(x, inbounds_f, demands_f)
    _, expected_q_len_f = get_expected_q_len(x, demands_f)

    new_x, actual_waiting_time_f = get_actual_waiting_time(x, actual_q_len_f, demands_f)

    new_x, n_f = get_n(new_x, actual_waiting_time_f)

    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)

    ax1.plot(x, actual_q_len_f(x))
    ax2.plot(new_x, actual_waiting_time_f(new_x))
    ax3.plot(x, demands_f(x))
    ax4.plot(x, n_f(x))
    ax5.plot(x, extra_profit_f(x))

    # ax1.set_xlabel('time (Nov.30 2019)')
    # ax1.set_ylabel('actual queue length')

    myFmt = mdates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(myFmt)
    ax2.xaxis.set_major_formatter(myFmt)
    ax3.xaxis.set_major_formatter(myFmt)
    ax4.xaxis.set_major_formatter(myFmt)
    ax5.xaxis.set_major_formatter(myFmt)

    plt.show()
    #
    # fig, ax1 = plt.subplots()
    #
    # ax1.plot(x, extra_profit_f(x))
    #
    # ax1.set_xlabel('time (Nov.30 2019)')
    # ax1.set_ylabel('extra profit per hour')
    #
    # myFmt = mdates.DateFormatter('%H:%M')
    # ax1.xaxis.set_major_formatter(myFmt)
    #
    # plt.show()


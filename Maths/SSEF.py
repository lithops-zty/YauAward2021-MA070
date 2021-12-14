#
# Created by Lithops on 2021/12/7.
#
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import matplotlib.dates as mdates

from Maths.objective1.constants import psg_per_taxi
from Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from Maths.parse_changi_airport_departures import get_passenger_departures
from Maths.taxi_demand_prediction import get_taxi_demands
from taxi_inbound_prediction import get_taxi_inbounds
from math import factorial
from util import interpolate, plot_intercepts, get_intercepts

c = 17


def mu(t):
    return 60 / (3 + (30 * 2.7) / (demands_f(t) * psg_per_taxi))


def lambda_(t):
    return 300
    # return inbound_f(t) / 8


def rho(t):
    return lambda_(t) / mu(t) / c


def P0(t):
    return 1 / (sum([1 / factorial(k) * (lambda_(t) / mu(t)) ** k for k in range(c)]) + 1 / factorial(c) / (
            1 - rho(t)) * (lambda_(t) / mu(t)) ** c)


def Tq(t):
    return ((c * rho(t)) ** c * rho(t) * P0(t)) / (factorial(c) * (1 - rho(t)) ** 2 * lambda_(t)) * 10


def opp_cost(t):
    return 0 if Tq(t) >= 0.28 else 16 / 0.28 * (0.28 - Tq(t))


def revenue(t: pd.Timestamp):
    h = t.hour + t.minute / 60
    if 0 < h < 5.5:
        return 20 * Tq(t)
    elif 5.5 <= h < 6.5:
        return (-20 * (h - 6.5) ** 2 + 45) * Tq(t)
    elif 6.5 <= h < 8.5:
        return 45 * Tq(t)
    elif 8.5 <= h < 9.5:
        return (-5 * (h - 8.5) ** 2 + 45) * Tq(t)
    elif 9.5 <= h < 15.5:
        return 40 * Tq(t)
    elif 15.5 <= h < 16.5:
        return (-10 * (h - 16.5) ** 2 + 50) * Tq(t)
    elif 16.5 <= h < 18.5:
        return 50 * Tq(t)
    elif 18.5 <= h < 19.5:
        return (-10 * (h - 18.5) ** 2 + 50) * Tq(t)
    elif 19.5 <= h < 21.5:
        return 40 * Tq(t)
    elif 21.5 <= h < 22.5:
        return (-5 * (h - 21.5) ** 2 + 40) * Tq(t)
    elif 22.5 <= h <= 24 or h == 0:
        return 35 * Tq(t)


# def revenue(t):
#     h = t.hour
#     if 0 <= h < 6:
#         return 20 * Tq(t)
#     elif 6 <= h < 9:
#         return 45 * Tq(t)
#     elif 9 <= h < 16:
#         return 40 * Tq(t)
#     elif 16 <= h < 19:
#         return 50 * Tq(t)
#     elif 19 <= h < 22:
#         return 40 * Tq(t)
#     elif 22 <= h <= 24:
#         return 35 * Tq(t)


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    x_, departures_f = get_passenger_departures()
    arrivals_x, arrivals_f = get_passenger_arrivals()

    _, inbound_f = get_taxi_inbounds(x_, departures_f)
    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)

    fig, ax = plt.subplots()

    # revenue = interpolate(x, [revenue(i) for i in x])

    y1 = np.array([opp_cost(i) + 0.5 for i in x])
    y2 = np.array([revenue(i) for i in x])
    ax.plot(x, y1, c='r', label='$C_E +R_0(t)$')
    ax.plot(x, y2, c='b', label='$Q$')

    print(list(zip(*get_intercepts(x, y1, y2))))

    plot_intercepts(ax, x, y1, y2)

    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('economic profit (SG$)')

    plt.legend()

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    plt.show()

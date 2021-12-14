#
# Created by Lithops on 2021/8/25.
#
import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from Maths.objective1.actual_queue_length import get_actual_q_len
from Maths.objective1.expected_queue_length import get_expected_q_len
from Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from Maths.parse_changi_airport_departures import get_passenger_departures
from Maths.taxi_demand_prediction import get_taxi_demands
from Maths.taxi_inbound_prediction import get_taxi_inbounds
from Maths.util import get_intercepts, to_epoch, plot_intercepts, offset


def print_decision(intercepts_x):
    print(intercepts_x.strftime('%H:%M'))

    ax.scatter(intercepts_x, np.zeros(shape=intercepts_x.shape))
    print(intercepts_x)

    tmp = [datetime.timedelta(seconds=i) for i in
           np.diff(to_epoch(intercepts_x), prepend=to_epoch(intercepts_x[-1] - datetime.timedelta(hours=24)))]
    print([str(x) for x in tmp])

    print(sum(tmp[1::2], start=datetime.timedelta(hours=0)))


def plot_one_day(ax, date):
    x = pd.date_range(date, offset(date, 1), freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals(date)
    departures_x, departures_f = get_passenger_departures(date)

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)
    inbounds_x, inbounds_f = get_taxi_inbounds(departures_x, departures_f)

    actual_q_len_x, actual_q_len_f = get_actual_q_len(x, inbounds_f, demands_f)
    expected_q_len_x, expected_q_len_f = get_expected_q_len(demands_x, demands_f)

    actual_q_len = actual_q_len_f(x)
    expected_q_len = expected_q_len_f(x)

    # plot_intercepts(ax, x, actual_q_len, expected_q_len)

    ax.plot(x, actual_q_len, label='actual')
    ax.plot(x, expected_q_len, label='equal profit', linestyle='--')

    length = min(np.sum(~np.isnan(actual_q_len)), np.sum(~np.isnan(expected_q_len)))
    intercepts, _ = get_intercepts(x, actual_q_len[:length], expected_q_len[:length])

    # print_decision(intercepts)

    # ax.set_title('model')
    ax.set_xlabel(f'time {date}')
    # ax.set_ylabel('queue length')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    for tick in ax.get_xticklabels():
        tick.set_rotation(-45)

    # ax.legend()


begin = '2021/09/16'
end = offset(begin, 1)

if __name__ == '__main__':
    r = 3
    c = 3
    fig, ax = plt.subplots(r, c, squeeze=False)

    ax = ax.reshape(-1)

    for i in range(r * c):
        plot_one_day(ax[i], offset(begin, i))

        print(i, 'done!')

    plt.show()

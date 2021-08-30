#
# Created by Lithops on 2021/8/25.
#
import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from YauAward2021.Maths.objective1.actual_queue_length import get_actual_q_len
from YauAward2021.Maths.objective1.expected_queue_length import get_expected_q_len
from YauAward2021.Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from YauAward2021.Maths.parse_changi_airport_departures import get_passenger_departures
from YauAward2021.Maths.taxi_demand_prediction import get_taxi_demands
from YauAward2021.Maths.taxi_inbound_prediction import get_taxi_inbounds
from YauAward2021.Maths.util import get_intercepts, to_epoch


def print_decision(intercepts_x):
    print(intercepts_x.strftime('%H:%M'))

    ax.scatter(intercepts_x, np.zeros(shape=intercepts_x.shape))
    print(intercepts_x)


    tmp = [datetime.timedelta(seconds=i) for i in
                              np.diff(to_epoch(intercepts_x), prepend=to_epoch(intercepts_x[-1] - datetime.timedelta(hours=24)))]
    print([str(x) for x in tmp])

    print(sum(tmp[1::2], start=datetime.timedelta(hours=0)))



if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals()
    departures_x, departures_f = get_passenger_departures()

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)
    inbounds_x, inbounds_f = get_taxi_inbounds(departures_x, departures_f)

    actual_q_len_x, actual_q_len_f = get_actual_q_len(x, inbounds_f, demands_f)
    expected_q_len_x, expected_q_len_f = get_expected_q_len(demands_x, demands_f)

    fig, ax = plt.subplots()

    actual_q_len = actual_q_len_f(x)
    expected_q_len = expected_q_len_f(x)

    ax.plot(x, actual_q_len, label='actual')
    ax.plot(x, expected_q_len, label='equal profit', linestyle='--')


    length = min(np.sum(~np.isnan(actual_q_len)), np.sum(~np.isnan(expected_q_len)))
    intercepts, _ = get_intercepts(x, actual_q_len[:length], expected_q_len[:length])

    print_decision(intercepts)


    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('queue length')

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    ax.legend()

    plt.show()

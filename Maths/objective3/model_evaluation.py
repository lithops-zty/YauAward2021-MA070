#
# Created by Lithops on 2021/10/30.
#

#
# Created by Lithops on 2021/8/26.
#

import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.integrate
import scipy.signal

from YauAward2021.Maths.objective1.constants import P_A
from YauAward2021.Maths.objective1.model_evaluation import get_actual_waiting_time
from YauAward2021.Maths.objective3.queue_jumping_pos import get_q_jump_pos
from YauAward2021.Maths.util import to_epoch, get_intercepts, plot_intercepts
from YauAward2021.Maths.objective1.actual_queue_length import get_actual_q_len
from YauAward2021.Maths.objective3.constants import P_A_prime, psi, X_A, t_dA
from YauAward2021.Maths.parse_changi_airport_arrivals import get_passenger_arrivals
from YauAward2021.Maths.parse_changi_airport_departures import get_passenger_departures
from YauAward2021.Maths.taxi_demand_prediction import get_taxi_demands
from YauAward2021.Maths.taxi_inbound_prediction import get_taxi_inbounds


if __name__ == '__main__':
    x = pd.date_range('2019/11/30 00:00', '2019/12/1 00:00', freq='1Min')

    arrivals_x, arrivals_f = get_passenger_arrivals()
    departures_x, departures_f = get_passenger_departures()

    demands_x, demands_f = get_taxi_demands(arrivals_x, arrivals_f)

    inbounds_x, inbounds_f = get_taxi_inbounds(departures_x, departures_f)

    actual_q_len_x, actual_q_len_f = get_actual_q_len(x, inbounds_f, demands_f)

    q_jump_pos_x, q_jump_pos_f = get_q_jump_pos(x, demands_f, gamma=0.2)

    l = min(len(actual_q_len_x), len(q_jump_pos_x))

    def queue_len_diff_f(times):
        ret = actual_q_len_f(times) - q_jump_pos_f(times)
        return ret if ret >= 0 else actual_q_len_f(times)

    new_x, shortened_waiting_time_f = get_actual_waiting_time(q_jump_pos_x[:l], queue_len_diff_f, demands_f)

    new_x, actual_waiting_time_f = get_actual_waiting_time(q_jump_pos_x[:l], actual_q_len_f, demands_f)



    fig, ax = plt.subplots()



    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)

    def extra_profit_f(times, gamma=0.2):
        E_s = P_A + P_A_prime - (1 + 2 * gamma) * psi * X_A
        t_s = actual_waiting_time_f(times) * 2 + (2 * gamma + 1) * (t_dA * 60)
        t_s_prime = t_s - shortened_waiting_time_f(times)
        return (E_s / t_s_prime - E_s / t_s) * 3600

    tmp = scipy.signal.savgol_filter(extra_profit_f(new_x), 21, 4)
    ax.plot(new_x, tmp)
    # ax.plot(new_x, shortened_waiting_time_f(new_x))
    # ax.plot(new_x, queue_len_diff_f(new_x))
    # ax.plot(new_x, q_jump_pos_f(new_x))
    # ax.plot(new_x, actual_q_len_f(new_x))

    # plot_intercepts(ax, x, actual_q_len, q_jump_pos)
    # plot_intercepts(ax, x, actual_q_len, q_jump_pos2)


    ax.set_xlabel('time (Nov.30 2019)')
    ax.set_ylabel('extra profit per hour')

    # ax.legend()


    plt.show()

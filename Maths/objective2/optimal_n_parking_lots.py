#
# Created by Lithops on 2021/8/28.
#

import datetime
import math

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from YauAward2021.Maths.objective2.constants import lambda_, k, v, L, t_r
import scipy.integrate
import scipy.stats


@np.vectorize
def t_per_f(E, n):
    return E + 2 / k * (n * L / v + (n - 1) * t_r)


def target_f(n):
    exp_dis: scipy.stats.rv_continuous = scipy.stats.expon(scale=1 / lambda_)  # scale = 1 / lambda, see documentation

    t_per = []
    for _ in range(100):
        rvs = exp_dis.rvs(size=n)
        # print(rvs.mean())
        E = rvs.max()
        t_per.append(t_per_f(E, n))
    return n / np.array(t_per).mean() * 3600


def monte_carlo():
    n = 2
    targets = []
    ns = []
    while n <= max_n:
        targets.append(target_f(n))
        ns.append(n)
        n += 2

    return ns, targets


# def int_interval(interval):
#     return (math.floor(interval[0]), math.ceil(interval[1]))
#

max_n = 200

if __name__ == '__main__':

    fig, ax = plt.subplots()

    # x = np.linspace(0, 200)

    ns, targets = monte_carlo()

    max_y = target_f(max_n + 100)


    ax.grid(color='#dddddd')
    ax.set_axisbelow(True)

    ax.scatter(ns, targets, s=2)

    tmp_xlim = ax.get_xlim()
    ax.hlines(max_y * 0.8, *tmp_xlim, linestyles=':', color='r')
    ax.set_xlim(tmp_xlim)

    ax.annotate(f'{max_y * 0.8:.2f}', (10, max_y * 0.8))

    ax.set_xticks(np.arange(0, max_n, 10))
    ax.set_yticks(np.arange(0, 600, 50))

    ax.set_xlabel('number of parking lots')
    ax.set_ylabel('supply rate (cars/hour)')

    ax.set_title(f'max efficiency={max_y}')


    plt.show()

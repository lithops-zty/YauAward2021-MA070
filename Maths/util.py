#
# Created by Lithops on 2021/8/25.
#
import datetime

import numpy as np
import pandas as pd
import scipy.interpolate

def to_epoch(date_like):
    if isinstance(date_like, pd.DatetimeIndex):
        return date_like.map(lambda timestamp: to_epoch(timestamp))
    elif isinstance(date_like, pd.Timestamp):
        return date_like.timestamp()
    elif isinstance(date_like, (float, int)):
        return date_like


def interpolate(x, y):
    f = scipy.interpolate.interp1d(to_epoch(x), y, kind='cubic', bounds_error=False)
    interp = lambda new_x: f(to_epoch(new_x))
    return interp


def get_intercepts(x, y1, y2):
    idx = np.argwhere(np.diff(np.sign(y1 - y2))).flatten()
    return x[idx], (y1[idx] + y2[idx]) / 2


def plot_intercepts(ax, x, y1, y2):
    intercepts_x, intercepts_y = get_intercepts(x, y1, y2)


    labels = [f'({x.strftime("%H:%M")}, {y:.2f})' for x, y in zip(intercepts_x, intercepts_y)]
    plot_scatter_with_labels(ax, intercepts_x, intercepts_y, labels)


def plot_scatter_with_labels(ax, x, y, labels):
    ax.scatter(x, y)

    for xx, yy, label in zip(x, y, labels):
        ax.annotate(label, (xx, yy), fontsize=6)


def offset(date, days):
    s = datetime.datetime.strptime(date, '%Y/%m/%d') + datetime.timedelta(days=days)
    return s.strftime('%Y/%m/%d')


if __name__ == '__main__':
    t = pd.Timestamp.utcfromtimestamp(1575136590.0)
    tt = to_epoch(t)
    print(t,tt)

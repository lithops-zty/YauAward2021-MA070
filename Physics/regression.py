#
# Created by Lithops on 2021/8/31.
#

from sklearn.linear_model import LinearRegression

import numpy as np

import matplotlib.pyplot as plt


def regress(x, y, term_fs, predict_x):
    model = LinearRegression()
    train_feature_xs = np.concatenate([f(x).reshape(-1, 1) for f in term_fs], axis=1)
    predict_feature_xs = np.concatenate([f(predict_x).reshape(-1, 1) for f in term_fs], axis=1)
    model.fit(train_feature_xs, y)

    return model.predict(predict_feature_xs), model.coef_, model.intercept_


x = np.arange(1, 8)

y = np.array([118.5, 47.49, 36.59, 27.67, 21.72, 18.22, 17.52])

sample_x = np.linspace(0.2, 9, 50000).reshape(-1, 1)

sample_y, _, _ = regress(x, y,
                         [lambda x: 1 / x
                          ], sample_x)

plt.plot(sample_x, sample_y, label='theoretical curve')

plt.scatter(x, y, marker='x', c='r', label='experimental data')

# plt.ylim([0, 150])
plt.xlabel('$\gamma$')
plt.ylabel('$t_{max}/s$')
plt.grid()
plt.legend()

plt.show()

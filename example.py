#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bowtie.control import Nouislider, DropDown, Button
from bowtie.visual import Plotly, SmartGrid

import numpy as np
import json
import pandas as pd
import plotlywrapper as pw

from sklearn.kernel_ridge import KernelRidge

iris = pd.read_csv('./iris.csv')
iris = iris.drop(iris.columns[0], axis=1)

attrs = iris.columns[:-1]

xdown = DropDown(caption='X variable', options=[dict(value=x, label=x) for x in attrs])
ydown = DropDown(caption='Y variable', options=[dict(value=x, label=x) for x in attrs])
zdown = DropDown(caption='Z variable', options=[dict(value=x, label=x) for x in attrs])
alphaslider = Nouislider(caption='alpha parameter', start=1, minimum=0.1, maximum=50)

mainplot = Plotly()
mplot3 = Plotly()
linear = Plotly()
table1 = SmartGrid()


def mainviewx(x):
    x = x['value']
    y = ydown.get()
    z = zdown.get()
    if y is not None:
        y = y['value']
        mainview(x, y)
        if z is not None:
            z = z['value']
            mainview3(x, y, z)


def mainviewy(y):
    y = y['value']
    x = xdown.get()
    z = zdown.get()
    if x is not None:
        x = x['value']
        mainview(x, y)
        if z is not None:
            z = z['value']
            mainview3(x, y, z)


def mainviewz(z):
    z = z['value']
    y = ydown.get()
    x = xdown.get()
    if x is not None and y is not None:
        x = x['value']
        y = y['value']
        mainview3(x, y, z)


def mainview(x, y):
    plot = pw.Chart()
    for i, df in iris.groupby('Species'):
        plot += pw.scatter(df[x], df[y], label=i)
    plot.xlabel(x)
    plot.ylabel(y)
    mainplot.do_all(plot.to_json())


def mainview3(x, y, z):
    plot = pw.Chart()
    for i, df in iris.groupby('Species'):
        plot += pw.scatter3d(df[x], df[y], df[z], label=i)
    plot.xlabel(x)
    plot.ylabel(y)
    plot.zlabel(z)
    mplot3.do_all(plot.to_json())


def regress(selection):
    alpha = float(alphaslider.get())
    mainregress(selection, alpha)


def regress2(alpha):
    select = mainplot.get()
    mainregress(select, float(alpha[0]))


def mainregress(selection, alpha):
    if len(selection) < 2:
        return

    x = xdown.get()['value']
    y = ydown.get()['value']

    tabdata = []
    mldatax = []
    mldatay = []
    species = iris.Species.unique()
    for i, p in enumerate(selection['points']):
        mldatax.append(p['x'])
        mldatay.append(p['y'])
        tabdata.append({x: p['x'],
                        y: p['y'],
                        'species': species[p['curveNumber']]
                        })


    X = np.c_[mldatax, np.array(mldatax) ** 2]
    ridge = KernelRidge(alpha=alpha).fit(X, mldatay)

    xspace = np.linspace(min(mldatax)-1, max(mldatax)+1, 100)

    plot = pw.scatter(mldatax, mldatay, label='train', markersize=15)
    for i, df in iris.groupby('Species'):
        plot += pw.scatter(df[x], df[y], label=i)
    plot += pw.line(xspace, ridge.predict(np.c_[xspace, xspace**2]), label='model', mode='lines')
    plot.xlabel(x)
    plot.ylabel(y)
    linear.do_all(plot.to_json())
    table1.do_update(tabdata)


if __name__ == "__main__":
    from bowtie import Layout
    layout = Layout()
    layout.add_controller(xdown)
    layout.add_controller(ydown)
    layout.add_controller(zdown)
    layout.add_controller(alphaslider)
    layout.add_visual(mainplot)
    layout.add_visual(mplot3)
    layout.add_visual(linear, next_row=True)
    layout.add_visual(table1)

    layout.subscribe(xdown.on_change, mainviewx)
    layout.subscribe(ydown.on_change, mainviewy)
    layout.subscribe(zdown.on_change, mainviewz)

    layout.subscribe(mainplot.on_select, regress)
    layout.subscribe(alphaslider.on_change, regress2)

    layout.build(debug=False)

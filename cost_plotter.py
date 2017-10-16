#!/usr/bin/env python

import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_charges():

    integrate = True
    path = '/home/rlbyrne/rlb_aws'
    anaconda_path = '/home/rlbyrne/anaconda2/bin'

    charge_items = get_data(path,anaconda_path)
    total_cost = sum([item.cost for item in charge_items])
    product_types = list(set([item.product for item in charge_items]))
    times = [datetime.now() + timedelta(minutes=minutes) for minutes in range(-10080,0)]
    while times[-1] > max([item.endtime for item in charge_items]):
        del times[-1]
    costs = np.zeros((len(product_types),len(times)))
    for i, time in enumerate(times):
        for item in charge_items:
            if item.starttime < time < item.endtime:
                costs[product_types.index(item.product),i] += item.cost_per_minute

    cost_integrated = np.zeros((len(product_types),len(times)))
    for j in range(len(product_types)):
        cost_integrated[j,:] = [sum(costs[j,:i]) for i in range(len(times))]

    #Sort products from most to least expensive. This is horrible and ugly, make it better.
    product_types = sorted(product_types, key = lambda val: cost_integrated[product_types.index(val),-1], reverse=True)


    if integrate:
        cost_integrated_sorted = cost_integrated[cost_integrated[:,-1].argsort()[::-1]]
        plot_fill_in(times, cost_integrated_sorted, product_types, integrate, path)
    else:
        costs_sorted = costs[cost_integrated[:,-1].argsort()[::-1]]
        plot_fill_in(times, costs_sorted, product_types, integrate, path)



def plot_lines(times, cost_data, product_types, integrate, path):

    plt.plot(times,np.sum(cost_data, axis=0), label='Total')
    for j in range(len(product_types)):
        plt.plot(times,cost_data[j,:],label=product_types[j])
    plt.xlabel("time")
    if integrate:
        plt.ylabel("total cost (USD)")
    else:
        plt.ylabel("cost (USD per minute)")
    plt.legend(loc=2)
    plt.grid(True)
    plt.tick_params(labelsize=6)
    plt.savefig('{}/aws_costs_{}.png'.format(path, datetime.now().date()))


def plot_fill_in(times, cost_data, product_types, integrate, path):

    fig, ax = plt.subplots()
    running_sum = [0]*len(times)
    for i in range(len(product_types)):
        running_sum_new = [running_sum[j]+cost_data[i,j] for j in range(len(times))]
        ax.fill_between(times,running_sum_new,running_sum,where=None,label=product_types[i])
        running_sum = running_sum_new
    plt.xlabel("time")
    if integrate:
        plt.ylabel("total cost (USD)")
    else:
        plt.ylabel("cost (USD per minute)")
    plt.legend(loc=2)
    plt.grid(True)
    plt.tick_params(labelsize=6)
    plt.savefig('{}/aws_costs_{}.png'.format(path, datetime.now().date()))


def find_cost_report(anaconda_path):

    reports_all = os.popen('{}/aws s3 ls s3://eorbilling//cost_report/ --recursive'.format(anaconda_path)).readlines()
    reports = [rep for rep in reports_all if rep.endswith('cost_report-1.csv.gz\n')]
    latest_report = reports[0]
    for rep in reports:
        time = latest_report_time = datetime.strptime(rep[:18],"%Y-%m-%d %H:%M:%S")
        latest_report_time = datetime.strptime(latest_report[:18],"%Y-%m-%d %H:%M:%S")
        if time > latest_report_time:
            latest_report = rep
    s3_path = "s3://eorbilling/{}".format(latest_report.split(' ')[-1])
    s3_path = s3_path.rstrip()
    return s3_path


def get_data(path,anaconda_path):

    s3_path = find_cost_report(anaconda_path)

    os.system("{}/aws s3 cp {} {}/".format(anaconda_path,s3_path,path))
    os.system("gunzip -f cost_report-1.csv.gz > {}/cost_report-1.csv".format(path))

    datafile = open("{}/cost_report-1.csv".format(path),"r")
    data = datafile.readlines()
    datafile.close()

    header = data[0].split(",")
    charge_items = []
    for i, data_line in enumerate(data[1:]):
        new_charge = Lineitem(data_line, header)
        if new_charge.cost > 0. and (datetime.now() - new_charge.endtime).total_seconds() < 604800:
            charge_items.append(new_charge)

    return charge_items


class Lineitem:

    def __init__(self, data_line, header):
        data_split = data_line.split(",")
        self.starttime = datetime.strptime(data_split[header.index("lineItem/UsageStartDate")],"%Y-%m-%dT%H:%M:%SZ")
        self.endtime = datetime.strptime(data_split[header.index("lineItem/UsageEndDate")],"%Y-%m-%dT%H:%M:%SZ")
        self.duration = (self.endtime - self.starttime).total_seconds()
        self.product = data_split[header.index("lineItem/ProductCode")]
        self.usage_type = data_split[header.index("lineItem/UsageType")]
        self.cost = float(data_split[header.index("lineItem/BlendedCost")])
        self.cost_per_minute = self.cost/self.duration*60
        self.description = data_split[header.index("lineItem/LineItemDescription")]


if __name__ == "__main__":
    plot_charges()

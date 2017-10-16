#!/usr/bin/env python

import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np


def plot_charges():

    charge_items = get_data()
    total_cost = sum([item.cost for item in charge_items])
    product_types = list(set([item.product for item in charge_items]))
    print(product_types)
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

    for j in range(len(product_types)):
        plt.plot(times,cost_integrated[j,:],label=product_types[j])
    plt.plot(times,np.sum(cost_integrated, axis=0), label='Total')
    plt.xlabel("time")
    plt.ylabel("total cost (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()


def find_cost_report():

    reports_all = os.popen('aws s3 ls s3://eorbilling//cost_report/ --recursive').readlines()
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


def get_data():

    s3_path = find_cost_report()

    os.system("aws s3 cp {} .".format(s3_path))
    os.system("gunzip cost_report-1.csv.gz")

    datafile = open("cost_report-1.csv","r")
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

#!/usr/bin/env python

import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def plot_charges():

    charge_items = get_data()
    total_cost = sum([item.cost for item in charge_items])
    times = [datetime.now() + timedelta(minutes=minutes) for minutes in range(-10080,0)]
    while times[-1] > max([item.endtime for item in charge_items]):
        times = times[:-1]
    costs = [0]*len(times)
    for i, time in enumerate(times):
        for item in charge_items:
            if item.starttime < time < item.endtime:
                costs[i] += item.cost_per_minute

    cost_integrated = [sum(costs[:i]) for i in range(len(times))]

    plt.plot(times,cost_integrated)
    plt.xlabel("time")
    plt.ylabel("total cost (USD)")
    plt.grid(True)
    plt.show()


def get_data():

    filename = "cost_report-1"
    s3_path = "s3://eorbilling//cost_report/20171001-20171101/ccf70ead-fdf4-43ea-ba98-696592a1ce37"

    os.system("aws s3 cp {}/{}.csv.gz .".format(s3_path,filename))
    os.system("gunzip {}.csv.gz".format(filename))

    datafile = open("{}.csv".format(filename),"r")
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

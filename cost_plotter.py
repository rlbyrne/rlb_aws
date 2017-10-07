#!/usr/bin/env python

import os


def get_data():

    filename = "cost_report-1"
    s3_path = "s3://eorbilling//cost_report/20171001-20171101/9cd86a3d-bd52-4e7d-bf94-ace317d6cbb2"

    os.system("aws s3 cp {}/{}.csv.gz .".format(s3_path,filename))
    os.system("tar -xvzf {}.csv.gz".format(filename))

    datafile = open("{}.csv".format(filename),"r")
    data = datafile.readlines()
    datafile.close()

    header = data[0]
    charge_items = []]
    for i, data_line in enumerate(data[1:]):
        new_charge = Lineitem(data_line, header)
        if new_charge.cost != 0.:
            charge_items.append(new_charge)

class Lineitem:

    def __init__(self, data_line, header):
        self.starttime = data_line[header.index("lineItem/UsageStartDate")]
        self.endtime = data_line[header.index("lineItem/UsageEndDate")]
        self.product = data_line[header.index("lineItem/ProductCode")]
        self.cost = float(data_line[header.index("lineItem/BlendedCost")])
        self.description = data_line[header.index("lineItem/LineItemDescription")]


if __name__ == "__main__":
    get_data()

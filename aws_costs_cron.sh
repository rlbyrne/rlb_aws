#!/bin/bash

/home/rlbyrne/rlb_aws/cost_plotter.py
plotname=$(ls /home/rlbyrne/rlb_aws/aws_costs_*.png)
/home/rlbyrne/slackcat --channel rubyb /home/rlbyrne/rlb_aws/${plotname}
rm /home/rlbyrne/rlb_aws/cost_report-1.csv
rm /home/rlbyrne/rlb_aws/${plotname}

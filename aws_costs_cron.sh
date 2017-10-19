#!/bin/bash

# Cron job for running on Enterprise to keep track of AWS charges.
# Generates up-to-date AWS charges plots and uploads them to the eor_cloud
# channel on the EoR Analysis Slack.
# To upload every day at noon, add 0 12 * * * /path/to/script/aws_costs_cron.sh
# to crontab -e.
# Created by R. Byrne 10/17

/home/rlbyrne/anaconda2/bin/python /home/rlbyrne/rlb_aws/cost_plotter.py
plotname=$(ls /home/rlbyrne/rlb_aws/aws_costs_*.png)
/home/rlbyrne/slackcat --channel eor_cloud ${plotname}
rm /home/rlbyrne/rlb_aws/cost_report-1.csv
rm ${plotname}

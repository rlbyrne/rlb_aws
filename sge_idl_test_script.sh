#! /bin/bash

echo "$1" > ~/file$1.txt
while [ $1 -gt 0 ]
do
    sleep 5
    idl -e sge_test >> ~/file$1.txt
done

#!/bin/bash

bank=$1
database=$2
acc=${bank}_ACCESS_TOKEN
req=${bank}_REQUISITION_ID
access_token=${!acc}
requisition_id=${!req}
python3 main_get.py "$access_token" "$requisition_id" "$bank" "$database"



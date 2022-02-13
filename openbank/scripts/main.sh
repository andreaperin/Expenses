#!/bin/bash

. ~/.profile
# cd /home/andrea/Documents/Projects/openbank/scripts
cd /home/andreaperin/MyDocuments/Ubuntu/Expenses/openbank/scripts
declare -a BankStringArray=(PAYPAL UNICREDIT FINECO N26)

database='../data/bank.db'

for bank in "${BankStringArray[@]}"; do
  acc=${bank}_ACCESS_TOKEN
  req=${bank}_REQUISITION_ID
  access_token=${!acc}
  requisition_id=${!req}
  echo "getting data with available token for ${bank}"
  ./get_data.sh "$bank" $database
done

### Sending mail

python3 notify.py

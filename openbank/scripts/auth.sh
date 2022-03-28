#!/bin/bash

SECRET_ID=$NORDIGEN_API_ID
SECRET_KEY=$NORDIGEN_API_KEY
# bank=UNICREDIT
country='IT'
max_historical_days="7"
access_valid_days="7"
redirect_uri="http://localhost"
need_link=1

echo "Enter a bank to update:"
echo "1: UNICREDIT"
echo "2: PAYPAL"
echo "3: FINECO"
echo "4: N26"

while true; do
  echo "Enter the value"
  read value

  if [ "$value" == '1' ]; then
    bank=UNICREDIT
    break
  elif [ "$value" == '2' ]; then
    bank=PAYPAL
    break
  elif [ "$value" == '3' ]; then
    bank=FINECO
    break
  elif [ "$value" == '4' ]; then
    bank=N26
    country='DE'
    break
  else
    echo "enter a valid bank value"
  fi
done

python3 main_auth.py "$SECRET_ID" "$SECRET_KEY" $country $max_historical_days $access_valid_days $redirect_uri $need_link $bank
# setting current access_token and requisition_id as env variable in bashrc
acc_token=$(cat ../results/tmp/mine.json | jq .access_token)
req_id=$(cat ../results/tmp/mine.json | jq .requisition_id)
reg="export ${bank}_"

sed -i "/${reg}/d" ~/.profile
echo "export ${bank}_ACCESS_TOKEN=${acc_token}" >>~/.profile
echo "export ${bank}_REQUISITION_ID=${req_id}" >>~/.profile
source ~/.profile

## Update ~/.profile in server
# Connection through ssh key pair
## this way to connect ssh works with key-pairs only (https://linuxize.com/post/how-to-setup-passwordless-ssh-login/)
# ssh andreaperin@192.168.1.9 << EOF
# sed -i "/${reg}/d" ~/.profile
# echo "export ${bank}_ACCESS_TOKEN="${acc_token}"" >>~/.profile
# echo "export ${bank}_REQUISITION_ID="${req_id}"" >>~/.profile
# source ~/.profile
# EOF

rm -r ../results/tmp

echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "Auth for $bank is finished!"
echo "Stay in this terminal for further auth or close it and open a new one for getting data"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

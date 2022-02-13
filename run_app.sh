#!/bin/bash

echo 'Updating database with last available version'

cd /home/andreaperin/MyDocuments/Ubuntu/Expenses/openbank/scripts
cp -r ../data/bank.db ../../application/data/

######################
##  Authorization   ##
######################

Yes_No() {
    # print question
    echo -n "Do you want to authorize an account?: "

    # read answer
    read YnAnswer

    # all to lower case
    YnAnswer=$(echo $YnAnswer | awk '{print tolower($0)}')

    # check and act on given answer
    case $YnAnswer in
    "yes") Start_auth ;;
    "no") break ;;
    *)
        echo "Please answer yes or no"
        Yes_No
        ;;
    esac
}

# function that is started when answer is yes
Start_auth() {
    ./auth.sh
    #more code here
    echo "Do you want to authorize another account?"
    Yes_No
}

# ask the yes/no question
Yes_No

#####################
##  RetrivingData  ##
#####################

Yes_No() {
    # print question
    echo -n "Do you want to retrieve latest data?: "

    # read answer
    read YnAnswer

    # all to lower case
    YnAnswer=$(echo $YnAnswer | awk '{print tolower($0)}')

    # check and act on given answer
    case $YnAnswer in
    "yes") Start_dwnl ;;
    "no") break ;;
    *)
        echo "Please answer yes or no"
        Yes_No
        ;;
    esac
}

# function that is started when answer is yes
Start_dwnl() {
    ./main.sh
    #more code here
}

# ask the yes/no question
Yes_No

echo 'Updating database in application'
cp -r ../data/bank.db ../../application/data/
echo 'Database correctly updated'

echo '-----------------------------------------------------------'
echo ''
echo 'starting application'
echo ''

cd /home/andreaperin/MyDocuments/Ubuntu/Expenses/application/scripts
python3 update_csvTransactions.py
python3 app_trial.py

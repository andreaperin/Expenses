### Before running ###
__logs/main__, __logs/auth__ and __data__ folders must be created

### Token ###
- nordigen API token are needed
- bank account token are stored in ~/.profile
  
### Environment ###
Using cona on linux:
- conda env create -f openbank

### Authentication ###
- auth is performed through __auth.sh__ and requires browser interaction.
- For me: this action can be performed from XPS15-Ubuntu, or from Desktop station with ssh connection tu XPS-15-Ubuntu [WSL is WIP]

### Data ###
- data are retrieved through __main_get.py__, called by __main.sh__
- retrieved data are stored into __data/bank.db__
- __main.sh__ is supposed to be run through crontab (_crontab -e_) and notify me through mail with logs.
    

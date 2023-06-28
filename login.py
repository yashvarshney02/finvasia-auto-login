from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyotp
import pandas as pd
import inquirer
import time

# parameters
ROOT_URL = "https://shoonya.finvasia.com/#/"

# read the accounts csv
accounts = pd.read_csv("accounts.csv") 


def get_user_options():
    """this returns a list of user options to select from
    """
    return accounts.user.to_list()

drivers = {}

while True:
    # now show user some options to select a user from
    options = get_user_options()
    questions = [
        inquirer.List('option',
                      message='List of available users',
                      choices=options)
    ]
    
    answers = inquirer.prompt(questions)
    user = answers['option']
    creds = accounts[accounts.user == user]
    password = creds.password.values[0]
    totp_secret = creds.secret.values[0]
    print("Attempting Login in", user)

    try:
        # now open a new chrome window
        # installing manager will take care for the driver itself, no need to pass
        # the executable path
        drivers[user] = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    except Exception as E:
        print("Not able to open browser due to error:", E)
        continue
        
    # open finvasia new window
    drivers[user].get(ROOT_URL)
    check = True # this is for checking if webpage has the current html tags
    
    while check:
        try:
            input_field = drivers[user].execute_script("return document.querySelector('body > flt-glass-pane').shadowRoot.querySelector('input');")
            # send the user name
            input_field.send_keys(user)
            input_field.send_keys(Keys.TAB)
            check = False
        except:
            # the page is not loaded yet maybe
            pass
        time.sleep(1) # a gap of 1 second
        
    try:
        input_field = drivers[user].execute_script("return document.querySelector('body > flt-glass-pane').shadowRoot.querySelector('input');")
        # now send the password
        input_field.send_keys(password)
        input_field.send_keys(Keys.TAB)
        
        # finally send the totp
        totp = pyotp.TOTP(totp_secret).now()
        input_field = drivers[user].execute_script("return document.querySelector('body > flt-glass-pane').shadowRoot.querySelector('input');")
        input_field.send_keys(totp)
        input_field.send_keys(Keys.RETURN)
        
    except Exception as E:
        print(f"Login failed in {user} due to error: {E}")
    
        
    
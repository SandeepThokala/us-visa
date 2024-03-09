# us-visa
* Uses github actions to run a Python script `main.py` every hour.
* The script logs into https://ais.usvisa-info.com using Selenium
* Navigates through the website, checks for available visa appointemts.
* Sends an email notification if an early available slot is found. 

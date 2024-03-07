import os
import smtplib as smtp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.chrome import ChromeDriverManager

SENDER = 'sandeep.thokala98@gmail.com'

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    # "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

chrome = webdriver.Chrome(service=chrome_service, options=chrome_options)

def login():
    chrome.get(r'https://ais.usvisa-info.com/en-ca/niv/users/sign_in')
    chrome.find_element(By.ID, "user_email").send_keys(SENDER)
    chrome.find_element(By.ID, "user_password").send_keys(os.environ['LOGIN_PASSWORD'])
    chrome.execute_script("document.getElementById('policy_confirmed').click();")
    chrome.find_element(By.ID, "policy_confirmed").is_selected()
    chrome.find_element(By.XPATH, '''//*[@id="sign_in_form"]/p[1]/input''').click()

def navigate():
    WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.XPATH, '''//*[@id="main"]/div[2]/div[3]/div[1]/div/div/div[1]/div[2]/ul/li/a'''))
    ).click()

    WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.XPATH, '''//*[@id="forms"]/ul/li[4]/a'''))
    ).click()

    button = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.XPATH, '''//*[@id="forms"]/ul/li[4]/div/div/div[2]/p[2]/a'''))
    )
    ActionChains(chrome).move_to_element(button).click(button).perform()

def check_slot(city):
    select = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "appointments_consulate_appointment_facility_id"))
    )
    Select(select).select_by_visible_text(city)

    # Wait 10s until 'try again text' has style attribute and check for dates
    try:
        WebDriverWait(chrome, 10).until(
            EC.text_to_be_present_in_element_attribute(
                (By.ID, "consulate_date_time_not_available"),
                'style',
                'none' 
            )
        )
        button = WebDriverWait(chrome, 10).until(
            EC.presence_of_element_located((By.XPATH, '''//*[@id="appointments_consulate_appointment_date"]'''))
        )
        ActionChains(chrome).move_to_element(button).click(button).perform()

        # Check next 14 months for a slot
        for i in range(14):
            try:
                date = WebDriverWait(chrome, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-group-first"))
                ).find_element(By.TAG_NAME, 'tbody').find_element(By.TAG_NAME, 'a').parent
                send_mail(f'{date.get_attribute("data-month")}-{date.get_attribute("data-yeay")}')
                break
            except:
                next = WebDriverWait(chrome, 10).until(
                    EC.presence_of_element_located((By.XPATH, '''//*[@id="ui-datepicker-div"]/div[2]/div/a'''))
                )
                ActionChains(chrome).move_to_element(next).click(next).perform()

        # Go to except block if no slot is found
        raise

    except:
        if city == 'Toronto':
            check_slot('Ottawa')
        else:
            return

def send_mail(body):
    with smtp.SMTP_SSL('smtp.gmail.com', 465) as conn: 
        conn.login(SENDER, os.environ['APP_PASSWORD'])
        conn.sendmail(from_addr=SENDER, to_addrs=SENDER, msg=body)


if __name__ == '__main__':
    login()
    navigate()
    check_slot('Toronto')
    

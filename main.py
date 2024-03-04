import os
import time
import base64
import smtplib as smtp
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service as ChromiumService

SENDER = 'sandeep.thokala98@gmail.com'

chrome = webdriver.Chrome(
    service=ChromiumService(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    )
)

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

        for i in range(50):
            try:
                WebDriverWait(chrome, 10).until(
                    EC.presence_of_element_located((By.XPATH, '''//*[@id="ui-datepicker-div"]'''))
                ).find_element(By.TAG_NAME, 'a')
                send_mail()
                break
            except:
                next = WebDriverWait(chrome, 10).until(
                    EC.presence_of_element_located((By.XPATH, '''//*[@id="ui-datepicker-div"]/div[2]/div/a'''))
                )
                ActionChains(chrome).move_to_element(next).click(next).perform()

    except:
        if city == 'Toronto':
            check_slot('Ottawa')
        else:
            send_mail()
    

def send_mail():
    with smtp.SMTP_SSL('smtp.gmail.com', 465) as conn: 
        mess = MIMEMultipart()
        mess['From'] = SENDER
        mess['To'] = SENDER
        mess['Subject'] = 'Rescheule your slot'
        mess.attach(MIMEText('No slots available'))
        # mess.attach(
        #     MIMEImage(
        #         base64.b64decode(chrome.get_screenshot_as_base64()),
        #         name='image.png'
        #     )
        # )
        conn.login(SENDER, os.environ['APP_PASSWORD'])
        conn.sendmail(from_addr=SENDER, to_addrs=SENDER, msg=mess)


if __name__ == '__main__':
    login()
    navigate()
    check_slot('Toronto')
    
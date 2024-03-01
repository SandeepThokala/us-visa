import os
import smtplib as smtp

with smtp.SMTP_SSL('smtp.gmail.com', 465) as conn:
    email_addr = 'sandeep.thokala98@gmail.com'
    email_passwd = os.environ['APP_PASSWORD']
    conn.login(email_addr, email_passwd)
    conn.sendmail(from_addr=email_addr, to_addrs=email_addr, msg=os.environ['MESSAGE']) #"Please check your slot")

#!/usr/bin/env python3
# Written by duanjun1981@gmail.com to check IP status and send out email to notify latest IP


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import socket
import os.path
import logging
import configparser


def sendMail(server_url, sender_email, sender_email_pass, message,subject, recipient_emails):
    server = smtplib.SMTP_SSL(server_url, 465)
    server.login(sender_email,sender_email_pass)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_emails
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'plain'))  
    text = msg.as_string()
    server.sendmail(sender_email, recipient_emails.split(','), text)

if __name__ =='__main__':    

    # load config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # check current ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    current_ip=s.getsockname()[0]


    # set log file
    logging.basicConfig(filename="logs.txt",
                    format='%(asctime)s %(message)s',
                    filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


    # Get email settings from config file
    machine_name = config['DEFAULT']['Machine']
    server_url = config['EMAIL']['Server_URL']
    subject = config['EMAIL']['Subject'] + " for " + machine_name
    sender_email = config['EMAIL']['Sender_email']
    sender_email_pass = config['EMAIL']['Sender_email_pass']
    recipient_emails =  config['EMAIL']['Recipient_emails']

    if os.path.isfile('.local_ip'):
        with open(".local_ip") as f:
            lines = f.read()
            last_ip = lines.split('\n', 1)[0]
            if(current_ip == last_ip):
                logger.info("Same IP")                
            else:
                message = 'CIDGOH IP montior found IP address status change. The IP has been changed from '+last_ip+' to '+current_ip +" for "+ machine_name+"."
                logger.warning(message)
                sendMail(server_url, sender_email, sender_email_pass, message,subject, recipient_emails)
                f = open(".local_ip", "w")
                f.write(current_ip)
                f.close()

    else:
        message = 'CIDGOH IP monitor is running. The current IP for '+ machine_name + ' is '+current_ip+"."
        sendMail(server_url, sender_email, sender_email_pass, message,subject, recipient_emails)     
        f = open(".local_ip", "w")
        f.write(current_ip)
        f.close()
        logger.info(message)
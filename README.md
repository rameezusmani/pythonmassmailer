# pythonmassmailer

pythonmassmailer is a very simple mass emailing python script that uses smtplib.SMTP class

PREREQUISITES
=============
if you get error like "socks" module not found then please install PySocks using

pip install PySocks

SMTP SERVERS and RECIPIENTS EMAIL ADDRESSES
===========================================
- SMTP servers must be listed in smtps.txt file. Each line in smtps.txt file is a smtp server in following format
ip_address:port,email_address,password,1(0 for no authentication)

- Recipients email addresses must be listed in emails.txt file. Each line in emails.txt is a recipient email address

RUNNING THE SCRIPT
==================
- After you have setup your SMTP servers in smtps.txt and recipients in emails.txt then you can run the script like this:

  python massmailer.py
  
CHANGING SUBJECT and BODY
=========================
- You can change values for subject and body inside load_config procedure in massmailerhelper.py. Following lines will require modification to change subject and body

  config.subject="this will be your subject"
  
  config.body="This will be the email body"

CHANGING OTHER VARIABLES
========================
- You can change values like number of threads to use, maximum number of email to send, sender name etc inside load_config procedure in massmailerhelper.py. For example if you want to set number of threads to 500 then you can set this line inside load_config procedure

  config.totalThreads=100

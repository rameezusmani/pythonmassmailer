# pythonmassmailer

pythonmassmailer is a very simple multithreaded mass emailing python script that uses smtplib.SMTP class. I tested it with 400 threads at a time and it sent 1000s of emails within few seconds using few (but working) SMTP servers.

HOW IT IS DIFFERENT
==================
- It is multithreaded and can execute any number of threads configured in the script
- You can use unlimited number of SMTP servers at the same time
- It uses SMTP server(s) efficiently so they are not overloaded
- 10K emails can be sent without any problem using few SMTP servers

PREREQUISITES
=============
if you get error like "socks" module not found then please install PySocks using

pip install PySocks

SMTP SERVERS and RECIPIENTS EMAIL ADDRESSES
===========================================
- SMTP servers must be listed in smtps.txt file. Each line in smtps.txt file is a smtp server in following format
ip_address:port,email_address,password,1(0 for no authentication)

- Recipients email addresses must be listed in emails.txt file. Each line in emails.txt is a recipient email address

PROXY SERVERS
=============
- Proxy servers must be listed in proxies.txt file. Each line in proxies.txt file is a proxy server in following format
ip_address:port,proxy_type(socks4,socks5,http)

EXAMPLE: 123.456.789.1:1080,socks5

ENABLE/DISABLE PROXY SUPPORT
============================
- You can change sendWithProxy of class MassMailerConfig in massmailerhelper.py file to toggle the proxy support.
    True = use proxy
    False = dont use proxy

ADDING ATTACHMENT(S)
====================
- You can add attachment to individual EmailToSend objects using their Attachments list property
- testmailer.py demonstrates how to use that

RUNNING THE SCRIPT
==================
- After you have setup your SMTP servers in smtps.txt and recipients in emails.txt then you can run the script like this:

  python massmailer.py
  
CHANGING SUBJECT and BODY
=========================
- You can change values for subject and body inside load_config procedure in massmailerhelper.py. Following lines will require modification to change subject and body

  config.subject="this will be your subject"
  
  config.body="This will be the email body" #you can use HTML in body

CHANGING OTHER VARIABLES
========================
- You can change values like number of threads to use, maximum number of email to send, sender name etc inside load_config procedure in massmailerhelper.py. For example if you want to set number of threads to 500 then you can set this line inside load_config procedure

  config.totalThreads=100
  
FUTURE PLANS
============
- SSL support

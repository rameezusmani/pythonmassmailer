from massmailerhelper import *
#this script will test sending of email using Gmail smtp server
load_config()
config.fromName="UglyGuy InSlippers"
smtp=smtpsQueue.get()
smtp.ip="smtp.gmail.com"
smtp.port=587
smtp.email="***************@gmail.com"
smtp.username="***********@gmail.com"
smtp.password="***********"
smtp.requiresAuthentication=True
smtp.useTls=True
email=emailsQueue.get()
email.Mail="*****@recdomain.com"
email.Attachments.append("attachment.txt")
print("Testing with: "+smtp.ip+":"+str(smtp.port)+". Sending to email: "+email.Mail)
sender=NonProxyEmailSender(config)
sender.set_smtp_server(smtp)
sender.set_email_to_send(email)
try:
    sender.send_email()
except Exception as err:
    print(format(err))
print("Finish")
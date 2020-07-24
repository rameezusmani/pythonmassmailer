from massmailerhelper import *
#this script will test sending of email using Gmail smtp server
load_config()
config.fromName="UglyGuy InSlippers"
#construct a new test smtp server
smtp=MassMailerSmtp()
smtp.host="gmail.com"
smtp.ip="smtp.gmail.com"
smtp.port=587
smtp.email="uglyguyinslippers@gmail.com"
smtp.username="uglyguyinslippers@gmail.com"
smtp.password="****************"
smtp.requiresAuthentication=True
smtp.useTls=True
#construct new recipient
email=EmailToSend()
email.Mail="***********@hotmail.com"
#add 1 attachment
email.Attachments.append("attachment.txt")
#call email.Attachments.append multiple times to add multiple attachments
print("Testing with: "+smtp.ip+":"+str(smtp.port)+". Sending to email: "+email.Mail)
sender=NonProxyEmailSender(config)
sender.set_smtp_server(smtp)
sender.set_email_to_send(email)
try:
    sender.send_email()
except Exception as err:
    print(format(err))
print("Finish")
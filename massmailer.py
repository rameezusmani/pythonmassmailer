import time
import threading
import sys
from datetime import datetime
from massmailerhelper import *
import smtplib
from threading import Lock

proxiesLock=Lock()

#removes proxy for the list of proxies
def drop_proxy(proxy):
    proxiesLock.acquire()
    for x in proxiesQueue:
        try:
            if (x.ip==proxy.ip and x.port==proxy.port):
                proxiesQueue.remove(x)
                break
        except Exception as err:
            pass

    proxiesLock.release()

def send_email_thread(tconfig:MassMailerThreadConfig):
    myTag="Thread#"+str(tconfig.threadIndex+1) #set unique tag of thread so it can be identified in logs
    try:
        stateObject=MassMailerThreadState() #state of this particular thread
        stateObject.config=tconfig.config #set global config object 
        stateObject.threadTag=myTag #unique tag of this thread to be identified in logs
        sender=None #email sender object
        #if proxy is being used then create ProxyEmailSender instance
        if (stateObject.config.sendWithProxy):
            sender=ProxyEmailSender(stateObject.config)
        #else create NonProxyEmailSender instance
        else:
            sender=NonProxyEmailSender(stateObject.config)

        #loop indefinitely
        while(True):
            #check if maximum number of emails are already sent
            if (check_max_emails_sent(stateObject,tconfig)):
                #decrement current threads count
                #as this thread will die
                config.totalThreads-=1
                return
            stateObject.proxy=False
            stateObject.smtp=False
            try:
                #try to get next smtp server from the queue
                stateObject.smtp=smtpsQueue.get_nowait()
                #set the retrieved smtp server
                sender.set_smtp_server(stateObject.smtp)
            except queue.Empty as err:
                #error thrown because smtp queue is empty. it means there are no more smtp servers available
                write_mysmtp_log("Couldn't find a free smtp server",stateObject.threadTag,True,True)
                #get out of the loop
                break
            smtp=stateObject.smtp
            proxy=stateObject.proxy
            #check if smtp has specified port opened
            if (not smtp.has_port_opened and not check_host(smtp.ip,smtp.port)):
                #if port is closed then go back to While loop to get next smtp from the queue
                write_mysmtp_log("SMTP " + smtp.ip + " have port " + str(smtp.port) + " closed",stateObject.threadTag,True,True)
                continue
            #set port opened of smtp to true
            smtp.has_port_opened=True
            #set number of current attempts to 0
            stateObject.smtpTryCount=0
            #set number of current proxy attempts to 0
            stateObject.proxyTryCount=0
            #loop indefinitely
            while(True):
                #check if maximum number of emails are already sent
                if (check_max_emails_sent(stateObject,tconfig)):
                    #decrement current threads count
                    #as this thread will die
                    config.totalThreads-=1
                    return
                #if send with proxy enabled
                if (stateObject.config.sendWithProxy):
                    #lock the proxies list
                    proxiesLock.acquire()
                    #if there are no proxies remaining in the list
                    if (len(proxiesQueue)==0):
                        write_mysmtp_log("No proxies available in list",stateObject.threadTag,True,True)
                        #decrement current threads by 1 because this thread will stop
                        config.totalThreads-=1
                        #release the lock on proxies list
                        proxiesLock.release()
                        #return from thread function (Exit the thread)
                        return
                    #get random index for a proxy server
                    proxyIndex=random.randint(0,len(proxiesQueue)-1)
                    #set current proxy to a random proxy server
                    stateObject.proxy=proxiesQueue[proxyIndex]
                    #release the lock on proxies list
                    proxiesLock.release()
                    #check if proxy specified port opened
                    if (not stateObject.proxy.has_port_opened and not check_host(stateObject.proxy.ip,stateObject.proxy.port)):
                        write_mysmtp_log("PROXY "+stateObject.proxy.ip+" have port "+str(stateObject.proxy.port)+" closed",stateObject.threadTag,True,True)
                        #drop this proxy from the list of proxies
                        drop_proxy(proxy)
                        continue
                    #set port opened for this proxy to True
                    stateObject.proxy.has_port_opened=True
                    try:
                        #set proxy server of email sender
                        sender.set_proxy_server(stateObject.proxy)
                    except queue.Empty as err:
                        write_mysmtp_log("Couldn't find a free proxy server",stateObject.threadTag,True,True)
                        #put back the smtp server in case of error in setting proxy server
                        smtpsQueue.put_nowait(stateObject.smtp)
                        time.sleep(2) #2 seconds
                        #continue with the thread again
                        continue
                proxy=stateObject.proxy
                #email will be the recipient's email object
                email=False
                try:
                    email=emailsQueue.get_nowait()
                except queue.Empty as err:
                    #just ignore the empty error
                    pass
                #if no email is retrieved from the queue
                #sleep for few milliseconds and then try again
                if (email==False):
                    time.sleep(10/1000) #10 milliseconds
                    continue
                #set recipient's email
                sender.set_email_to_send(email)
                #if this email has some attempts remaining
                if (email.Tries < EmailToSend.MAX_TRIES):
                    #check if maximum number of emails are already sent
                    if (check_max_emails_sent(stateObject,tconfig)):
                        #decrement current threads count
                        #as this thread will die
                        config.totalThreads-=1
                        return
                    write_mysmtp_log("Sending email to "+email.Mail+",Try#"+str(email.Tries+1))
                    try:
                        #get timestamp at the time of attempt
                        dtStart=time.time()
                        write_mysmtp_log("SMTP: "+smtp.ip+":"+str(smtp.port),stateObject.threadTag,True,False)    
                        if (stateObject.config.sendWithProxy):
                            write_mysmtp_log("PROXY: "+proxy.ip+":"+str(proxy.port),stateObject.threadTag,True,False)
                        #attempt to send the mail
                        sender.send_email()
                        #calculate difference between current timestamp and starting timestamp
                        tsDiff=time.time()-dtStart
                        logText="Email sent to " + email.Mail + "(SMTP: " + smtp.ip + ":"+str(smtp.port)+")"
                        if (stateObject.config.sendWithProxy):
                            logText+=" (PROXY: "+proxy.ip+":"+str(proxy.port)+")"
                        logText+=" in "+str(tsDiff)+" seconds"
                        write_mysmtp_log(logText, myTag,True,False)
                        #email is successfully sent
                        #set Tries to 0 (not required)
                        email.Tries=0
                        #increment the total number of emails sent
                        totalEmailsSent[0]+=1
                        #add the time taken to send this email to global total seconds
                        totalEmailsSent[1]+=tsDiff
                    except smtplib.SMTPException as err:
                        #smtp server returned some failed response
                        #increment number of attempts for this email
                        email.Tries+=1
                        #add this email back to the queue
                        emailsQueue.put_nowait(email)
                        #increment number of attempts for this smtp server
                        stateObject.smtpTryCount+=1
                        write_mysmtp_log("SMTP SmtpException(SMTP: " + smtp.ip + ",Tries: " + str(stateObject.smtpTryCount) + "): " + format(err), myTag,True,False)
                        #if number of attempts have reached MAX_TRIES value then drop this smtp server
                        #smtp server is dropped by breaking the email loop and going back to the first While loop where next smtp will be fetched from the queue
                        if (stateObject.smtpTryCount==MassMailerSmtp.MAX_TRIES):
                            write_mysmtp_log("SMTP is bad after " + str(MassMailerSmtp.MAX_TRIES) + " tries (SMTP: " + smtp.ip + ")", myTag,True,False)
                            break
                    except Exception as err:
                        #general error in sending email
                        #increment number of attempts for this email
                        email.Tries+=1
                        #add this email back to the queue
                        emailsQueue.put_nowait(email)
                        #increment number of attempts for this smtp server
                        stateObject.smtpTryCount+=1
                        write_mysmtp_log("SMTP Exception(SMTP: " + smtp.ip + ",Tries: " + str(stateObject.smtpTryCount) + "): " + format(err), myTag,True,False)
                        #if number of attempts have reached MAX_TRIES value then drop this smtp server
                        #smtp server is dropped by breaking the email loop and going back to the first While loop where next smtp will be fetched from the queue
                        if (stateObject.smtpTryCount==MassMailerSmtp.MAX_TRIES):
                            write_mysmtp_log("SMTP is bad after " + str(MassMailerSmtp.MAX_TRIES) + " tries (SMTP: " + smtp.ip + ")", myTag,True,False)
                            break
        #While loop ended
        #thread will die so decrement the total number of threads running
        config.totalThreads-=1
    except Exception as err:
        #global exception in thread
        write_mysmtp_log("Exception: "+format(err),myTag,True,True)
        #decrement the total number of threads running as this thread will die
        config.totalThreads-=1
    
#thread to monitor the progress about how many emails are sent and how much average time is taken
#and how many threads are active
def monitor_thread_proc(myarg):
    while(True):
        avg=0
        if (totalEmailsSent[0]>0):
            #total seconds / total number of emails sent
            avg=totalEmailsSent[1]/totalEmailsSent[0]
        write_mysmtp_log("Sent: "+str(totalEmailsSent[0])+",Threads: "+str(config.totalThreads)+",Average: "+str(avg)+" seconds","Monitor",False,True)
        time.sleep(2)

def start_the_process():
    write_mysmtp_log("Script started","StartTheProcess",False,True)
    try:
        #load global configuration
        load_config()
        if (config.totalThreads==0):
            raise Exception("Total threads are 0")

        #start monitoring thread
        threading._start_new_thread(monitor_thread_proc,(0,))
        threadIndex=0
        #start all email sending threads
        for x in range(config.totalThreads):
            tconfig=MassMailerThreadConfig() #thread specific configuration
            tconfig.config=config #global config object
            tconfig.threadIndex=threadIndex #index of this thread
            threading._start_new_thread(send_email_thread,(tconfig,))
            threadIndex+=1
    except Exception as err:
        write_mysmtp_log("Exception: "+format(err),"StartTheProcess",False,True)
        raise err

start_the_process()
input("Press enter to stop and exit...")
logFile.close() #close log file
print("Quitting...")
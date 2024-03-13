#close,open apps,chatgpt,dalle integration,whatsapp msg sent integration,gmail using gpt + own voice mail,song play sys,alarm,current time
#take screenshot also now and saving it,reminder
import pyttsx3
from customtkinter import*
from win11toast import toast
from bs4 import BeautifulSoup
import requests
import numpy as np
import cv2
import pyautogui
import speech_recognition as sr
from customtkinter import*
from gtts import gTTS
import mysql.connector as mycon
import time  as time
import os
'''from AppOpener import open as OPEN
from AppOpener import close as CLOSE'''
import pywhatkit as pwk
import datetime
import openai
from apikey import *
import urllib.request
from PIL import Image
from smtplib import *
s_e="cs.pr0j3ct.xii@gmail.com"#sender email
passwd="omtghmrwfehjgcqb"#pass of sender
server=SMTP("smtp.gmail.com",587)
con=mycon.connect(host="localhost",user="root",password="27ramome76A",database="vassi")
cur=con.cursor()
openai.api_key ="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"
language = 'en'
listallowed_c={"akshat":"+919871371357","shreyas":"+917219585006","aditya":"+916299050059","mummy":"+919990610804","papa":"+919990434478"}
listallowed_gm={"akshat":"akshatsrivastava206@gmail.com","aditya":"jacksparrow20231@gmail.com","mummy":"monikasrivastava2004@gmail.com"}
#to mute/unmute
mode="off"

def main():
    global inputaudio
    r=sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("say something")
        audio=r.listen(source)

        try:
            inputaudio=r.recognize_google(audio)
            print("you have said:\n"+inputaudio)
        except Exception as e:
            print("error")
            start()
#alarm checker if time matches it play sound
def check_alarm():
    nowt= datetime.datetime.now()
    current_time=str(nowt.time())
    cur.execute("select* from alarm")
    all_time=cur.fetchall()
    for i in all_time:
        if i[0]==current_time[:5]:
            if mode=="off":
                os.system("alarm.mp3")
                toast("alarm(ringing..)")


def check_reminder():
    nowt2= datetime.datetime.now()
    curr_time=str(nowt2.time())
    cur.execute("select * from reminder")
    all_table=cur.fetchall()
    for i in all_table:
        if i[1]==curr_time[:5]:
            toast("reminder:",i[0])
            



def start():
    while True:

        
        
        
        
#########
        check_alarm()
        check_reminder()
##########################
        with open("mode.txt","r") as f:
            mode=f.read()
#########################
        main()
        
        if "hexa" in inputaudio.lower():#change name of assitant here currently vashi as vassi not
            resp1 = 'yes'
            if mode=="off":
                engine = pyttsx3.init()
                engine.setProperty("rate", 100)
                engine.say(resp1)
                engine.runAndWait()
                time.sleep(4)
            toast("go ahead ask your queries:")
            r2=sr.Recognizer()

            with sr.Microphone() as source2:
                r2.adjust_for_ambient_noise(source2)
                print("ask")


                audio2=r2.listen(source2)
#2nd input to answer
                try:

                    inputaudio2=r2.recognize_google(audio2)
#confirmation msg
                    resp3 = 'ok'
                    if mode=="off":
                        engine = pyttsx3.init()
                        engine.say(resp1)
                        engine.runAndWait()
                    print("you have said:\n"+inputaudio2)
                    inpaudio=inputaudio2.split()
                    print(inpaudio[-1].title())

                    '''elif "open" in inputaudio2.lower():
                        print("loading....")
                        app_open=inpaudio[-1]
                        OPEN(app_open)

                    elif "close" in inputaudio2.lower():
                        print("loading....")
                        app_close=inpaudio[-1]
                        CLOSE(app_close)'''


                    if "delete all alarm" in inputaudio2.lower():
                        cur.execute("delete from alarm;")
                        con.commit()
                        if mode=="off":
                            engine = pyttsx3.init()
                            engine.say("all alarm deleted")
                            engine.runAndWait()
                    elif "delete all reminder" in inputaudio2.lower():
                        cur.execute("delete from reminder;")
                        con.commit()
                        if mode=="off":
                            engine = pyttsx3.init()
                            engine.say("all reminder deleted")
                            engine.runAndWait()
                            
                        
                        


                    elif "mute mode on" in inputaudio2.lower():
                        with open("mode.txt","w") as f:
                            f.write("on")
                        toast("mute mode activated")
                    elif "mute mode off" in inputaudio2.lower():
                        with open("mode.txt","w") as f:
                            f.write("off")
                        engine = pyttsx3.init()
                        engine.say("mute mode deactivated")
                        engine.runAndWait()
                        toast("mute mode deactivated")



#to get current temp of region

                    elif "temperature" in inputaudio2.lower():
                        user_query="temp of"+inputaudio2.lower().split()[-1]
                        URL = "https://www.google.co.in/search?q=" + user_query

                        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
                        page = requests.get(URL, headers=headers)
                        soup = BeautifulSoup(page.content, 'html.parser')
                        result = soup.find(class_='wob_t q8U8x').get_text()
                        print(result+" degree celcius")
                        if mode=="off": 
                            engine = pyttsx3.init()
                            engine.say(result+"degree celcius")
                            engine.runAndWait()
                        toast("temp of "+inputaudio2.lower().split()[-1]+" is "+result+" degree celcius")

#to get daily news update
                    elif "today's news" in inputaudio2.lower()  or "headlines" in inputaudio2.lower():
                        url = 'https://www.bbc.com/news'
                        response = requests.get(url) 
                        soup = BeautifulSoup(response.text, 'html.parser') 
                        headlines = soup.find('body').find_all('h3') 
                        news_line=""
                        for x in headlines: 
                            print(x.text.strip())
                            news_line+=x.text.strip() 
                        if mode=="off": 
                            engine = pyttsx3.init()
                            engine.setProperty("rate", 150)
                            engine.say(news_line)
                            engine.runAndWait()
                        toast(news_line)
                        


#to take screenshot 
                    elif "take screenshot" in inputaudio2.lower():
                        image = pyautogui.screenshot()
                        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                        all_files=os.listdir('.')
                        file_no=0
                        file_name="screenshot.jpg"
                        for i in all_files:
                            if i==file_name:
                                file_no+=1
                                file_name="screenshot"+str(file_no)+".jpg"
                        cv2.imwrite(file_name, image)
                        toast("screenshot saved as:",file_name)

#to send text msg to someone
                    elif "text message" in inputaudio2.lower():
                        if mode=="off":
                            engine = pyttsx3.init()
                            engine.say("what's the message")
                            engine.runAndWait()
                        toast("tell message to be sent")
                        r3=sr.Recognizer()
                        with sr.Microphone() as source:
                            r3.adjust_for_ambient_noise(source)
                            print("tell message to be sent")
                            audio=r3.listen(source)
                            try:
                                inputaudio3=r3.recognize_google(audio)
                                print("you said:\n"+inputaudio3)
                                toast("you said:\n"+inputaudio3)
                                var1=inpaudio[-1].lower()
                                var2=listallowed_c.keys()
#current time ####################################################
                                nowt= datetime.datetime.now()
                                current_time=str(nowt.time())
##################################################################
                                if var1 in var2:
                                     v1=listallowed_c[inpaudio[-1].lower()]
                                     v2=int(current_time[0:2])
                                     v3=int(current_time[3:5])+1  
                                     print("message rec at",v2,v3,"for",v1)
                                     pwk.sendwhatmsg(v1,inputaudio3,v2,v3)#int stuff to add min to current time
                                     if mode=="off":
                                        engine = pyttsx3.init()
                                        engine.say("message sent")
                                        engine.runAndWait()
                                     print("Message Sent!")


                            except Exception as e:
                                print("error")
                                start()
#reminder systummmmmm

                    elif "remind" in inputaudio2.lower():
                        time_var=""
                        for i in inputaudio2:
                            if i.isnumeric():
                                time_var+=i
                        if len(time_var)==1:
                            time_var="0"+time_var+":00"
                            print("reminder set for:",time_var)
                            toast("reminder set for:",time_var)
                            cur.execute("insert into reminder(topic,time) values('{}','{}');".format(inputaudio2.split,time_var))
                            con.commit()
                
                        elif len(time_var)==2:
                            time_var=time_var+":00"
                            print("reminder set for:",time_var)
                            toast("reminder set for:",time_var)
                            cur.execute("insert into reminder(topic,time) values('{}','{}');".format(inputaudio2,time_var))
                            con.commit()
                            
                        elif len(time_var)==3:
                            time_var="0"+time_var[0]+":"+time_var[1:3]
                            print("reminder set for:",time_var)
                            toast("reminder set for:",time_var)
                            cur.execute("insert into reminder(topic,time) values('{}','{}');".format(inputaudio2,time_var))
                            con.commit()
                            
                        elif len(time_var)==4:
                            time_var=time_var[0:2]+":"+time_var[2:4]
                            print("reminder set for:",time_var)
                            toast("reminder set for:",time_var)
                            cur.execute("insert into reminder(topic,time) values('{}','{}');".format(inputaudio2,time_var))
                            con.commit()
                            
                        else:
                            print("unable to catch sorry try again")
                            toast("sorry try again! ")
                




#alarm systummmmm
                    elif "create alarm"  in inputaudio2.lower():
                        print("time:(what)")
                        toast("for what time?")
                        if mode=="off":
                            engine = pyttsx3.init()
                            engine.say("for what time")
                            engine.runAndWait()
                        r8=sr.Recognizer()
                        with sr.Microphone() as source:
                            r8.adjust_for_ambient_noise(source)
                            audio8=r8.listen(source)
                            inputaudio8=r8.recognize_google(audio8)
                            time_var=""
                            for i in inputaudio8:
                                if i.isnumeric():
                                    time_var+=i
                            if len(time_var)==1:
                               time_var="0"+time_var+":00"
                               print("alarm set for:",time_var)
                               toast("alarm set for:",time_var)
                               cur.execute("insert into alarm() values('{}');".format(time_var))
                               con.commit()
                               if mode=="off":
                                    conf1_time = gTTS(text="alarm created", lang=language, slow=True)
                                    conf1_time.save("resp1.mp3")
                                    os.system("resp1.mp3")
                            elif len(time_var)==2:
                                time_var=time_var+":00"
                                print("alarm set for:",time_var)
                                toast("alarm set for:",time_var)
                                cur.execute("insert into alarm() values('{}');".format(time_var))
                                con.commit()
                                if mode=="off":
                                    conf2_time = gTTS(text="alarm created", lang=language, slow=True)
                                    conf2_time.save("resp1.mp3")
                                    os.system("resp1.mp3")
                            elif len(time_var)==3:
                                time_var="0"+time_var[0]+":"+time_var[1:3]
                                print("alarm set for:",time_var)
                                toast("alarm set for:",time_var)
                                cur.execute("insert into alarm() values('{}');".format(time_var))
                                con.commit()
                                if mode=="off":
                                    conf3_time = gTTS(text="alarm created", lang=language, slow=True)
                                    conf3_time.save("resp1.mp3")
                                    os.system("resp1.mp3")
                            elif len(time_var)==4:
                                time_var=time_var[0:2]+":"+time_var[2:4]
                                print("alarm set for:",time_var)
                                toast("alarm set for:",time_var)
                                cur.execute("insert into alarm() values('{}');".format(time_var))
                                con.commit()
                                if mode=="off":
                                    conf4_time = gTTS(text="alarm created", lang=language, slow=True)
                                    conf4_time.save("resp1.mp3")
                                    os.system("resp1.mp3")
                            else:
                                print("unable to catch sorry try again")
                                toast("sorry try again! ")
#to know current time
                    elif "what's the time" in inputaudio2.lower():
                        nowt2= datetime.datetime.now()
                        current_time=str(nowt2.time())
                        final_time="currently it's "+current_time[:5]
                        toast(final_time)
                        if mode=="off":
                           engine = pyttsx3.init()
                           engine.say(final_time)
                           engine.runAndWait()


                            

                            

                        

                        
#create image keyword create image
                    elif "create image" in inputaudio2.lower():
                        print("laoding.....")
                        toast("loading.....")
                        response = openai.Image.create(prompt=inputaudio2,n=1,size="1024x1024")
                        out=response["data"][0]["url"]
                        url = str(out)
                        urllib.request.urlretrieve(url, "vaiimg.png")
                        img = Image.open(r"vaiimg.png")
                        img.show()
###################################


#to open content on web
                    elif "play" in inputaudio2.lower():
                        pwk.playonyt(inpaudio[2:])

#to send gmail to person
                    elif "email" in inputaudio2.lower():
                        if mode=="off":
                            engine = pyttsx3.init()
                            engine.say("do you want to use chatgpt to write email for you")
                            engine.runAndWait()
                        toast("want to use chat gpt to write email choice(yes/no):")
                        r4=sr.Recognizer()
                        with sr.Microphone() as source:
                            
                            r4.adjust_for_ambient_noise(source)
                            print("your choice?(yes/no)")
                            audio4=r4.listen(source)
                            inputaudio4=r4.recognize_google(audio4)
                            print(inputaudio4)
                            if  "yes" in inputaudio4.lower():
                                toast("topic of your mail")
                                if mode=="off":
                                    engine = pyttsx3.init()
                                    engine.say("topic of your email")
                                    engine.runAndWait()
                                print("topic of your mail")
                                
                                r5=sr.Recognizer()
                                with sr.Microphone() as source:
                                
                                    r5.adjust_for_ambient_noise(source)
                                    audio5=r5.listen(source)
                                    inputaudio5=r5.recognize_google(audio5)
                                    print("your said",inputaudio5)
                                    toast("your said",inputaudio5)
                                    print("loading.......")
                                    toast("loading.......")
                  

                                    output = openai.chat.completions.create(  
                                    model="gpt-3.5-turbo", 
                                    messages=[{"role": "user", "content":"write email to"+inpaudio[-1]+"topic:"+inputaudio5}])
                                    email_gpt=(output.choices[0].message.content)
                                    print("output",email_gpt)
                                    toast("output",email_gpt)
                                    print("is it okay(yes/no)")
                                    toast("is it okay(yes/no):")
                                    if mode=="off":
                                        engine = pyttsx3.init()
                                        engine.say("is it okay")
                                        engine.runAndWait()
                                    time.sleep(5)
                                    r7=sr.Recognizer()
                                    with sr.Microphone() as source:
                                        r7.adjust_for_ambient_noise(source)
                                        audio7=r7.listen(source)
                                        inputaudio7=r7.recognize_google(audio7)
                                        print("email going to:",listallowed_gm[inpaudio[-1].lower()])
                                        toast("email going to:",listallowed_gm[inpaudio[-1].lower()])
                                        if  "yes" in inputaudio7:
                                            server.starttls()
                                            server.login(s_e,passwd)
                                            server.sendmail(s_e,listallowed_gm[inpaudio[-1].lower()],email_gpt)
                                            toast("email sent")
                                            if mode=="off":
                                                engine = pyttsx3.init()
                                                engine.say("email sent")
                                                engine.runAndWait()
                                            print("email sent")
                                    
                                        else:
                                            print("email not sent")
                                            toast("email not sent")
                                            if mode=="off":
                                                engine = pyttsx3.init()
                                                engine.say("email not sent")
                                                engine.runAndWait()
                                            start()


                                
                            else:
                                toast("ok tell what to send:")
                                if mode=="off":
                                    engine = pyttsx3.init()
                                    engine.say("ok,tell what to sent")
                                    engine.runAndWait()
                                time.sleep(4)
                                print("tell your mail:")
                                r6=sr.Recognizer()
                                with sr.Microphone() as source:
                                    r6.adjust_for_ambient_noise(source)
                                    audio6=r6.listen(source)
                                    inputaudio6=r6.recognize_google(audio6)
                                    print("email going to:",listallowed_gm[inpaudio[-1].lower()])
                                    if mode=="off":
                                       engine = pyttsx3.init()
                                       engine.say("ok")
                                       engine.runAndWait()
                                    
                                    server.starttls()
                                    server.login(s_e,passwd)
                                    you_mail="Dear human "+",\n"+inputaudio6+"\n Regards Akshat\n(sent using vassi)"
                                    server.sendmail(s_e,listallowed_gm[inpaudio[-1].lower()],you_mail)
                                    toast("email sent to:",listallowed_gm[inpaudio[-1].lower()])


                            
                            





########################


                    else:
                        print("laoding.....")
                        toast("loading.....")
                        output = openai.chat.completions.create(
                        model="gpt-3.5-turbo", 
                        messages=[{"role": "user", "content":inputaudio2+"try making response smaller"}])
                        answer=(output.choices[0].message.content)
                        toast(answer)
                        print(answer)
                        if mode=="off":
                            engine = pyttsx3.init()
                            engine.setProperty("rate", 170)
                            engine.say(answer)
                            engine.runAndWait()
                        time.sleep(3)
                        start()
                    
                except Exception as e:
                    print("error")
                    resp4 = 'sorry try again'
                    if mode=="off":
                        engine = pyttsx3.init()
                        engine.say(resp4)
                        engine.runAndWait()     
                    

     
start()

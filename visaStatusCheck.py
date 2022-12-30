#import libriraies
import urllib.request
import os
from lib2to3.pgen2 import driver
import time
import random
from exceptiongroup import catch
import speech_recognition as sr
from pydub import AudioSegment
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def wait_interval(time1, time2):
    time.sleep( random.uniform(time1,time2))


#links
login_url = "https://online.vfsglobal.dz/Global-Appointment/Account/RegisteredLogin"
selectVac_page = "https://online.vfsglobal.dz/Global-Appointment/Home/SelectVAC"

#webdriver initialize
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
#chrome_options.add_argument("--incognito")
PATH = "C:\Program Files (x86)\chromedriver.exe"

#telegram variables
token = "tokenOfTelegramGroup"
groupId = "groupIdOfTelegram"

#credentials
cred_email = 'example@gmail.com'
cred_password = 'password'

while True :
    try:
        Continue = False
        goOut = False
        driver = webdriver.Chrome(PATH,options=chrome_options)
        driver.get(login_url)
        
        #check if page is loaded by searching a field
        while True:
            try :
                wait_interval(1,1.5)
                email = driver.find_element(By.ID, 'EmailId')
                break
            except :
                time.sleep(61)
        
        #set email field
        email.send_keys(cred_email)
        time.sleep( random.uniform(1,2))
        
        #set password field
        password = driver.find_element(By.ID, 'Password')
        password.send_keys(cred_password)
        time.sleep( random.uniform(1,2))
        
        #select iframe with title reCAPTCHA
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='reCAPTCHA']")))
        
        #click the recaptcha box
        WebDriverWait(driver, 16).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()
        time.sleep( random.uniform(2,3))
        
        #select checkbox and verify if is active 
        checkBox = driver.find_element(By.ID,"recaptcha-anchor")
        if 'recaptcha-checkbox-checked' in checkBox.get_attribute('class').split():
            print('element is active')
            driver.switch_to.default_content()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "submitbtn"))).click()
            Continue = True

        #try with audio to solve captcha 
        else:
            driver.switch_to.default_content()
            time.sleep(3)
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge expires in two minutes']")))
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, ":2"))).click()
            src = driver.find_element(By.ID,"audio-source").get_attribute("src")
            print(src)
            urllib.request.urlretrieve(src,os.getcwd()+ "\\src.mp3")

            # files                                                                       
            src = "src.mp3"
            dst = "final.wav"

            # convert wav to mp3                                                            
            audSeg = AudioSegment.from_mp3("src.mp3")
            audSeg.export(dst, format="wav")
            sample_audio = sr.AudioFile(dst)

            # extract text from audio
            r = sr.Recognizer()
            with sample_audio as source:
                audio = r.record(source)
            key = r.recognize_google(audio)
            print("key = "+key)
            audio_input = driver.find_element(By.ID, 'audio-response')
            time.sleep( random.uniform(2,3))
            audio_input.send_keys(key)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "recaptcha-verify-button"))).click()
            time.sleep( random.uniform(4,5))
            checkBox = driver.find_element(By.ID,"recaptcha-anchor")

            if 'recaptcha-checkbox-checked' in checkBox.get_attribute('class').split():
                print('element is active')
                driver.switch_to.default_content()
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "submitbtn"))).click()
                Continue = True

        if Continue :
            time.sleep( random.uniform(3,4))
            while True :
                time.sleep(4)
                while True:
                    try:
                        driver.find_element(By.LINK_TEXT, "Schedule Appointment").click()
                        time.sleep(4)
                        break
                    except:
                        time.sleep(61)
                        current_url = driver.current_url
                        if login_url in current_url:
                            time.sleep(1)
                            goOut = True
                            break
                if goOut :
                    break
                driver.find_element(By.XPATH, "//select[@id='VisaCategoryId']/option[@value='874']").click()
                time.sleep(2)
                lblMessageText = driver.find_element(By.XPATH, "//label[@id='lblMessage']").text
                lblDateNonPrime = driver.find_element(By.XPATH, "//label[@id='lblDate']").text
                print (lblMessageText)
                lblMessagePrimeText = driver.find_element(By.XPATH, "//label[@id='lblMessagePrime']").text
                lblDatePrime = driver.find_element(By.XPATH, "//label[@id='lblDatePrime']").text
                print (lblMessagePrimeText)

                if lblDateNonPrime.strip():
                    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id=@{groupId}&text={lblDateNonPrime}'
                    res = requests.get(url)
                    if res.status_code==200:
                        print('Successfully sent '+lblDateNonPrime)
                    else:
                        print('ERROR: Could not send Message')

                if lblDatePrime.strip():
                    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id=@{groupId}&text={lblDatePrime}'
                    res = requests.get(url)
                    if res.status_code==200:
                        print('Successfully sent '+lblDatePrime)
                    else:
                        print('ERROR: Could not send Message')

                time.sleep(2)
                print ("non prime date "+lblDateNonPrime+"\nprime date "+lblDatePrime)

                time.sleep(60)
                driver.get(selectVac_page)
                time.sleep(1)
                current_url = driver.current_url
                print("current url after refresh : "+current_url)
                if selectVac_page not in current_url:
                    time.sleep(20)
                    break
        else:
            driver.get(login_url)
    except :
        
        time.sleep(185)
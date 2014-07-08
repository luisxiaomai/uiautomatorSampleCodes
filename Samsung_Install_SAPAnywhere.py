#coding=utf-8
import subprocess
from uiautomator import Device
import sys
import os
import traceback
from selenium import webdriver
from time import sleep
import logging 


class InstallUninstallTest(object):
    
    def __init__(self, serial=None):
        self.serial = serial 
        self.device=Device(self.serial)
        self.log_setting()
        
    def log_setting(self):
        logfilepath = os.path.abspath("C:\Temp")
        if not os.path.exists(logfilepath):
            os.mkdir(logfilepath)
        self.logger = logging.getLogger('mylogger')    
        self.logger.setLevel(logging.INFO) 
        #create handler for writting log into log file.
        fh = logging.FileHandler(os.path.join(logfilepath,"InstallSAPAnywhere.log")) 
        #create handler for writting log into console.
        ch = logging.StreamHandler() 
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') 
        fh.setFormatter(formatter) 
        ch.setFormatter(formatter) 
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)   
   

    def check_device_attached(self):
        out=subprocess.Popen("adb devices",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0]
        match="List of devices attached"
        index=out.find(match)
        target_device_index=out.find(self.serial)
        if index<0:
            raise EnvironmentError("adb is not working.")
        elif target_device_index>0:
            self.logger.info("Device with serial %s attached"%self.serial)
        else:
            raise EnvironmentError("Device with serial %s is not attached"%self.serial)  
        
    def switch_network_to_corporate(self):
        try:
            self.swipe_down_notification_bar()
            self.device(text="WLAN").long_click()
            if not self.device(text="SAP-Corporate").sibling(text="Connected").exists:
                self.device(text="SAP-Corporate").click()
                self.device(text="Connect",className="android.widget.Button").click()
            if self.device(text="Notice").exists:
                self.device(text="connect",className="android.widget.Button").click()
            if self.device(text="SAP-Corporate").sibling(text="Connected").wait.exists(timeout=10000):
                self.logger.info("Network is switched to SAP-Corporate successfully")
            else:
                self.logger.error("Network is switched to SAP-Corporate timeout in 10s") 
        except:
            self.logger.error("Switch network to corporate failed with below %s"%traceback.format_exc()) 
     
    def check_app_installed(self):
        out=subprocess.Popen("adb shell pm list packages sap.sfa.container",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0]
        if len(out)>0:
            self.logger.info("SAP Anywhere is installed alreadlly.")
        else:
            self.logger.info("SAP Anywhere is not installed.")
        return len(out)>0
    
    def uninstall_app(self,appName):
        try:
            self.device.press("home")
            self.device.press("menu")
            self.device(text="Settings",className="android.widget.TextView").click()
            self.device(scrollable=True).scroll.to(text="Application manager")
            self.device(text="Application manager",className="android.widget.TextView").click()
            self.device(scrollable=True).scroll.to(text=appName)
            self.device(text=appName,className="android.widget.TextView").click()
            self.device(text="Uninstall").click()
            self.device(text="OK").click()
            if self.device(text="Uninstalled").wait.exists(timeout=10000)==True:
                self.logger.info("SAP Anywhere is uninstalled successfully.")    
                self.device(text="OK").click()
            else:
                self.logger.error("SAP Anywhere is uninstalled timeout in 10s.")
  
        except:
            self.logger.error("SAP Anywhere is uninstalled failed with below %s"%traceback.format_exc())      
              
    def install_app(self,appName):
        try:
            self.device(textContains=appName).click()
            self.device(text="Install").click()
            if self.device(text="Application installed").wait.exists(timeout=15000)==True:
                self.logger.info("%s is installed successfully."%appName)
                self.device(text="Done").click()
            else:
                self.logger.error("%s is installed timeout in 15s."%appName)                
        except:
            self.logger.error("%s is installed faield with below %s"%(traceback.format_exc(),appName))    
       

    def launch_chromedriver_servie(self):
        try:
            subprocess.Popen("start cmd /k C:\\temp\\chromedriver.exe",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.logger.info("Launch chromedriver service successfully.")
        except:
            self.logger.error("Launch chromedriver service failed with below %s"%traceback.format_exc()) 
            
    def kill_chromedriver_servie(self):
        try:
            
            subprocess.Popen("start cmd /k taskkill /f /im chromedriver.exe",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.logger.info("Terminate chromedriver service successfully.")
        except:
            self.logger.error("Terminate chromedriver service failed with below %s"%traceback.format_exc())  
                
    def download_app_from_appStore(self):
        try:
            capabilities = {
              'chromeOptions': {
                'androidPackage': 'com.android.chrome',
                "androidDeviceSerial":self.serial,
              }
            }
            driver = webdriver.Remote('http://localhost:9515', capabilities)
            driver.get('http://10.58.81.195:8081/store')
            
            driver.find_element_by_xpath('(//div[@class="ref"]//a[contains(text(),"Android")])[1]').click()
            self.device(text="OK").click()
            driver.quit()
            self.swipe_down_notification_bar()
            if self.device(text="Download complete").wait.exists(timeout=60000)==True:
                self.logger.info("SAP Anywhere is downloaded successfully from internal app store.")
            else:
                self.logger.error("SAP Anywhere is downloaded timeout in 60s from internal app store.")
        except:
            self.logger.error("SAP Anywhere is downloaded failed from internal app store with below %s"%traceback.format_exc())     
         
        
    def swipe_down_notification_bar(self):
        self.device.swipe(self.device.width/2, 0 ,self.device.width/2, self.device.height,10)
                
    def test_install_uninstall_SAPAnywhere(self):
        self.logger.info("Log start----------------------------------------")
        self.check_device_attached()
        self.device.screen.on()
        self.device.swipe(self.device.width-10,self.device.height/2,0,self.device.height/2)
        self.switch_network_to_corporate()
        if self.check_app_installed()==True:
            self.uninstall_app("SAP Anywhere")  
        self.kill_chromedriver_servie()
        sleep(2)
        self.launch_chromedriver_servie()            
        self.download_app_from_appStore()
        self.install_app("SAPAnywhere")             
        self.logger.info("Log end----------------------------------------")
           
if __name__=="__main__":
    device_serial=sys.argv[1]
    Install_Uninstall_TestCase=InstallUninstallTest(serial=device_serial)
    Install_Uninstall_TestCase.test_install_uninstall_SAPAnywhere()
    subprocess.Popen("start cmd /k taskkill /f /im cmd.exe",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

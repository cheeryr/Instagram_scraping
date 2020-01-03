from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import math
import os
import requests
import shutil
from xlsxwriter import Workbook

class App:
    def __init__(self, username='',password='', target_username='',path='F:\Photo\insPhoto'):

        self.username = username
        self.password = password
        self.target_username = target_username
        self.path = path
        self.driver = webdriver.Chrome('D:\chromedriver')
        self.main_url = 'https://www.instagram.com/'
        self.all_images = []
        self.driver.get(self.main_url)
        self.error = False
        sleep(2)

        #write log in function
        self.login()
        if self.error == False:
            self.close_dialog_box()
            self.open_target_profile()
        if self.error == False:
            self.scroll_down()
        if self.error == False:
            if not os.path.exists(path):
                os.mkdir(path)
            self.download_images()
        input('stop for now')

        sleep(3)
        #close drive 
        self.driver.close()

    def write_caption_to_excel_file(self, images,caption_path):
        print('Writing to excel')
        workbook = Workbook(os.path.join(caption_path,'captions.xlsx'))
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write(row,0, 'Image name')#(row,column,value)
        worksheet.write(row,1, 'Caption')
        row += 1
        for index, image in enumerate(images):
            filename = 'image_' + str(index) + '.jpg'
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists for this image'
            worksheet.write(row,0,filename)
            worksheet.write(row,1,caption)
            row += 1

        workbook.close()
    def download_captions(self,images):
        captions_folder_path = os.path.join(self.path, 'captions')
        if not os.path.exists(captions_folder_path):
            os.mkdir(captions_folder_path)
        self.write_caption_to_excel_file(images,captions_folder_path)
        '''
        for index, image in enumerate(images):
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption for this image'
            file_name = 'cation_' + str(index) + '.txt'
            file_path = os.path.join(captions_folder_path, file_name)
            link = image['src']
            with open(file_path, 'wb') as file:
                file.write(str('link:'+str(link)+'\n'+'caption:'+caption).encode())
            '''
    def download_images(self):
        self.all_images = list(set(self.all_images))       
        print('Length of all images: ' , len(self.all_images))
        self.download_captions(self.all_images)
        for index, image in enumerate(self.all_images):
                       
            filename = 'image_' + str(index) +'.jpg'
            #os.path.join
            image_path = os.path.join(self.path,filename)
            link = image['src']        
            print("Downloading image ", index)
            
            try:
                response = requests.get(link, stream = True)
                with open(image_path,'wb') as file:
                    shutil.copyfileobj(response.raw, file)#(src,dst)
            except Exception as e:
                print(e)
                print('Could not download image number ', index)
                print('Image link: ', link)
                pass
        



    def scroll_down(self):
        try:            
            no_of_posts = self.driver.find_element_by_xpath('//span[@class="g47SY "]')
            no_of_posts = str(no_of_posts.text).replace(',','')#15,483->15483
            self.no_of_posts = int(no_of_posts)
            
            if self.no_of_posts > 24:#loaded 24 pics when the page first load
                no_of_scrolls = math.ceil((self.no_of_posts-24)/12) + 2#load 12 pics each time scroll down
                try:
                    for value in range(no_of_scrolls):
                        soup = BeautifulSoup(self.driver.page_source, 'lxml')
                        images = soup.find_all('img')
                        for img in images:
                            self.all_images.append(img)
                        
                        self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
                        sleep(2)
                    
                except Exception as e:
                    self.error = True
                    print(e)
                    print('Some error occured while trying to scroll down')
            
            #alternative solution
            """
            while True:
                lenght_of_page = len(self.driver.page_source)
                self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
                sleep(1)
                if len(self.driver.page_source) == lenght_of_page:
                    break
            """
        except Exception:
            self.error = True
            print(e)
            print('Some error occurred while trying to scroll down')
        

    def open_target_profile(self):
        try:
            sleep(1)
            search_bar = self.driver.find_element_by_xpath('//input[@placeholder="Search"]')
            search_bar.send_keys(self.target_username)
            sleep(1)
            target_profile_url =self.main_url +self.target_username + '/'
            self.driver.get(target_profile_url)
            sleep(2)
        except Exception:
            self.error = True
            print('Could not find search bar')


    def close_dialog_box(self):
        try:
            sleep(1)
            notnow_btn = self.driver.find_element_by_xpath('//button[@class="aOOlW   HoLwm "]')
            notnow_btn.click()
            sleep(2)
        except Exception:          
            pass



    def login(self):
        try:
            login_button = self.driver.find_element_by_xpath("//div[@id='react-root']//p[@class='izU2O']/a")
            login_button.click()
            sleep(1)
            try:
                #username_input = self.driver.find_element_by_xpath("//div[@class='_9GP1n   ']//input[@name='username']")
                username_input = self.driver.find_element_by_xpath('//input[@name="username"]')
                username_input.send_keys(self.username)
                sleep(1)
                #password_input = self.driver.find_element_by_xpath("//div[@class='_9GP1n   ']//input[@name='password']")
                password_input = self.driver.find_element_by_name('password')
                password_input.send_keys(self.password)
                sleep(1)
                password_input.submit()
            except Exception:
                self.error = True
                print('Some exception occurred while trying to find username or password field')
        except Exception:
            self.error = True
            print('Unable to find login button')
        






if __name__ =='__main__':
    app = App()

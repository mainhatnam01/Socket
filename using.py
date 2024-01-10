from mail_client import MailClient
from console import menu, send_mail_console, mail_boxes_console, mail_box_console, mail_content_console, display_files_console
import yaml
import os
from constants import mail_boxes_dict
from utils import read_mail_boxes
import json
import time
import threading

with open('config.yml', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
bufferSize = config['Server']['bufferSize']
smtpServer = config['Server']['MailServer']
smtp_port = config['Server']['SMTP']
pop3_port = config['Server']['POP3']
username = config['Authentication']['username']
password = config['Authentication']['password']
filter = config['Filter']

'''
    1. Hàm xử lý thao tác gửi mail
    2. Hàm xử lý thao tác tải mail
    3. Hàm xử lý thao tác mở thư mục mail
    4. Hàm xử lý thao tác mở mail content
'''

def send_mail_worker(mail_client):
    mail_client.connect()
    os.system('cls')
    subject, message, from_addr, to_addr, cc_addr, bcc_addr, attach_files = send_mail_console()
    try:
        mail_client.send_mail(subject, message, from_addr, to_addr, cc_addr, bcc_addr,attach_files)
        print('Send mail successfully!\n')
        os.system('pause')
    except:
        print('Send mail failed!\n')
        os.system('pause')
def download_mail_worker(mail_client):
    os.system('cls')
    print('=====Download mail=====')
    try:
        mail_client.authenticate(username)
        mail_client.download_mail(username)
        print('\nDownload mail successfully!\n')
        os.system('pause')
    except:
        print('\nDownload mail failed!\n')
        os.system('pause')  
def open_mail_box_worker(mail_client, mail_dict):
    while True:
        os.system('cls')
        mail_boxes_console()
        choice_lv2 = input('Your choice: ')
        while choice_lv2 not in ['1', '2', '3', '4', '5', '']:
            print('Invalid choice!')
            choice_lv2 = input('Your choice: ')
        if choice_lv2 == '':
            break
        open_mail_content_worker(mail_client, int(choice_lv2) - 1, mail_dict)
def open_mail_content_worker(mail_client, choice_lv2, mail_dict):
    while True:
        os.system('cls')
        box_index = mail_boxes_dict[choice_lv2]
        # mail_box_console(mail_dict[box_index])
        if mail_box_console(mail_dict[box_index]) == -1:
            break
        choice_lv3 = input('Your choice: ')
        if choice_lv3 == '':
            break
        mail_index = int(choice_lv3) - 1
        os.system('cls')
        mail_content_console(mail_dict[box_index][mail_index])
        #save read status
        mail_dict[box_index][mail_index]['READ'] = True
        with open(f'mail_boxes/{username}/{box_index}/{mail_dict[box_index][mail_index]["NAME_MAIL_FILE"]}', 'w') as f:
            # mail_dict[box_index][mail_index].pop('NAME_MAIL_FILE')
            json.dump(mail_dict[box_index][mail_index], f)
        print('Do you want to download attachment files?\n')
        while True:
            choice_lv4 = input('Y/Yes - N/No: ')
            if choice_lv4 in ['Y', 'Yes', 'y', 'yes']:
                all_files = mail_dict[box_index][mail_index]['FILES'].split(', ') 
                mail_index = mail_dict[box_index][mail_index]['NAME_MAIL_FILE'].split('.')[0][4:] #mail1.json -> 1
                if all_files == []:
                    print('\nThere is not file here!\n')
                    os.system('pause')
                    break
                else:
                    display_files_console(all_files)
                    choice_lv5 = input('Your choice: ').capitalize()
                    mail_client.download_attachment(box_index, mail_index, choice_lv5, username)
                    print('\nDownload attachment files successfully!\n')
                    os.system('pause')
                    break
            elif choice_lv4 in ['N', 'No', 'n', 'no']:
                print('\n')
                os.system('pause')
                break
            else:
                print('\nInvalid choice!\n')

def load_menu():
    while True:
        #menu
        os.system('cls')
        menu(username)
        choice_lv1 = input('Your choice: ')
        while choice_lv1 not in ['1', '2', '3', '4']:
            print('Invalid choice!')
            choice_lv1 = input('Your choice: ')
        if choice_lv1 == '1':
            send_mail_worker(mail_client)
        if choice_lv1 == '2':
            download_mail_worker(mail_client)
        if choice_lv1 == '3':
            os.system('cls')
            mail_dict = read_mail_boxes(username)
            if mail_dict == -1:
                return
            open_mail_box_worker(mail_client, mail_dict)
        if choice_lv1 == '4':
            print('Goodbye!')
            break
            # keep_running = False
def auto_download_mail():
    time.sleep(5)
    while True:
        # print('Downloading mail...')
        mail_client.authenticate(username)
        mail_client.download_mail(username)
        time.sleep(5)
       

if __name__ == '__main__':
    mail_client = MailClient(smtpServer, smtp_port, pop3_port, filter, bufferSize)
    mail_client.connect()

    t1 = threading.Thread(target=load_menu)
    t2 = threading.Thread(target=auto_download_mail)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

# mail_client.send_mail('this is subject', 'this is a message', 'tuannhat@gmail.com', ['tn','tn1','tn2'], ['nhat.jpg', 'xstktl.pdf'])
# mail_client.authenticate('tuannhat1209@gmail.com')
# mail_client.download_mail('tuannhat1209@gmail.com')
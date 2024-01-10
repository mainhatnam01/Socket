import os

'''
	1. Cửa sổ menu
	2. Của sổ gửi mail
	3. Cửa sổ từng folder mail
	4. Cửa sổ danhs sách mail trong folder
	5. Cửa sổ thông tin mail
	6. Cửa sổ danh sách file đính kèm
'''


def menu(user):
	print('=====Welcome to mail client======\n')
	print(f'Current user: {user}\n')
	print('1. Send mail\n')
	print('2. Download mail\n')
	print('3. Open mail boxes\n')
	print('4. Exit\n')

def send_mail_console():
	print('=====Send mail=====\n')
	from_addr = input('From: ')
	to_addr = input('To: ')
	cc_addr = input('CC: ')
	bcc_addr = input('BCC: ')
	subject = input('Subject: ')
	message = input('Message: ')
	attach_files = []
	while True:
		attach_file = input('Attach file (Press Enter to skip): ')
		if attach_file == '':
			break
		#check file exist
		if not os.path.exists(attach_file):
			print('File not found!')
			continue
		#check file size
		size = os.path.getsize(attach_file)
		#if size > 3mb, then continue
		if size > 3145728:
			print('File size is too large (>3Mb)!')
			continue
		attach_files.append(attach_file)
	to_addr = to_addr.split(' ')
	cc_addr = cc_addr.split(' ')
	bcc_addr = bcc_addr.split(' ')
	return subject, message, from_addr, to_addr, cc_addr, bcc_addr, attach_files

def mail_boxes_console():
	print('=====Mail boxes=====\n')
	print('1. Inbox\n')
	print('2. Important\n')
	print('3. Work\n')
	print('4. Project\n')
	print('5. Spam\n')
	print('Enter. Back to menu\n')

def mail_box_console(dict):
	print('=====Mail box=====')
	if len(dict) == 0:
		print('\nNo mail here!\n')
		os.system('pause')
		return -1
	else:
		for i in range(len(dict)):
			print(('\n * ' if not dict[i]['READ'] else '\n  ') + f'{i+1}. SUBJECT: {dict[i]["SUBJECT"]}'.rstrip('\r') + f' - FROM: {dict[i]["FROM"]}\n')
	print('Enter. Back\n')

def mail_content_console(dict):
	print('=====Mail content=====')
	print(f'\nDATE: {dict["DATE"]}\n')
	print(f'FROM: {dict["FROM"]}\n')
	print(f'TO: {dict["TO"]}\n')
	print(f'CC: {dict["CC"]}\n')
	print(f'SUBJECT: {dict["SUBJECT"]}\n')
	print(f'CONTENT: {dict["CONTENT"]}\n')
	print(f'FILES: {"".join(dict["FILES"] if dict["FILES"] != "" else "None")}\n')

def display_files_console(files):
	print('\n=====Attachment files=====\n')
	for i in range(len(files)):
		print(f'{i}. {files[i]}\n')
	print(f'A. All files\n')
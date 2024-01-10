from socket import *
import base64
from utils import extract_mail, filter, create_folder, current_mail_number_on_local
import json
from datetime import datetime

'''
	1. Hàm kết nối
	2. Hàm lấy thông tin trả về từ server
	3. Hàm gửi thông tin đến server
	4. Hàm đăng nhập
	5. Hàm gửi mail
	6. Hàm xác thực nguời dùng để sử dụng pop3
	7. Hàm lấy số lượng mail hiện tại trên server
	8. Hàm lưu file
	9. Hàm tải mail (không bao gồm file đính kèm)
	10. Hàm tải file đính kèm
'''

class MailClient:
	def __init__(self, host, smtp_port, pop3_port, filter, bufferSize=1024):
		self.host = host
		self.smtp_port = smtp_port
		self.pop3_port = pop3_port
		self.filter = filter
		self.bufferSize = bufferSize

	def connect(self):
		self.smtp_socket = socket(AF_INET, SOCK_STREAM)
		print('Connecting to SMTP server...')
		self.smtp_socket.connect((self.host, self.smtp_port))

		self.pop3_socket = socket(AF_INET, SOCK_STREAM)
		print('Connecting to POP3 server...')
		self.pop3_socket.connect((self.host, self.pop3_port))
		self.respone(self.pop3_socket)

	def respone(self, server):
		try:
			recv = ''
			while True:
				part = server.recv(self.bufferSize)
				recv += part.decode()
				if len(part) < self.bufferSize:
					break
			return recv
		except timeout:
			pass

	def request(self, server, message, expect_return_msg=True, display_msg=True):
		server.send(f'{message}\r\n'.encode())
		if expect_return_msg:
			recv = self.respone(server)
			if display_msg: 
				print(recv)
			return recv

	#SMTP
	def login(self, user: str, password: str):
		str = '\x00' + user + '\x00' + password
		base64_str = base64.b64encode(str.encode())
		auth_msg = 'AUTH PLAIN ' + base64_str.decode()
		self.request(self.smtp_socket, auth_msg)

	def send_mail(self, sjt, msg, from_addr, to_addr, cc_addr, bcc_addr, attach_file=None):
		self.request(self.smtp_socket, f'MAIL FROM:<{from_addr}>', expect_return_msg=False)
		for addr in (to_addr + cc_addr) if cc_addr != [] else to_addr:
			self.request(self.smtp_socket, f'RCPT TO:<{addr}>', expect_return_msg=False)
		for addr in bcc_addr:
			self.request(self.smtp_socket, f'RCPT TO:<{addr}>',expect_return_msg=False)
		self.request(self.smtp_socket, f'DATA', expect_return_msg=False)
		self.request(self.smtp_socket, f'DATE: {datetime.today().strftime("%Y-%m-%d %H:%M:%S")}', expect_return_msg=False)
		self.request(self.smtp_socket, f'FROM: {from_addr}', expect_return_msg=False)
		self.request(self.smtp_socket, f'TO: {", ".join(to_addr)}', expect_return_msg=False)
		self.request(self.smtp_socket, f'CC: {", ".join(cc_addr)}', expect_return_msg=False)
		self.request(self.smtp_socket, f'SUBJECT: {sjt}', expect_return_msg=False)
		self.request(self.smtp_socket, f'CONTENT: {msg}', expect_return_msg=False)
		if attach_file:
			self.request(self.smtp_socket, f'FILES: {", ".join(attach_file)}', expect_return_msg=False)
			for file in attach_file:
				with open(file, 'rb') as f:
					l = f.read(self.bufferSize)
					l = base64.b64encode(l)
					self.request(self.smtp_socket, f'ATTACH: {file}: {l}', expect_return_msg=False)
					while l:
						l = f.read(self.bufferSize)
						l = base64.b64encode(l)
						self.request(self.smtp_socket, l, expect_return_msg=False)
		self.request(self.smtp_socket, '.', expect_return_msg=False)

	#POP3
	def authenticate(self, user):
		# self.respone(self.pop3_socket)
		# print("Sent: USER " + user)
		self.request(self.pop3_socket, "USER " + user, display_msg=False)
		
	def current_mail_number_on_server(self):
		# print("Sent: STAT")
		number = self.request(self.pop3_socket, "STAT", display_msg=False)
		number = int(number.split(' ')[1])
		return number
	
	def save_files(self, path, files):
		for file in files:
			if file['data'] != '':
				f = open(path + '/downloaded_' + file['name'], 'wb')
				encoded = bytes(file['data'], 'ascii')
				fdata = base64.b64decode(encoded)
				f.write(fdata)
				f.close()

	def download_mail(self, user):
		create_folder(user)

		current_on_local = current_mail_number_on_local(user) # số lượng mail trên local

		current_on_server = self.current_mail_number_on_server() # số lượng mail trên server

		# print(f'Current on local: {current_on_local}')
		# print(f'Current on server: {current_on_server}')
		for i in range(current_on_local, current_on_server + 1):
			# print("Sent: RETR " + str(i))
			recv = self.request(self.pop3_socket, "RETR " + str(i), display_msg=False)
			# print('Get mail successfully')

			dict = extract_mail(recv)
			folder = filter(dict, self.filter)

			for each_folder in folder:
				# self.save_files(f'mail_boxes/{user}/{each_folder}', dict['FILES'])
				with open(f'mail_boxes/{user}/{each_folder}/mail{i}.json', 'w') as f:
					#json dump file without dict['FILES]
					dict['FILES'] = ', '.join(files['name'] for files in dict['FILES'])
					dict['NAME_MAIL_FILE'] = f'mail{i}.json'
					# dict.pop('FILES')
					json.dump(dict, f)
	
	def download_attachment(self, folder, mail_index, file_index, user):
		recv = self.request(self.pop3_socket, "RETR " + mail_index, display_msg=False)
		# print('Get mail successfully')

		if file_index == 'A':
			dict = extract_mail(recv)
		else:
			dict = extract_mail(recv, index_download=int(file_index))
		# folder = filter(dict, self.filter)

		# for each_folder in folder:
		self.save_files(f'mail_boxes/{user}/{folder}', dict['FILES'])
		# with open(f'mail_boxes/{user}/{folder}/mail{i}.json', 'w') as f:
		# 	#json dump file without dict['FILES]
		# 	dict['FILES'] = ', '.join(files['name'] for files in dict['FILES'])
		# 	dict['NAME_MAIL_FILE'] = f'mail{i}.json'
		# 	# dict.pop('FILES')
		# 	json.dump(dict, f)
		# with open(f'mail_boxes/{username}/inbox/mail{mail_index}.json', 'r') as f:
		# 	dict = json.load(f)
		# self.save_files(f'mail_boxes/{username}/inbox', dict['FILES'])
		# os.rename(f'mail_boxes/{username}/inbox/downloaded_{dict["FILES"][int(file_index)]["name"]}', f'mail_boxes/{username}/inbox/{dict["FILES"][int(file_index)]["name"]}')



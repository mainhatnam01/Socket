import os
import json
text = "+OK 106\nFROM: tuannhat448@gmail.com\nSUBJECT: testing server\nCONTENT: Hello, this is a message from Tuan Nhat 2\n."

'''
	1. Hàm trích xuất thông tin từ chuỗi text 
	2. Hàm kiểm tra xem các phần tử trong 1 list có chứa trong 1 string nhất định nào đó hay không
	3+4. Hàm lọc mail theo config
	5. Hàm tạo folder
	6. Hàm đếm số lượng mail hiện tại trên local
	7. Hàm đọc mail từ local và cho vào dictionary để thuan tiện cho việc xử lý
'''



def extract_mail(text, index_download=None):
	splited_text = text.split('\n')
	dict = {}
	dict['DATE'] = splited_text[1].split(': ')[1]
	dict['FROM'] = splited_text[2].split(': ')[1]
	dict['TO'] = splited_text[3].split(': ')[1]
	dict['CC'] = splited_text[4].split(': ')[1]
	dict['SUBJECT'] = splited_text[5].split(': ')[1]
	dict['CONTENT'] = splited_text[6].split(': ')[1]
	dict['READ'] = False
	dict['FILES'] = []
	if len(splited_text) > 7:
		start_indexes = [i for i in range(len(splited_text)) if 'ATTACH' in splited_text[i]]
		end_indexes = [i for i in range(len(splited_text)) if "b''" in splited_text[i]]
		if index_download != None:
			# extract bytes from text
			file_string = splited_text[start_indexes[index_download]].split(': ')[2][2:-1]
			for i in range(start_indexes[index_download] + 1, end_indexes[index_download]):
				file_string += splited_text[i][2:-1]

			dict['FILES'].append({
				'name': splited_text[start_indexes[index_download]].split(': ')[1],
				'data': file_string
			})
		else:
			# struct = []
			# for i in range(len(start_indexes)):
			# 	struct.append({
			# 		'start_index': start_indexes[i],
			# 		'end_index': end_indexes[i]
			# 	})
			for each_index in range(len(start_indexes)):
				# for ele in struct:
				file_string = splited_text[start_indexes[each_index]].split(': ')[2][2:-1]
				for i in range(start_indexes[each_index] + 1, end_indexes[each_index]):
					file_string += splited_text[i][2:-1]
				dict['FILES'].append({
					'name': splited_text[start_indexes[each_index]].split(': ')[1],
					'data': file_string
				})
	return dict
def check_contains(list, string):
	if list == []:
		return False
	for ele in list:
		if ele in string:
			return True
	return False
def box_filter(filter_config, dict, box):
	return check_contains(filter_config[box]['From'], dict['FROM']) or check_contains(filter_config[box]['Subject'],  dict['SUBJECT']) or check_contains(filter_config[box]['Content'], dict['CONTENT'])
def filter(dict, filter_config):
	folder_list = []
	#check element in list A whether in string B
	if box_filter(filter_config, dict, 'Important'):
		folder_list.append('important')
	if box_filter(filter_config, dict, 'Spam'):
		folder_list.append('spam')
	if box_filter(filter_config, dict, 'Project'):
		folder_list.append('project')
	if box_filter(filter_config, dict, 'Work'):
		folder_list.append('work')
	if folder_list == []:
		folder_list.append('inbox')
	return folder_list
def create_folder(user):
	lists = ['spam', 'important', 'inbox', 'project', 'work']
	for folder in lists:
		if not os.path.exists(f'mail_boxes/{user}/{folder}'):
			os.makedirs(f'mail_boxes/{user}/{folder}')
def current_mail_number_on_local(user):
	#count number of files in folder mail_boxes
	file_list = []
	for each_folder in os.listdir(f'mail_boxes/{user}'):
		file_list += os.listdir(f'mail_boxes/{user}/{each_folder}') # lấy toàn bộ files
	#filter file type
	file_list = [file for file in file_list if file.endswith('.json')]
	num = len(list(set(file_list))) + 1
	return num
def read_mail_boxes(user):
	#count number of files in folder mail_boxes
	folder_dict = {}
	if not os.path.exists(f'mail_boxes/{user}'):
		print('\nDownload mail first!\n')
		os.system('pause')
		return -1
	for each_folder in os.listdir(f'mail_boxes/{user}'):
		file_list = []
		for each_file in os.listdir(f'mail_boxes/{user}/{each_folder}'):
			#check file type
			if not each_file.endswith('.json'):
				continue
			f = open(f'mail_boxes/{user}/{each_folder}/{each_file}', 'r')
			dict = json.load(f)
			file_list.append(dict)
		folder_dict[each_folder] = file_list
	return folder_dict
#folder_dict={
# 	'inbox': [
# 		{
# 			'FROM': 'tuannhat448@gmail',
# 			'SUBJECT': 'testing server'
# 		},
# 		{
# 			'FROM': 'tuannhat448@gmail',
# 			'SUBJECT': 'testing server'
# 		}
# 	],
# 	'important': [
# 		{
# 			'FROM': 'tuannhat448@gmail',
# 			'SUBJECT': 'testing server'
# 		},
# 		{
# 			'FROM': 'tuannhat448@gmail',
# 			'SUBJECT': 'testing server'
# 		}
# 	]
# }

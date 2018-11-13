import os
import shutil

def run():
	print('hello')
	file_name('./')
	print('完成')
	return True

def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        for value in files:
        	shutil.copyfile(value,value+'.gif')

run()
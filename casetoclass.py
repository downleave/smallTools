import os
import re
import shutil

fileList = ['init_code','detail_code','print_code','submit_val','detail_val','edit_val','print_val']
path = './'
instancepath = './instance/'
backpath = './backup/'

def run():
	for method in fileList:
		buildComponents(method)
	print('完成')

def buildComponents(method):
	file = open(path+method+'.txt', 'r', encoding='UTF-8')
	content = file.read()
	# 先找控件名
	namesPattern = re.compile(r'(?<=case\s\')[a-z]+(?=\')')
	nameList = namesPattern.findall(content)
	#去重
	nameList = list(set(nameList))
	replaceContent(nameList, method, content)
	print(method+'成功')
	file.close()

def replaceContent(nameList, method, content):
	for name in nameList:
		filePath = instancepath + name.capitalize() + 'Methods.php'
		if not os.path.exists(filePath):
			#打开模板类
			template = open(path+'template.php', 'r', encoding='UTF-8')
			templatecontent = template.read();
			template.close()
			fileobj = os.open(filePath,os.O_CREAT|os.O_RDWR)
		else:
			fileobj = os.open(filePath,os.O_RDWR)
			templatecontent = os.read(fileobj,1000000)
			templatecontent = bytes.decode(templatecontent)
			os.close(fileobj)
			os.remove(filePath)
			fileobj = os.open(filePath,os.O_CREAT|os.O_RDWR)
		templatecontent = templatecontent.replace('ComponentTemplate', name.capitalize()+'Methods')
		methodCode = getMethodCode(name, content)
		if methodCode:
			templatecontent = templatecontent.replace('###'+method, methodCode)
		os.write(fileobj, bytes(templatecontent, 'UTF-8'))
		#print('生成'+name+'控件成功')
		os.close(fileobj)

def getMethodCode(name, content):
	methodPattern = re.compile(r'(?<=(case\s\''+name+'\':))([\w\W]*?)(?=break;)')
	methodList = methodPattern.findall(content);
	if methodList:
		#检查是否还有switch
		checkSwitch(name,methodList[0][1])
		#有些case共用同一个处理方式，所以遇到case代码应该删除
		retstr = delCaseCode(methodList[0][1])
		return retstr
	return None

def delCaseCode(methodCode):
	casePattern = re.compile(r'\t*case\s\'[a-z]+\':[\w\W]*?\n')
	caseList = casePattern.findall(methodCode);
	#print(caseList)
	if caseList:
		for case in caseList:
			methodCode = methodCode.replace(case, '')
	return methodCode

def checkSwitch(name, code):
	switchPattern = re.compile(r'switch')
	ret = switchPattern.findall(code)
	if ret:
		print("注意，%s里面还有switch" % (name))
	return None

def copyBackup():
	for root, dirs, files in os.walk(backpath):
		for file in files:
			copyfilename = file.replace('Backup.php','.php')
			shutil.copy(backpath+file, instancepath+copyfilename)
			print('复制%s成功' % (copyfilename))
run()
copyBackup()
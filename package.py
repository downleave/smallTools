import os
import re
import shutil

instancepath = './instance/'
backpath = './backup/'
files = []
methodNames = ['init_code','detail_code','print_code','submit_val','detail_val','edit_val','print_val']
packageCodesArray = []

def run():
	getFiles()
	packageCodes()
	#从打包好的数据中生成对应的工具类
	ceateTools()
	replaceCodes()
	print('完成')

def getFiles():
	for root, dirs, filenames in os.walk(instancepath):
		for file in filenames:
			files.append(instancepath + file)

def packageCodes():
	for filePath in files:
		content = getContent(filePath)
		methodCodes = getMethodsCode(content)
		compareCode(methodCodes,filePath)

def getContent(filePath):
	fileobj = os.open(filePath,os.O_RDWR)
	content = os.read(fileobj,1000000)
	content = bytes.decode(content)
	os.close(fileobj)
	return content

def createFile(filePath,content):
	fileobj = os.open(filePath,os.O_CREAT|os.O_RDWR)
	os.write(fileobj, bytes(content, 'UTF-8'))
	os.close(fileobj)
	return True

def getMethodsCode(content):
	methodCodes = dict()
	for name in methodNames:
		code = getCodeByName(name, content)

		if code:
			methodCodes[name] = code
	return methodCodes

def getCodeByName(name, content):
	methodsPattern = re.compile(r'(?<=#<'+name+'>#)([\w\W]*?)(?=#<'+name+'>#)')
	methodsList = methodsPattern.findall(content)
	if methodsList:
		return methodsList[0]
	return None

def compareCode(methodCodes,thisPath):
	for filePath in files:
		if filePath == thisPath:
			continue
		content = getContent(filePath)
		targetMethodCodes = getMethodsCode(content)
		filename = getFileName(filePath)
		for key in targetMethodCodes:
			#检查是否无效函数
			if re.compile('###[\w\W]*').findall(targetMethodCodes[key]):
				continue

			isNewCode = True

			#检查全局变量是否有函数
			for values in packageCodesArray:
				if values['code'] == targetMethodCodes[key]:
					isNewCode = False
					if filename not in values['components']:
						values['components'].append(filename)


			#如全局变量没有，则第一次加入全局变量
			if isNewCode:
				if key in methodCodes:
					if(methodCodes[key] == targetMethodCodes[key]):
						thisname = getFileName(thisPath)
						tmp = dict()
						tmp['code'] = methodCodes[key]
						tmp['method'] = key
						tmp['components'] = []
						tmp['components'].append(filename)
						tmp['components'].append(thisname)
						packageCodesArray.append(tmp)


def getFileName(Path):
	name = Path.replace(instancepath,'')
	name = name.replace('Methods.php','')
	return name

def ceateTools():
	for index,value in enumerate(packageCodesArray):
		end = ''
		if value['method'] == 'submit_val':
			template = 'templateSubmitVal.php'
			templateFunction = '::'+'exec'+'($version,$prm_base,$cmptname,$val,$formitem_setdata,$objid,$fldname,$other_params);'
			ret = '$val = '
		elif value['method'] == 'init_code' or value['method'] == 'detail_code' or value['method'] == 'print_code':
			template = 'templateCode.php'
			templateFunction = '::'+'exec'+'($version, $prm_base, $itemdetail, $replace_data_arr, $data, $other_params);'
			ret = '$ret = '
			end = 'extract($ret);'
		elif value['method'] == 'print_val':
			template = 'templatePrintVal.php'
			templateFunction = '::'+'exec'+'($version, $prm_base, $tbdata, $formitem_setdata, $cmptval, $id, $is_h5_print, $other_params);'
			ret = '$cmptval = '
		else:
			template = 'templateVal.php'
			templateFunction = '::'+'exec'+'($version, $prm_base, $tbdata, $formitem_setdata, $cmptval, $id, $other_params);'
			ret = '$cmptval = '
		filename = getMethodName(value)
		content = getContent(template)
		content = content.replace('ComponentTemplate',filename)
		content = content.replace('functionname','exec')
		content = content.replace('###code',value['code'])
		filePath = './tool/'+filename+'.php'
		value['tool'] = "\n\t\t"+ret+filename + templateFunction+"\n\t\t"
		if end != '':
			value['tool'] = value['tool']+end+"\n\t\t"
		createFile(filePath,content)
def replaceCodes():
	for value in packageCodesArray:
		for component in value['components']:
			filepath = getFilePath(component)
			content = getContent(filepath)
			code = getCodeByName(value['method'], content)
			content = content.replace(code,value['tool'])
			reWriteFiles(filepath,content)
	return True

def reWriteFiles(filepath,content):
	os.remove(filepath)
	createFile(filepath,content)

def getFilePath(filename):
	return instancepath+filename+'Methods.php'

def getMethodName(value):
	namearr = value['method'].split('_',1)
	method = namearr[0].capitalize() + namearr[1].capitalize()
	return value['components'][0]+method+'Tool'
run()
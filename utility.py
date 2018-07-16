# -*- coding:utf-8 -*-  
############################################################################  
''''' 
# 程序：爬虫utility 
# 功能：多维工具集合 
# 创建时间：2018/04/16
# 作者：taylor 
'''
#############################################################################  
import time 
import datetime
def getCurrentDate():
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))
def getCurrentTime():  
        # 获取当前时间  
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
def getTimeWithStamp(timeStamp):
		timeArray = time.localtime(timeStamp)
		return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)        
def get_day_of_day(n=0):
	if (n < 0):
		n = abs(n)
		return datetime.date.today() - datetime.timedelta(days=n)
	else:
		return datetime.date.today() + datetime.timedelta(days=n)
def getStrToDate(string):
	return datetime.datetime.strptime(string,'%Y-%m-%d %H:%M:%s')
def getstringNoCode(string):
	if string == None:
		return ''
	else:
		return string  
def getstringNoCodeRe(string):
	if string == None:
		return ''
	else:
		return string.replace('\n','').replace(' ','')		      
def getstring(string):
	if string == None:
		return ''
	else:
		return string.encode('UTF-8').replace('\n','').replace(' ','')
def getDBstring(string):
	if string == None:
		return '0'
	elif string == '':
		return '0'	
	else:
		return str(string).encode('UTF-8').replace('\n','').replace(' ','')
def getDBNoCode(string):
	if string == None:
		return '0'
	elif string == '':
		return '0'	
	else:
		return str(string).replace('\n','').replace(' ','')
def getDBNoneConvert(string):
	if string == None:
		return 'null'
	elif string == '':
		return 'null'	
	else:
		return str(string).encode('UTF-8').replace('\n','').replace(' ','')					
def getfloat(string):
	if string == None:
		return 0
	elif string == '':
		return 0
	else:
		return float(string)
def getstrip(string):
	return '' if string == None else string.strip()
def getProxy():	
	return {"http": "http://16YPROHH:195778@p10.t.16yun.cn:6446", "https": "http://16YPROHH:195778@p10.t.16yun.cn:6446"}
def getProxy1():	
	return {"http": "http://16PGCOYA:238767@n10.t.16yun.cn:6442", "https": "http://16PGCOYA:238767@n10.t.16yun.cn:6442"}
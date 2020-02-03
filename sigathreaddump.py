#!/usr/bin/python

import gdata.spreadsheet.service
import imaplib, re, email
from email.parser import HeaderParser
from symbol import except_clause

def _FindSheet(feed, name):
	for i, entry in enumerate(feed.entry):
		print '%s %s\n' % (entry.title.text, entry.content.text)

def _FindByName(feed, name):
	for i, entry in enumerate(feed.entry):
		if entry.title.text == name:
			return _ExtractId(entry)

def _ExtractId(entry):
	id_parts = entry.id.text.split('/')
	return id_parts[len(id_parts) - 1]

def _StringToDictionary(row_data):
	dict = {}
	for param in row_data.split('#'):
		temp = param.split('=')
		dict[temp[0]] = temp[1]
	return dict

def _FindOrCreateWorksheetByName(sheet, name):
	wksht_feed = gd_client.GetWorksheetsFeed(sht_id)
	wksht_id = _FindByName(wksht_feed, name)
	if wksht_id == None:
		wksht_id = _ExtractId(gd_client.AddWorksheet(name, 1, 3, sheet))
		entry = gd_client.UpdateCell(1, 1, 'threadid', sheet, wksht_id)
		if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
			print 'Criou coluna threadid!!'
		entry = gd_client.UpdateCell(1, 2, 'stacktrace', sheet, wksht_id)
		if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
			print 'Criou coluna stacktrace!!'
		entry = gd_client.UpdateCell(1, 3, 'numocurrence', sheet, wksht_id)
		if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
			print 'Criou coluna numocurrence!!'
	return wksht_id

def _RecoverWorksheetId(sheet, name):
	try:
		return wksht_dict[name]
	except:
		wksht_dict[name] = _FindOrCreateWorksheetByName(sheet, name)
		return wksht_dict[name]

def _RecoverValue(value):
	if value[-1:] == 'M':
		return float(valor[0:-1]) / 1000
	else:
		return float(valor[0:-1])

gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = 'siga.sms.sp'
gd_client.password = 'sigasaude'
gd_client.source = 'Spreadsheets Monitor'
gd_client.ProgrammaticLogin()
feed = gd_client.GetSpreadsheetsFeed()
sht_id = _FindByName(feed, 'sigathreaddump')

conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login('siga.sms.sp', 'sigasaude')
conn.select('Inbox')
type, data = conn.search(None, 'UnSeen')
wksht_dict = {}
rethread = re.compile("Thread: (\w| |\.|\#|\:|-|/|\[|\]|\(|\))+</b> : priority:(?P<priority>\d+), demon:(?P<demon>true|false), threadId:(?P<threadId>\d+), threadState:(?P<threadState>RUNNABLE|WAITING|TIMED_WAITING|BLOCKED), lockName:(?P<lockName>(\w|\.|\@|\$)+)<br><blockquote>(?P<stackTrace>(\w| |\.|\#|\:|-|/|\[|\]|\(|\)|<br>|\$)+)")
remachine = re.compile('siga_(?P<valor>.+)@prodam\.sp\.gov\.br"')
retimestamp = re.compile('Informacoes servidor SIGA - (?P<valor>.+)min')
mapThreadAnterior = {}
mapThread = {}
mapThreadImpressao = {}
for num in data[0].split():
	type, data = conn.fetch(num, '(RFC822)')
	mail = HeaderParser().parsestr(data[0][1])
	try:
		mapThreadAnterior = mapThread.copy()
		maquina = remachine.search(mail['From']).group('valor').split('.')[0]
		mapThread[maquina] = {}
		timestamp = retimestamp.search(mail['Subject']).group('valor')
		timestamp = '%s-%s-%s %s:%s' % (timestamp[0:4], timestamp[4:6], timestamp[6:8], timestamp[9:11], timestamp[12:])
		content = email.message_from_string(data[0][1])
		for part in content.walk():
			if part.get_filename() == 'jmx2.html':
				payload = part.get_payload(decode=True)
				for s in rethread.finditer(payload):
					stacktrace = s.group('stackTrace').replace('<br>', '\r\n')
					mapThread[maquina][s.group('threadId')] = stacktrace
					if (stacktrace.find('atech') + 1 or stacktrace.find('cesar') + 1 or stacktrace.find('vidatis') + 1) and not stacktrace.startswith('java.net.SocketInputStream.socketRead0') and mapThreadAnterior.has_key(maquina) and mapThreadAnterior[maquina].has_key(s.group('threadId')) and mapThreadAnterior[maquina][s.group('threadId')] == stacktrace:
						if not mapThreadImpressao.has_key(maquina):
							mapThreadImpressao[maquina] = {}
						if not mapThreadImpressao[maquina].has_key(s.group('threadId')):
							mapThreadImpressao[maquina][s.group('threadId')] = {'stackTrace': stacktrace, 'numOcurrence': 1}
						mapThreadImpressao[maquina][s.group('threadId')]['numOcurrence'] = mapThreadImpressao[maquina][s.group('threadId')]['numOcurrence'] + 1 
				break
	except Exception as e:
		print 'Erro: %s' % e

conn.close()
conn.logout()

for k1, v1 in mapThreadImpressao.items():
	for k2, v2 in v1.items():
		record = 'threadid=%s#stacktrace=%s#numocurrence=%s' % (k2, v2['stackTrace'], v2['numOcurrence'])
		entry = gd_client.InsertRow(_StringToDictionary(record), sht_id, _RecoverWorksheetId(sht_id, k1))
		if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
			print 'Inserted %s!' % k1


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
		wksht_id = _ExtractId(gd_client.AddWorksheet(name, 1, 2, sheet))
		entry = gd_client.UpdateCell(1, 1, 'timestamp', sheet, wksht_id)
		if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
			print 'Criou coluna timestamp!'
		entry = gd_client.UpdateCell(1, 2, 'valor', sheet, wksht_id)
		if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
			print 'Criou coluna valor!!'
	return wksht_id

def _RecoverWorksheetId(sheet, name):
	try:
		return wksht_dict[maquina]
	except:
		wksht_dict[maquina] = _FindOrCreateWorksheetByName(sheet, name)
		return wksht_dict[maquina]

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
sht_id = _FindByName(feed, 'sigamonitor')

conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login('siga.sms.sp', 'sigasaude')
conn.select('Inbox')
type, data = conn.search(None, 'UnSeen')
wksht_dict = {}
for num in data[0].split():
	type, data = conn.fetch(num, '(RFC822)')
	mail = HeaderParser().parsestr(data[0][1])
	try:
		maquina = re.search('siga_(?P<valor>.+)@prodam\.sp\.gov\.br"', mail['From']).group('valor').split('.')[0]
		timestamp = re.search('Informacoes servidor SIGA - (?P<valor>.+)min', mail['Subject']).group('valor')
		timestamp = '%s-%s-%s %s:%s' % (timestamp[0:4], timestamp[4:6], timestamp[6:8], timestamp[9:11], timestamp[12:])
		content = email.message_from_string(data[0][1])
		for part in content.walk():
			if part.get_filename() == 'jmx.html':
				payload = part.get_payload(decode=True)
				valor = re.search('PS Old Gen.+used:(?P<valor>.+)b<\/blockquote><\/blockquote><br><.+PS Perm Gen', payload).group('valor')
				valor = _RecoverValue(valor)
				record = 'timestamp=%s#valor=%s' % (timestamp, valor)
				entry = gd_client.InsertRow(_StringToDictionary(record), sht_id, _RecoverWorksheetId(sht_id, maquina))
				if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
					print 'Inserted!'
				break
	except Exception, what:
		print what

conn.close()
conn.logout()

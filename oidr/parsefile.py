import csv
import os
import codecs

print("DELETE FROM SEGMENTION_RULE_VARIABLE;")
print("DELETE FROM SEGMENTATION_RULE;")
print("DELETE FROM CALLGROUP_DEST;")
print("DELETE FROM SCHEDULE;")
print("DELETE FROM CALLGROUP;")
print("DELETE FROM STATE;")
print("DELETE FROM REGION;")
print("DELETE FROM RR_SITE;")
print("DELETE FROM RRSITESETTINGS_SITE;")
print("DELETE FROM RRSITESETTINGS;")
print("DELETE FROM ROUTERULEINTERVAL;")
print("DELETE FROM ROUTERULE;")
print("DELETE FROM LOB;")
print("DELETE FROM SITE_WEEKHOURCONFIG;")
print("DELETE FROM WEEKHOURCONFIG;")
print("DELETE FROM DESTINATION;")
print("DELETE FROM SITE;")
print("DELETE FROM CALLCENTER;")
print("DELETE FROM SEGMENTION_VARIABLE;")
print("DELETE FROM HOLIDAYSLIST;")

def exist_in_list(mylist, elem):
	for e in mylist:
		if e == elem:
			return True
	return False

if os.path.exists("newfile"):
	os.remove("newfile")

fo = codecs.open("newfile", "a", "utf-8")

with codecs.open("oidr", "r", "utf-8") as tsv:
	csvr = csv.reader(tsv, dialect="excel-tab")
	next(csvr)
	for line in csvr:
		criteria = line[1]
		index = criteria.find("(or)")
		while index != -1:
			fo.write("%s\t%s, IVR_GROUP=%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (line[0],criteria[0:index].strip(),line[2],line[2],line[3],line[4],line[5],line[6],line[7]))
			criteria = criteria[index+4:]
			index = criteria.find("(or)")
		else:
			fo.write("%s\t%s, IVR_GROUP=%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (line[0],criteria.strip(),line[2],line[2],line[3],line[4],line[5],line[6],line[7]))

fo.close()

callcenters = {}
lobs = {}
segmentation_rules_var = set()

with codecs.open("newfile", "r", "utf-8") as tsv:
	for line in csv.reader(tsv, dialect="excel-tab"):
		if not line[0] in lobs:
			lobs[line[0]] = {}

		lob = lobs[line[0]]
		if not line[3] in callcenters:
			callcenters[line[3]] = {}

		sites = callcenters[line[3]]

		if not line[4] in sites:
			sites[line[4]] = set()

		destinations = sites[line[4]]

		rules = line[1].replace(" ","").split(",")
		segmentation_rule = {}
		for rule in rules:
			key_value = rule.split("=")
			segmentation_rule[key_value[0]] = key_value[1]
			segmentation_rules_var.add(key_value[0])

		region_pos_map = {"R1":5, "R2":6, "R3":7}

		if "DDD" in segmentation_rule and segmentation_rule["DDD"] in region_pos_map:
			k = segmentation_rule["DDD"]
			v = region_pos_map[k]
			if not k in lob:
				lob[k] = {k: {}}
			state = lob[k][k]
			if not line[2] in state:
				state[line[2]] = {'SegmentationRule': segmentation_rule, 'Destinations': set()}
			state[line[2]]['Destinations'].add(line[v])
			destinations.add(line[v])
		else:
			for (k, v) in region_pos_map.items():
				if line[v].strip() != '-':
					if not k in lob:
						lob[k] = {k: {}}
					state = lob[k][k]
					if not line[2] in state:
						state[line[2]] = {'SegmentationRule': segmentation_rule, 'Destinations': set()}
					state[line[2]]['Destinations'].add(line[v])
					destinations.add(line[v])

holidaylist_id = 1
print("INSERT INTO HOLIDAYSLIST (HOLIDAYSLIST_ID,DESCRIPTION,LAST_UPDATE_TIMESTAMP,NAME) VALUES (%s,'Brazil National Holidays',SYSDATE,'Brazil Holidays');" % holidaylist_id)
lob_id = 0
routerule_id = 0
routeruleinterval_id = 0
routerulesitesettings_id = 0
schedule_id = 0
region_id = 0
state_id = 0
callgroup_id = 0
destination_id = 0
site_id = 0
callcenter_id = 0
wkconfig_id = 0
segmentationrule_id = 0
segmentationrulevar_id = 0
segmentationvar_id = 0

for var in segmentation_rules_var:
        segmentationvar_id+=1
        print("INSERT INTO SEGMENTION_VARIABLE (SEGMENTATIONVAR_ID,NAME) VALUES (%s,'%s');" % (segmentationvar_id, var))

for callcenter in callcenters:
        callcenter_id+=1
        print("INSERT INTO CALLCENTER (CALLCENTER_ID,CALL_LIMIT,CALL_LIMIT_PERIOD,DESCRIPTION,EMERGENCY,LAST_UPDATE_TIMESTAMP,NAME,HOLIDAYSLIST_ID) VALUES (%s,35000,0,'%s',1,SYSDATE,'%s',%s);" % (callcenter_id, callcenter, callcenter, holidaylist_id))
        for site in callcenters[callcenter]:
                site_id+=1
                site_name = "%s - Callcenter %s" % (site, callcenter_id)
                print("INSERT INTO SITE (SITE_ID,CALLLIMIT,CALLLIMIT_PERIOD,DESCRIPTION,EMERGENCY,IS_OVERWRITE_CALLLIMIT,IS_OVERWRITE_WEEKHOURCONFIG,LAST_UPDATE_TIMESTAMP,NAME,CALLCENTER_ID,HOLIDAYSLIST_ID) VALUES (%s,1000,0,'%s',1,0,0,SYSDATE,'%s',%s,%s);" % (site_id, site_name, site_name, callcenter_id, holidaylist_id))
                for destination in callcenters[callcenter][site]:
                        if destination and not destination.isspace():
                                destination_id+=1
                                print("INSERT INTO DESTINATION (DESTINATION_ID,AUDIO_ID,DESCRIPTION,DESTINATION_NUMBER,LAST_UPDATE_TIMESTAMP,NAME,HOLIDAYSLIST_ID,SITE_ID,IS_OVERWRITE_WEEKHOURCONFIG) VALUES (%s,'%s','%s','%s',SYSDATE,'%s',%s,%s,1);" % (destination_id, "audio", destination, destination, destination, holidaylist_id, site_id))
                                for i in range(0,7):
                                        wkconfig_id+=1
                                        print("INSERT INTO WEEKHOURCONFIG (WKCONFIG_ID,ENDTIME,IS_CLOSED,STARTTIME,WEEKDAY,CALLCENTER_ID,DESTINATION_ID,SITE_ID) VALUES (%s,TO_DATE('%s 23:59:59','YYYY-MM-DD HH24:MI:SS'),0,TO_DATE('%s 00:00:00','YYYY-MM-DD HH24:MI:SS'),%s,%s,%s,%s);" % (wkconfig_id, "2100-12-31", "1970-01-01", i, callcenter_id, destination_id, site_id))
                                        print("INSERT INTO SITE_WEEKHOURCONFIG (SITE_SITE_ID,WEEKCONFIGS_WKCONFIG_ID) VALUES (%s, %s);" % (site_id, wkconfig_id))

for lob in lobs:
        lob_id+=1
        routerule_id+=1
        routeruleinterval_id+=1
        routerulesitesettings_id+=1
        routerule_descr = "Route Rule %s" % routerule_id
        routeruleinterval_descr = "Route Rule Interval %s" % routeruleinterval_id
        print("INSERT INTO LOB (LOB_ID,DESCRIPTION,EMERGENCY_DESTINATION,LAST_UPDATE_TIMESTAMP,NAME) VALUES (%s,'%s','123456',SYSDATE,'%s');" % (lob_id, lob, lob))
        print("INSERT INTO ROUTERULE (ROUTERULE_ID,DESCRIPTION,LAST_UPDATE_TIMESTAMP,NAME,LOB_ID) VALUES (%s /*not nullable*/,'%s' /*not nullable*/,SYSDATE /*not nullable*/,'%s' /*not nullable*/,%s /*not nullable*/);" % (routerule_id, routerule_descr, routerule_descr, lob_id))
        print("INSERT INTO ROUTERULEINTERVAL (RRINTERVAL_ID,ENABLED_FRIDAY,ENABLED_MONDAY,ENABLED_SATURDAY,ENABLED_SUNDAY,ENABLED_THURSDAY,ENABLED_TUESDAY,ENABLED_WEDNESDAY,INTERVAL_FROM,LAST_UPDATE_TIMESTAMP,NAME,INTERVAL_TO,ROUTERULE_ID) VALUES (%s,1,1,0,0,1,1,1,TO_DATE('%s 00:00:00','YYYY-MM-DD HH24:MI:SS'),SYSDATE,'%s',TO_DATE('%s 23:59:59','YYYY-MM-DD HH24:MI:SS'),%s);" % (routeruleinterval_id, "1970-01-01", routeruleinterval_descr, "2100-12-31", routerule_id))
        print("INSERT INTO RRSITESETTINGS (RRSITESETTINGS_ID,LAST_UPDATE_TIMESTAMP,PERCENTAGE_ALLOCATION,ROUTING_TYPE,RRINTERVAL_ID) VALUES (%s,SYSDATE,100,'STATIC',%s);" % (routerulesitesettings_id, routeruleinterval_id))
        print("INSERT INTO RRSITESETTINGS_SITE (RRSITESETTINGS_ID,SITE_ID) SELECT %s,SITE_ID FROM SITE;" % routerulesitesettings_id)
        print("INSERT INTO RR_SITE (ROUTERULE_ID,SITE_ID) SELECT %s,SITE_ID FROM SITE;" % routerule_id)
        for region in lobs[lob]:
                region_id+=1
                region_name = "Region %s" % region
                print("INSERT INTO REGION (REGION_ID,DESCRIPTION,LAST_UPDATE_TIMESTAMP,NAME,LOB_ID) VALUES (%s,'%s',SYSDATE,'%s',%s);" % (region_id, region_name, region_name, lob_id))
                for state in lobs[lob][region]:
                        state_id+=1
                        state_name = "State %s" % state
                        print("INSERT INTO STATE (STATE_ID,DESCRIPTION,LAST_UPDATE_TIMESTAMP,NAME,REGION_ID) VALUES (%s,'%s',SYSDATE,'%s',%s);" % (state_id, state_name, state_name, region_id))
                        for callgroup in lobs[lob][region][state]:
                                callgroup_id+=1
                                callgroup_name = "Callgroup %s of %s" % (callgroup_id, state_name)
                                schedule_id+=1
                                print("INSERT INTO CALLGROUP (CALLGROUP_ID,DESCRIPTION,LAST_UPDATE_TIMESTAMP,NAME,STATE_ID) VALUES (%s,'%s',SYSDATE,'%s',%s);" % (callgroup_id, callgroup_name, callgroup_name, state_id))
                                print("INSERT INTO SCHEDULE (SCHEDULE_ID,ENABLE_TYPE,SCHEDULE_END_DATE,SCHEDULE_END_TIME,SCHEDULE_FRIDAY,LAST_UPDATE_TIMESTAMP,SCHEDULE_MONDAY,SCHEDULE_SATURDAY,SCHEDULE_START_DATE,SCHEDULE_START_TIME,SCHEDULE_SUNDAY,SCHEDULE_THURSDAY,SCHEDULE_TUESDAY,SCHEDULE_WEDNESDAY,CALLGROUP_ID,ROUTERULE_ID) VALUES (%s,2,null,TO_DATE('%s 23:59:59','YYYY-MM-DD HH24:MI:SS'),1,SYSDATE,0,1,null,TO_DATE('%s 00:00:00','YYYY-MM-DD HH24:MI:SS'),1,0,0,0,%s,%s);" % (schedule_id, "2100-12-31", "1970-01-01", callgroup_id, routerule_id))
                                for destination in lobs[lob][region][state][callgroup]["Destinations"]:
                                        if destination and not destination.isspace():
                                                print("INSERT INTO CALLGROUP_DEST (CALLGROUP_ID,DESTINATION_ID) SELECT %s, DESTINATION_ID FROM DESTINATION WHERE DESTINATION_NUMBER='%s';" % (callgroup_id, destination))
                                                segmentationrule_id+=1
                                                segmentationrule_descr = "Segmentation Rule %s" % segmentationrule_id
                                                print("INSERT INTO SEGMENTATION_RULE (SEGMENTATIONRULE_ID,ACTIVE,DESCRIPTION,NAME,PRIORITY,CALLGROUP_ID) VALUES (%s,1,'%s','%s',1,%s);" % (segmentationrule_id, segmentationrule_descr, segmentationrule_descr, callgroup_id))
                                                for segmentationrule in lobs[lob][region][state][callgroup]["SegmentationRule"]:
                                                        segmentationrulevar_id+=1
                                                        print("INSERT INTO SEGMENTION_RULE_VARIABLE (SEGMENTATIONRULEVAR_ID,VALUE,SEGMENTATIONRULE_ID,SEGMENTATIONVAR_ID) SELECT %s,'%s',%s,SEGMENTATIONVAR_ID FROM SEGMENTION_VARIABLE WHERE NAME='%s';" % (segmentationrulevar_id, lobs[lob][region][state][callgroup]["SegmentationRule"][segmentationrule], segmentationrule_id, segmentationrule))


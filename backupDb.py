import os
import datetime
try:
	from deploy_settings import BACKUP_DIRECTORY
except ImportError:
	BACKUP_DIRECTORY = "."
current = datetime.datetime.now()
filename = "%s/auto_backup_%s_%s_%s.json"%(BACKUP_DIRECTORY,current.day,current.month,current.year)
command = "./manage.py dumpdata > %s"%filename
try:
	os.system(command)
	print "Backed up data on %s" % (current.strftime("%A %d %B %Y"))
except Exception as e:
	print "Backup failed with message: ",e.message
	

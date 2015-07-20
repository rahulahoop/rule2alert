import os,re,sys

class SnortConf:
	
	def __init__(self, file=None):
		self.conf  = file
		self.vars  = {}
		self.src   = None
		self.dst   = None
		self.sport = None
		self.dport = None

	def default(self, extNet, homeNet):
		#self.vars = {
		#		"HOME_NET": homeNet,
		#		"EXTERNAL_NET": extNet,
		#		"DNS_SERVERS": homeNet,
		#		"SMTP_SERVERS": homeNet,
		#		"HTTP_SERVERS": homeNet,
		#		"SQL_SERVERS": homeNet,
		#		"TELNET_SERVERS": homeNet,
		#		"FTP_SERVERS": homeNet,
		#		"SNMP_SERVERS": homeNet,
		#		"HTTP_PORTS": 80,
		#		"SSH_PORTS": 22,
		#		"SHELLCODE_PORTS": 81,
		#		"ORACLE_PORTS": 1521,
		#		"FTP_PORTS": 21
		#	    }
		if not os.path.exists("Parser/default.conf"):
			print "Default config missing"
			sys.exit(1)

		f = open("Parser/default.conf",'r')
		conf = f.read().splitlines()
		for line in conf:
			name,data  = line.split(" ")
			if data == "HOME_NET": data = homeNet
			elif data == "EXTERNAL_NET": data = extNet
			self.vars[name] = data

		return self.vars
		
	def parse(self):
		f = open(self.conf, 'r')
		conf = f.read().splitlines()
		f.close()

		for line in conf:
			if line.startswith("ipvar"):
				#r = re.search("ipvar\s+(?P<var>[A-Z]+)\s+(?P<data>[\w\[\]\,\$]+)", line)
				r = re.search("ipvar\s+(?P<var>[A-Z_]+)\s+(?P<data>[\[\w+\.\,*\s*\/*\]\$]+)", line)

				if not r: continue
				var  = r.group("var")
				data = r.group("data")
				
				#print var, "VAR"
				#print data, "DATA"
				
				if data[1:] in self.vars:
					data = self.vars[data[1:]]
				self.vars[var] = data
			elif line.startswith("portvar"):
				#r = re.search("portvar\s+(?P<var>[A-Z]_+)\s+(?P<data>[\d\$\[\]\,]+)", line)
				hasEnv = False
				if line.find('$') is not -1:
					envVar = re.findall("\$(\w*)", line)
					hasEnv = True
					data = ''
					for env in envVar:
						if data == '':
							data = self.vars[env]
						else:
							data = str(data[:-1]+ ',' + self.vars[env][1:])
						line = line.replace(str('$' + env + ","), '')
				else:
					r = re.search("portvar\s+(?P<var>[A-Z_]+)\s+(?P<data>\[*[\d+\,*]+\]*)", line)

				if not r: continue
				var  = re.search("portvar\s+(?P<var>[A-Z_]+)\s", line).group("var")
				if not hasEnv:
					data = r.group("data")
				else:
					newPorts = re.search("(?P<data>\[*[\d+\,*]+\]*)", line).group("data")
					data = str(data[:-1]+ ',' + newPorts[1:])
					print data
				#print var, "PORTVARS"
				#print data, "DATA for Ports"
				if data[1:] in self.vars:
					data = self.vars[data[1:]]
				if data.startswith("!$"):
					data = self.vars[data[2:]]
				elif data.startswith("!"):
					data = int(data[1:]) + 1
				elif data.startswith("$"):
					data = self.vars[data[1:]]

				self.vars[var] = data

		return self.vars

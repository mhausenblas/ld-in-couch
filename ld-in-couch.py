#!/usr/bin/python

""" 
  Enables you to store, process and query RDF-based Linked Data in Apache CouchDB.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2012-10-06
@status: init
"""
import sys
import logging
import getopt
import string
import StringIO
import urlparse
import urllib
import urllib2
import string
import cgi
import time
import datetime
import json
import io
from BaseHTTPServer import BaseHTTPRequestHandler
from os import curdir, sep
from couchdbkit import Server, Database, Document, StringProperty, DateTimeProperty, StringListProperty
from restkit import BasicAuth

# Configuration
DEBUG = True
PORT = 7172
COUCHDB_SERVER = 'http://127.0.0.1:5984/'
COUCHDB_DB = 'rdf'
COUCHDB_USERNAME = 'admin'
COUCHDB_PASSWORD = 'admin'

if DEBUG:
	FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
	logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
	FORMAT = '%(asctime)-0s %(message)s'
	logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')

# The main LD-in-Couch service
class LDInCouchServer(BaseHTTPRequestHandler):

	# changes the default behavour of logging everything - only in DEBUG mode
	def log_message(self, format, *args):
		if DEBUG:
			try:
				BaseHTTPRequestHandler.log_message(self, format, *args)
			except IOError:
				pass
		else:
			return
	
	# reacts to GET request by serving static content in standalone mode as well as
	# handles API calls for managing content
	def do_GET(self):
		parsed_path = urlparse.urlparse(self.path)
		target_url = parsed_path.path[1:]
		
		# API calls
		if self.path.startswith('/q/'):
			self.send_error(404,'File Not Found: %s' % self.path) #self.serve_lookup(self.path.split('/')[-1])
		# static stuff (for standalone mode - typically served by Apache or nginx)
		elif self.path == '/':
			self.serve_content('index.html')
		elif self.path.endswith('.ico'):
			self.serve_content(target_url, media_type='image/x-icon')
		elif self.path.endswith('.html'):
			self.serve_content(target_url, media_type='text/html')
		elif self.path.endswith('.js'):
			self.serve_content(target_url, media_type='application/javascript')
		elif self.path.endswith('.css'):
			self.serve_content(target_url, media_type='text/css')
		elif self.path.startswith('/img/'):
			if self.path.endswith('.gif'):
				self.serve_content(target_url, media_type='image/gif')
			elif self.path.endswith('.png'):
				self.serve_content(target_url, media_type='image/png')
			else:
				self.send_error(404,'File Not Found: %s' % target_url)
		else:
			self.send_error(404,'File Not Found: %s' % target_url)
		return
	
	# look up an entity
	def serve_lookup(self, entryid):
		pass
		# try:
		# 	backend = 
		# 	(entry_found, entry) = backend.find(entryid)
		# 	
		# 	if entry_found:
		# 		self.send_response(200)
		# 		self.send_header('Content-type', 'application/json')
		# 		self.end_headers()
		# 		self.wfile.write(json.dumps(entry))
		# 	else:
		# 		self.send_error(404,'Entry with ID %s not found.' %entryid)
		# 	return
		# except IOError:
		# 	self.send_error(404,'Entry with ID %s not found.' %entryid)	
	
	# serves static content from file system
	def serve_content(self, p, media_type='text/html'):
		try:
			f = open(curdir + sep + p)
			self.send_response(200)
			self.send_header('Content-type', media_type)
			self.end_headers()
			self.wfile.write(f.read())
			f.close()
			return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
	
	# serves remote content via forwarding the request
	def serve_URL(self, remote_url, media_type='application/json'):
		logging.debug('REMOTE GET %s' %remote_url)
		self.send_response(200)
		self.send_header('Content-type', media_type)
		self.end_headers()
		data = urllib.urlopen(remote_url)
		self.wfile.write(data.read())
	

# A single entity, expressed in RDF data model
class RDFEntity(Document):
	tstamp = DateTimeProperty() # last update
	s = StringProperty() # the one and only subject
	p = StringListProperty() # list of predicates
	o = StringListProperty() # list of objects
	o_in = StringListProperty() # list of back-links (read: 'object in')

# The Apache CouchDB backend for LD-in-Couch
class LDInCouchBinBackend(object):
	
	# init with URL of CouchDB server, database name, and credentials
	def __init__(self, serverURL, dbname, username, pwd):
		self.serverURL = serverURL
		self.dbname = dbname
		self.username = username
		self.pwd = pwd
		self.server = Server(self.serverURL, filters=[BasicAuth(self.username, self.pwd)])
	
	# adds a triple to the database
	def add(self, triple):
		try:
			db = self.server.get_or_create_db(self.dbname)
			RDFEntity.set_db(db)
			doc = RDFEntity(tstamp = datetime.datetime.utcnow(), s = triple['s'],  p = triple['p'], o = triple['o'], )
			doc.save()
			logging.debug('Added entity with ID %s' %doc['_id'])
			return doc['_id']
		except Exception as err:
			logging.error('Error while adding entity: %s' %err)
			return None
	
	# finds a document via its ID in the database
	def find(self, eid):
		try:
			db = self.server.get_or_create_db(self.dbname)
			if db.doc_exist(eid):
				ret = db.get(eid)
				return (True, ret)
			else:
				return (False, None)
		except Exception as err:
			logging.error('Error while looking up entity: %s' %err)
			return (False, None)
			
	# import and RDF NTriples file triple by triple into JSON documents
	def import_NTriples(self, file_name):
		logging.debug('Processing NTriples file %s' %file_name)
		input_doc = open(file_name, "r")
		for input_line in input_doc:
			triple = input_line.split(' ') # naively assumes SPO is separated by a single whitespace, @@FIXME - employ real NTriples parser here!
			logging.debug('Got triple %s %s %s' %(triple[0], triple[1], triple[2]))

def usage():
	print('Usage: python ld-in-couch.py -c $couchdbserverURL -u $couchdbUser -p $couchdbPwd')
	print('To import an RDF NTriples document:')
	print(' python ld-in-couch.py -i data/example_0.nt')
	print('To run the service (note: these are all defaults, so don\'t need to specify them):')
	print(' python ld-in-couch.py -c http://127.0.0.1:5984/ -u admin -p admin')

if __name__ == '__main__':
	do_import = False
	try:
		# extract and validate options and their arguments
		logging.info('-'*80)
		logging.info('*** CONIGURATION ***')
		opts, args = getopt.getopt(sys.argv[1:], 'hi:c:u:p:', ['help', 'import=', 'couchdbserver=', 'username=', 'password='])
		for opt, arg in opts:
			if opt in ('-h', '--help'):
				usage()
				sys.exit()
			elif opt in ('-i', '--import'):
				input_file = arg
				do_import = True
			elif opt in ('-c', '--couchdbserver'):
				couchdbserver = arg
				logging.info('Using CouchDB server: %s' %couchdbserver)
			elif opt in ('-u', '--username'):
				couchdbusername = arg
				logging.info('Using CouchDB username: %s' %couchdbusername)
			elif opt in ('-p', '--password'): 
				couchdbpassword = arg
				logging.info('Using CouchDB password: %s' %couchdbpassword)
		logging.info('-'*80)
		
		if do_import:
			logging.debug("Importing %s into CouchDB" %input_file)
			backend = LDInCouchBinBackend(serverURL = COUCHDB_SERVER , dbname = COUCHDB_DB, username = COUCHDB_USERNAME, pwd = COUCHDB_PASSWORD)
			backend.import_NTriples(input_file)
		else:
			from BaseHTTPServer import HTTPServer
			server = HTTPServer(('', PORT), LDInCouchServer)
			logging.info('LDInCouchServer started listening on port %s, use {Ctrl+C} to shut-down ...' %PORT)
			server.serve_forever()
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
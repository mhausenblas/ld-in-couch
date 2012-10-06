# Linked Data in CouchDB

## Purpose

This project enables you to store, process and query RDF-based [Linked Data](http://linkeddatabook.com/editions/1.0/) in Apache [CouchDB](http://couchdb.apache.org/).

## Design

There exists a number of related efforts, such as [ipublic/rdf-couchdb](https://github.com/ipublic/rdf-couchdb). However, with LD-in-Couch - which has been designed from scratch - we have the following requirements in mind:

* efficient query processing of RDF (SPARQL, etc.)
* support for sharding graphs automatically (or with minimal user intervention)
* minimise the  time spent in scanning single documents for fields and values (P-O)

Here is the basic idea for how LD-in-Couch manages RDF triples in CouchDB documents:

	let INPUT be an RDF document in NTriples {1} format.
	
	let TRIPLE be the current line (triple) in INPUT in the format [SUBJECT PREDICATE OBJECT].
	
	let DOC be a CouchDB document in a CouchDB database DB {2}.
	
	while  exists(LINE):		# scan each line (triple) of the input document
	
		if isNewSubject(LINE.SUBJECT):		# a new resource, never seen in subject position before
		
			DOC = DB.create_doc( {
				"subject" : LINE.SUBJECT,
				"predicate" : [LINE.PREDICATE],
				"object" : [LINE.OBJECT]
			})
		
		else: # we've already seen the resource in subject position
		
			DOC =  DB.find( "subject" = LINE.SUBJECT)
			
			DOC.add( {
				"predicate" : append(LINE.PREDICATE]),
				"object" : append(LINE.OBJECT])
			})
			
		if not isLiteral(LINE.OBJECT):		# make sure to remember the resource object via back-link
			
			DB.create_or_update_doc( {
				"subject" : LINE.OBJECT,
				"object_in" : DOC._id
			})
	

{1} As in [NTriples](http://www.w3.org/TR/rdf-testcases/#ntriples "RDF Test Cases") 

{2} See [CouchDB reference](http://wiki.apache.org/couchdb/Reference) for details


## Usage

First, in case you haven't done already so, you want to [install Apache CouchDB](http://couchdb.apache.org/) and set it up, that is, create a user called `admin` with the password `admin`. Then you go and [install couchdbkit](http://couchdbkit.org/download.html). 

After that you run once the import task, for example:

	python ld-in-couch.py -i data/example_0.nt
	2012-10-06T10:38:04 INFO --------------------------------------------------------------------------------
	2012-10-06T10:38:04 INFO *** CONIGURATION ***
	2012-10-06T10:38:04 INFO --------------------------------------------------------------------------------
	2012-10-06T10:38:04 INFO Starting import ...
	2012-10-06T10:38:04 INFO Processing NTriples file '/Users/michau/Documents/dev/ld-in-couch/data/example_0.nt'
	2012-10-06T10:38:04 DEBUG --------------------
	2012-10-06T10:38:04 DEBUG #1: S: http://example.org/#m P: http://www.w3.org/1999/02/22-rdf-syntax-ns#type O: http://xmlns.com/foaf/0.1/Person
	2012-10-06T10:38:04 DEBUG http://example.org/#m is a resource I haven't seen in subject position, yet
	2012-10-06T10:38:04 DEBUG  ... created new entity with ID ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//xmlns.com/foaf/0.1/Person"
	2012-10-06T10:38:04 DEBUG The entity document with http://xmlns.com/foaf/0.1/Person in subject position does not exist, yet.
	2012-10-06T10:38:04 DEBUG  ... created new back-link entity with ID ac595818ad836bcda35ea9c9eea6a82f with back-link ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG --------------------
	2012-10-06T10:38:04 DEBUG #2: S: http://example.org/#m P: http://www.w3.org/2000/01/rdf-schema#label O: Michael
	2012-10-06T10:38:04 DEBUG I've seen http://example.org/#m already in subject position
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//example.org/%23m"
	2012-10-06T10:38:04 DEBUG The entity document with http://example.org/#m in subject position has the ID ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG  ... updated existing entity with ID ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG --------------------
	2012-10-06T10:38:04 DEBUG #3: S: http://example.org/#m P: http://xmlns.com/foaf/0.1/knows O: http://example.org/#r
	2012-10-06T10:38:04 DEBUG I've seen http://example.org/#m already in subject position
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//example.org/%23m"
	2012-10-06T10:38:04 DEBUG The entity document with http://example.org/#m in subject position has the ID ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG  ... updated existing entity with ID ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//example.org/%23r"
	2012-10-06T10:38:04 DEBUG The entity document with http://example.org/#r in subject position does not exist, yet.
	2012-10-06T10:38:04 DEBUG  ... created new back-link entity with ID ac595818ad836bcda35ea9c9eea6a789 with back-link ac595818ad836bcda35ea9c9eea6b73a
	2012-10-06T10:38:04 DEBUG --------------------
	2012-10-06T10:38:04 DEBUG #4: S: http://example.org/#r P: http://www.w3.org/1999/02/22-rdf-syntax-ns#type O: http://xmlns.com/foaf/0.1/Person
	2012-10-06T10:38:04 DEBUG I've seen http://example.org/#r already in subject position
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//example.org/%23r"
	2012-10-06T10:38:04 DEBUG The entity document with http://example.org/#r in subject position has the ID ac595818ad836bcda35ea9c9eea6a789
	2012-10-06T10:38:04 DEBUG  ... updated existing entity with ID ac595818ad836bcda35ea9c9eea6a789
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//xmlns.com/foaf/0.1/Person"
	2012-10-06T10:38:04 DEBUG The entity document with http://xmlns.com/foaf/0.1/Person in subject position has the ID ac595818ad836bcda35ea9c9eea6a82f
	2012-10-06T10:38:04 DEBUG  ... updated existing entity with ID ac595818ad836bcda35ea9c9eea6a82f with back-link ac595818ad836bcda35ea9c9eea6a789
	2012-10-06T10:38:04 DEBUG --------------------
	2012-10-06T10:38:04 DEBUG #5: S: http://example.org/#r P: http://www.w3.org/2000/01/rdf-schema#label O: Richard
	2012-10-06T10:38:04 DEBUG I've seen http://example.org/#r already in subject position
	2012-10-06T10:38:04 DEBUG  ... querying view http://127.0.0.1:5984/rdf/_design/lookup/_view/by_subject?key="http%3A//example.org/%23r"
	2012-10-06T10:38:04 DEBUG The entity document with http://example.org/#r in subject position has the ID ac595818ad836bcda35ea9c9eea6a789
	2012-10-06T10:38:04 DEBUG  ... updated existing entity with ID ac595818ad836bcda35ea9c9eea6a789
	2012-10-06T10:38:04 INFO Import completed. I've processed 6 triples and seen 3 subjects (incl. back-links).
	
So, this means the RDF NTriples document `[data/example_o0.nt](https://raw.github.com/mhausenblas/ld-in-couch/master/data/example_0.nt)` that looks as follows:

	<http://example.org/#m> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
	<http://example.org/#m> <http://www.w3.org/2000/01/rdf-schema#label> "Michael" .
	<http://example.org/#m> <http://xmlns.com/foaf/0.1/knows> <http://example.org/#r> .
	<http://example.org/#r> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
	<http://example.org/#r> <http://www.w3.org/2000/01/rdf-schema#label> "Richard" .

... has been mapped to three JSON documents in CouchDB that are akin to:
	
	{
	   "_id": "ac595818ad836bcda35ea9c9eea6b73a",
	   "_rev": "3-fd84df7c2cdb28c9a280ad97041de9d8",
	   "doc_type": "RDFEntity",
	   "s": "http://example.org/#m",
	   "p": [
	       "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
	       "http://www.w3.org/2000/01/rdf-schema#label",
	       "http://xmlns.com/foaf/0.1/knows"
	   ],
	   "o_in": [
	   ],
	   "o": [
	       "http://xmlns.com/foaf/0.1/Person",
	       "Michael",
	       "http://example.org/#r"
	   ]
	}

... which represents the first entity identified by `http://example.org/#m`, and:


	{
	   "_id": "ac595818ad836bcda35ea9c9eea6a789",
	   "_rev": "3-412f313e0e27ef6271d2127b34e5aa79",
	   "doc_type": "RDFEntity",
	   "s": "http://example.org/#r",
	   "p": [
	       "",
	       "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
	       "http://www.w3.org/2000/01/rdf-schema#label"
	   ],
	   "o_in": [
	       "ac595818ad836bcda35ea9c9eea6b73a"
	   ],
	   "o": [
	       "",
	       "http://xmlns.com/foaf/0.1/Person",
	       "Richard"
	   ]
	}

... which represents the second entity identified by `http://example.org/#m=r`, as well as:

	{
	   "_id": "ac595818ad836bcda35ea9c9eea6a82f",
	   "_rev": "2-273821052cbbcb689243edfba4a3df42",
	   "doc_type": "RDFEntity",
	   "s": "http://xmlns.com/foaf/0.1/Person",
	   "p": [
	       ""
	   ],
	   "o_in": [
	       "ac595818ad836bcda35ea9c9eea6b73a",
	       "ac595818ad836bcda35ea9c9eea6a789"
	   ],
	   "o": [
	       ""
	   ]
	}

... which is not really an entity but a pure back-link entry: there are neither property nor object values set but two entries in the `o_in` field, meaning that `http://xmlns.com/foaf/0.1/Person` occurs in object position twice.


## Dependencies

* [couchdbkit](http://couchdbkit.org/)


## License and Acknowledgements

This software is licensed under Apache 2.0 Software License. In case you have any questions, ask [Michael Hausenblas](http://mhausenblas.info/ "Michael Hausenblas").

The design for LD-in-Couch has been influenced and inspired by Ilya Katsov's [NoSQL Data Modeling Techniques](http://highlyscalable.wordpress.com/2012/03/01/nosql-data-modeling-techniques/) as well as the wonderful book [Seven Databases in Seven Weeks: A Guide to Modern Databases and the NoSQL Movement](http://pragprog.com/book/rwdata/seven-databases-in-seven-weeks) written by Eric Redmond and Jim R. Wilson.
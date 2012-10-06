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
			
			DB.create_doc( {
				"subject" : LINE.OBJECT,
				"object_in" : DOC._id
			})
	

{1} As in [NTriples](http://www.w3.org/TR/rdf-testcases/#ntriples "RDF Test Cases") 

{2} See [CouchDB reference](http://wiki.apache.org/couchdb/Reference) for details


## Usage

First, in case you haven't done already so, you want to [install Apache CouchDB](http://couchdb.apache.org/) and set it up, that is, create a user called `admin` with the password `admin`. Then you go and [install couchdbkit](http://couchdbkit.org/download.html). 

After that you run once the import task:

	python ld-in-couch.py -i data/example_0.nt

Now, head over to the Web interface and see if the documents have been created and then try the following:

	curl http://127.0.0.1:5984/rdf/_design/lookup_by_subject/_view/lookup_by_subject

... which should yield something like:

	{
		"total_rows": 2,
		"offset": 0,
		"rows": [{
			"id": "91e30cf2427b98c1be46ca102e200c51",
			"key": "http://example.org/#m",
			"value": {
				"_id": "91e30cf2427b98c1be46ca102e200c51",
				"_rev": "1-fce05065572656630e58f9767151855a",
				"doc_type": "RDFEntity",
				"s": "http://example.org/#m",
				"p": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"],
				"o": ["http://xmlns.com/foaf/0.1/Person"],
				"o_in": []
			}
		}, {
			"id": "91e30cf2427b98c1be46ca102e2006d6",
			"key": "http://example.org/#r",
			"value": {
				"_id": "91e30cf2427b98c1be46ca102e2006d6",
				"_rev": "1-bce3383fbec6f221c4687bf600ce977e",
				"doc_type": "RDFEntity",
				"s": "http://example.org/#r",
				"p": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"],
				"o": ["http://xmlns.com/foaf/0.1/Person"],
				"o_in": []
			}
		}]
	}

## Dependencies

* [couchdbkit](http://couchdbkit.org/)


## License and Acknowledgements

This software is licensed under Apache 2.0 Software License. In case you have any questions, ask [Michael Hausenblas](http://mhausenblas.info/ "Michael Hausenblas").

The design for LD-in-Couch has been influenced and inspired by Ilya Katsov's [NoSQL Data Modeling Techniques](http://highlyscalable.wordpress.com/2012/03/01/nosql-data-modeling-techniques/) as well as the wonderful book [Seven Databases in Seven Weeks: A Guide to Modern Databases and the NoSQL Movement](http://pragprog.com/book/rwdata/seven-databases-in-seven-weeks) written by Eric Redmond and Jim R. Wilson.
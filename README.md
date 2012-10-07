# Linked Data in CouchDB

## Purpose

This project enables you to store, process and query RDF-based [Linked Data](http://linkeddatabook.com/editions/1.0/) in Apache [CouchDB](http://couchdb.apache.org/).

## Design

There exists a number of related efforts, such as [ipublic/rdf-couchdb](https://github.com/ipublic/rdf-couchdb). However, with LD-in-Couch - which has been designed from scratch - we have the following requirements in mind:

* efficient query processing of RDF (SPARQL, etc.)
* support for sharding graphs automatically (or with minimal user intervention)
* minimise the  time spent in scanning single documents for fields and values (P-O)

See the Wiki page [Mapping RDF to JSON documents](https://github.com/mhausenblas/ld-in-couch/wiki/Mapping-RDF-to-JSON-documents) for details about LD-in-Couch's design considerations.

## Usage

First, in case you haven't already done so, you want to [install Apache CouchDB](http://couchdb.apache.org/) and set it up, that is, create a user called `admin` with the password `admin` - alternatively you can update the main script with the [username](https://github.com/mhausenblas/ld-in-couch/blob/master/ld-in-couch.py#L36) and [password](https://github.com/mhausenblas/ld-in-couch/blob/master/ld-in-couch.py#L37) you want to use. Then you go and [install couchdbkit](http://couchdbkit.org/download.html). Last but not least, you need to [create a view](http://guide.couchdb.org/draft/tour.html#mapreduce) in CouchDB, namely as shown in [`views/lookup-by_subject.txt`](https://raw.github.com/mhausenblas/ld-in-couch/master/views/lookup-by_subject.txt).

After all that, you're good to go. Now, for each RDF Triples document you want to process, you run _once_ the import task, for example:

	$ python ld-in-couch.py -i data/example_0.nt -g http://example.org
	2012-10-06T10:38:04 INFO --------------------------------------------------------------------------------
	2012-10-06T10:38:04 INFO *** CONFIGURATION ***
	2012-10-06T10:38:04 INFO --------------------------------------------------------------------------------
	2012-10-06T10:38:04 INFO Starting import ...
	2012-10-06T10:38:04 INFO Importing NTriples file '/Users/michau/Documents/dev/ld-in-couch/data/example_0.nt' into graph <http://example.org>
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

Now you could, for example, look up the entity `http://example.org/#m` in the graph `http://example.org` like so:

	$ curl 'http://127.0.0.1:5984/rdf/_design/entity/_view/by_subject?key="http%3A//example.org/%23mhttp://example.org"'

	{
		"total_rows": 6,
		"offset": 1,
		"rows": [{
			"id": "ea479b6dad91e36e1cefac33b57ad884",
			"key": "http://example.org/#mhttp://example.org",
			"value": [
				[{
					"g": "http://example.org",
					"s": "http://example.org/#m",
					"p": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
					"o": "http://xmlns.com/foaf/0.1/Person",
					"o_type": "uri"
				}],
				[{
					"g": "http://example.org",
					"s": "http://example.org/#m",
					"p": "http://www.w3.org/2000/01/rdf-schema#label",
					"o": "Michael",
					"o_type": "literal"
				}],
				[{
					"g": "http://example.org",
					"s": "http://example.org/#m",
					"p": "http://xmlns.com/foaf/0.1/knows",
					"o": "http://example.org/#r",
					"o_type": "uri"
				}]
			]
		}]
	}


## To Do

* retain subject and object type (add uri, bNode, literal flags)
* add `o_in__with_p` to record with which predicate the resource is back-linked
* use proper NTriples parser, for example, [Sean's impl](http://inamidst.com/proj/rdf/ntriples.py)
* SPARQL support, for example through [fyzz](http://hg.logilab.org/fyzz/file/tip/yappsparser/parser.py)

## Dependencies

* [Apache CouchDB](http://couchdb.apache.org/) 
* [couchdbkit](http://couchdbkit.org/)


## License and Acknowledgements

This software is licensed under Apache 2.0 Software License. In case you have any questions, ask [Michael Hausenblas](http://mhausenblas.info/ "Michael Hausenblas").

The design for LD-in-Couch has been influenced and inspired by Ilya Katsov's [NoSQL Data Modeling Techniques](http://highlyscalable.wordpress.com/2012/03/01/nosql-data-modeling-techniques/) as well as the wonderful book [Seven Databases in Seven Weeks: A Guide to Modern Databases and the NoSQL Movement](http://pragprog.com/book/rwdata/seven-databases-in-seven-weeks) written by Eric Redmond and Jim R. Wilson.
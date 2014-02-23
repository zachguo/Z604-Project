#! /usr/bin/python

# Generate dependent variable in MongoDB.
# The collection name of metadata source is assumed to be "metadata".
# The collection name of extracted dependent variable is "dv".
# To run: python getDV.py path/to/metadata.xml

from pymongo import MongoClient
import xml2json, re, sys, json

def xml2mongo(filename, db):
	# insert xml metadata into mongoDB
	try:
		with open(filename) as fin:
			for doc in xml2json.xml2json(fin.read()).split('\n'):
				db.metadata.insert(json.loads(doc))
		print "Collection 'metadata' is successfully inserted into 'HTRC' database."
	except IOError:
		print "Failed to insert 'metadata' collection into MongoDB."

def generateDV(db):
	# generate collection for dependent variable
	try:
		for doc in db.metadata.find({"language":"eng"}, {"date":1}):
			if "date" in doc:
				date = doc["date"]
				if re.search(r"^\D*(\d{4}).*$", date):
					doc["date"] = re.subn(r"^\D*(\d{4}).*$", r"\1", date)[0]
				else:
					doc["date"] = "ERROR: "+date
			db.dv.insert(doc)
		print "Collection 'dv' is successfully inserted into 'HTRC' database."
	except IOError:
		print "Failed to insert 'dv' collection into MongoDB."

def main(filename):
	client = MongoClient('localhost', 27017)
	db = client.HTRC
	collections = db.collection_names()
	if "dv" in collections:
		print "Collection 'dv' already exists in 'HTRC' database."
	elif "metadata" in collections:
		print "Collection 'metadata' already exists in 'HTRC' database. Start generating 'dv' using existing 'metadata' collection."
		generateDV(db)
	else:
		xml2mongo(filename, db)
		generateDV(db)
	# Test
	print "empty date: ", db.dv.find({"date":""}).count();
	print "nonexistent date: ", db.dv.find({"date":{"$exists":0}}).count();
	print "empty&nonexistent date: ", db.dv.find({"$or":[{"date":""},{"date":{"$exists":0}}]}).count();
	print "erroneous date: ", db.dv.find({"date":{"$regex":"^ERROR:"}}).count();
	print "valid date: ", db.dv.find({"date":{"$regex":"^\d{4}"}}).count();

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Please provide XML metadata filename."
	elif not sys.argv[1].endswith(".xml"):
		print "Invalid XML metadata filename."
	else:
		main(sys.argv[1])
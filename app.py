from flask import Flask, render_template, request # Clean up needed
from wtforms import Form, TextAreaField, validators
import pickle
import sqlite3
import os
import numpy as np
import ast
from collections import OrderedDict

# import HashingVectorizer from local dir ?
#from vectorizer import vect

####### Preparing the d2v model
cur_dir = os.path.dirname(__file__)
d2v_model = pickle.load(open(os.path.join(cur_dir, 'pkl_objects/model.pkl'), 'rb'))
with open(os.path.join(cur_dir, 'data/serveIDs.txt'), 'r') as f:
	URIs = [line.replace('\n', '') for line in f]

stage = 0 # initialise our rec counter

print(len(URIs)) # confirm all URIs are loaded
#print(str(URIs))
#db = os.path.join(cur_dir, 'reviews.sqlite')

artists = []

with open('data/distinct_artists', 'r') as f:
	parsed = ast.parse(f.read()) # security risks?

first_dict = next(node for node in ast.walk(parsed) if isinstance(node, ast.Dict))
keys = (node.s for node in first_dict.keys)
vals = (node.s for node in first_dict.values)
od = OrderedDict(zip(keys, vals))




def sqlite_entry(path, document, y):
	conn = sqlite2.connect(path)
	c = conn.cursor()
	c.execute("INSERT INTO recommendations_db (recommendation[n]))"\
	" VALUES (?, ?, DATETIME('now'))", (document, y)) #change date time to a better suited primary key
	conn.commit()
	conn.close()
	

app = Flask(__name__)
class HelloForm(Form):
	sayhello = TextAreaField('',[validators.DataRequired()])

@app.route('/<int:stage>')
def index(stage):
	#form = NextButton(request.form)
	return render_template('pre_study.html', stage=stage)

@app.route('/app_phase/<int:stage>') #methods=['POST'])
def appPhase(stage):
	#form = HelloForm(request.form)
	#if request.method == 'POST' and form.validate():
	#	name = request.form['sayhello']
	#	return render_template('hello.html', name=name)
	artists = od.keys()
		
	return render_template('app_phase.html', artists=artists, stage=stage)# form=form

# View specific entry
@app.route('/release_recommendation/<int:stage>/<string:selected_artist>')
def release_recommendation(selected_artist, stage):
	check = False
	shift = 1
	cur_uri = od[selected_artist] # query into artist dictionary, returns URI of corresponding artist release
	print(cur_uri)
	cur_index = URIs.index('spotify:album:' + cur_uri) + 1
	print('curindex =' + str(cur_index))
	reclist = (d2v_model.docvecs.most_similar(str(cur_index)+'.txt')) #returns a list, first index is most similar
	print(reclist)
	rec = [x[0] for x in reclist][0]
	rec_file = str(rec)
	#print(rec)
	rec_index = int(rec_file.split('.txt')[0])
	if (URIs[rec_index-1].__contains__('spotify:album:') and rec_index != 5133): #if 5133 is first then stops it skipping to an unmapped uri
		check = True
	if (rec_index == 5133): # this rogue release has a vector space which throws off the cos sim
		rec_file = str([x[0] for x in reclist][shift])
		rec_index = int(rec_file.split('.txt')[0])
	while (check==False): 
		rec_file = str([x[0] for x in reclist][shift])
		rec_index = int(rec_file.split('.txt')[0])
		if (rec_index == 5133): # this rogue review has a vector space which throws off the cos sim
			rec_file = str([x[0] for x in reclist][shift+1])
			rec_index = int(rec_file.split('.txt')[0])
		if (URIs[rec_index-1].__contains__('spotify:album:')):
			check=True
		else: # shift along and try again
			shift += 1
	stage += 1
	if (check==True): 
		print(rec_index)	
		uri = URIs[rec_index-1].split('spotify:album:')[1] # - 1 as file indexes start at 1 - 95% on this
	return render_template('release_recommendation.html', uri=uri, stage=stage)
	

@app.route('/post_study')
def postStudy():
	return render_template('post_study.html')


if __name__ == '__main__':
	app.run('0.0.0.0', port=8000, debug=True)

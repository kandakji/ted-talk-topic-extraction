from flask import Flask, jsonify, request, abort, make_response
from corpus import retrieve_prepare_subtitles, retrieve_prepare_tags
from models import tfidf, lda, lftm, ntm
import time

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

#################################################################
#							PREDICTION							#
#################################################################

@app.route('/api/tfidf/predict/', methods=['POST'])
def extract_topics_tfidf():
	start = time.time()
	# Extract request body parameters
	url = request.json['url']
	# Retrieve subtitles
	subtitles = retrieve_prepare_subtitles(url)
	if 'not found' == subtitles:
		return jsonify({'error':'video could not be retreived'})
	# Load the model
	model = tfidf()
	model.load()
	# Perform Inference
	results = model.predict(subtitles)
	# Retrieve tags
	tags = retrieve_prepare_tags(url)
	# Evaluate
	score = model.evaluate(results, tags)
	dur = time.time() - start
	# Return resutls and score
	return jsonify({'time' : dur, 'results':results, 'score':score})

@app.route('/api/lda/predict', methods=['POST'])
def extract_topics_lda():
	start = time.time()
	# Extract request body parameters
	subtitles = retrieve_prepare_subtitles(request.json['url'])
	if 'not found' == subtitles:
		return jsonify({'error':'video could not be retreived'})
	# Load the model
	model = lda()
	model.load()
	# Perform Inference
	results = model.predict(subtitles)
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'results' : results})

@app.route('/api/lftm/predict', methods=['POST'])
def extract_topics_lftm():
	start = time.time()
	# Extract request body parameters
	subtitles = retrieve_prepare_subtitles(request.json['url'])
	if 'not found' == subtitles:
		return jsonify({'error':'video could not be retreived'})
	# Load the model
	model = lftm()
	# Perform Inference
	results = model.predict(subtitles)
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'results' : results})

#################################################################
#							TAGS								#
#################################################################

@app.route('/api/tags', methods=['POST'])
def extract_tags():
	start = time.time()
	# Retrieve tags
	tags = retrieve_prepare_tags(request.json['url'])
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'tags':tags})

#################################################################
#							TOPICS								#
#################################################################

@app.route('/api/lda/topics', methods=['GET'])
def get_topics_lda():
	start = time.time()
	# Load the model
	model = lda()
	model.load()
	# Retrieve topics
	topics = model.topics()
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'topics': topics})

@app.route('/api/lftm/topics', methods=['GET'])
def get_topics_lftm():
	start = time.time()
	# Load the model
	model = lftm()
	# Retrieve topics
	topics = model.topics()
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'topics': topics})

@app.route('/api/ntm/topics', methods=['GET'])
def get_topics_ntm():
	start = time.time()
	# Load the model
	model = ntm()
	model.load()
	# Retrieve topics
	topics = model.topics()
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'topics': topics})


#################################################################
#							TRAINING							#
#################################################################

@app.route('/api/tfidf/train', methods=['POST'])
def train_tfidf():
	start = time.time()
	# Load model
	model = tfidf()
	# Train model
	results = model.train(request.json['datapath'],
		(int(request.json['min_ngram']),
		int(request.json['max_ngram'])),
		float(request.json['max_df']),
		float(request.json['min_df']))
	dur = time.time() - start
	# return result
	return jsonify({'time' : dur, 'result':results})

@app.route('/api/lda/train', methods=['POST'])
def train_lda():
	start = time.time()
	# Load model
	model = lda()
	# Train model
	results = model.train(request.json['datapath'],
		int(request.json['num_topics']),
		int(request.json['alpha']),
		int(request.json['iterations']),
		int(request.json['optimize_interval']),
		float(request.json['topic_threshold']))
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'result':results})

@app.route('/api/lftm/train', methods=['POST'])
def train_lftm():
	start = time.time()
	# Load model
	model = lftm()
	# Train model
	results = model.train(request.json['datapath'],
		request.json['ntopics'],
		request.json['alpha'],
		request.json['beta'],
		request.json['lambda'],
		request.json['initer'],
		request.json['niter'],
		request.json['topn'])
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'result':results})

@app.route('/api/ntm/train', methods=['POST'])
def train_ntm():
	start = time.time()
	# Load model
	model = ntm()
	# Train model
	results = model.train(request.json['datapath'],
		int(request.json['n_topics']),
		int(request.json['batch_size']),
		int(request.json['n_epochs']),
		float(request.json['lr']),
		float(request.json['l1_doc']),
		float(request.json['l1_word']),
		int(request.json['word_dim']))
	dur = time.time() - start
	# return result
	return jsonify({'time' : dur, 'result':results[0], 'fmeasure':str(results[1]), 'loss': str(results[2])})

#################################################################
#							EVALUATION							#
#################################################################

@app.route('/api/lda/eval', methods=['GET'])
def eval_lda():
	start = time.time()
	# Load model
	model = lda()
	model.load()
	# Evaluate model
	score = model.evaluate()
	dur = time.time() - start
	# Retrun results
	return jsonify({'time' : dur, 'score':score})

@app.route('/api/lftm/eval', methods=['GET'])
def eval_lftm():
	start = time.time()
	# Load model
	model = lftm()
	# Evaluate model
	score = model.evaluate()
	dur = time.time() - start
	# Return results
	return jsonify({'time' : dur, 'score':score})

if __name__ == '__main__':
	app.run(debug=True)
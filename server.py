import os
import time
import json

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from swagger_ui import flask_api_doc as api_doc

from topic_model import TfIdfModel, LdaModel, LftmModel, Doc2TopicModel, GsdmmModel
from topic_model.corpus import retrieve_prepare_tags, prepare_subtitles

__package__ = 'topic_model'

app = Flask(__name__)
CORS(app)
api_doc(app, config_path='swagger.yml', url_prefix='', title='Topic Model API')

models = {
    'gsdmm': GsdmmModel,
    'doc2topic': Doc2TopicModel,
    'lftm': LftmModel,
    'lda': LdaModel,
    'tfidf': TfIdfModel
}


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


#################################################################
#							PREDICTION							#
#################################################################

@app.route('/api/<string:model_type>/predict', methods=['POST'])
def predict(model_type):
    start = time.time()
    # Extract request body parameters
    # Retrieve subtitles
    subtitles = prepare_subtitles(str(request.data))
    # Load the model
    model = models[model_type]()
    # Perform Inference
    results = model.predict(subtitles)
    dur = time.time() - start
    # Return results and score
    return jsonify({'time': dur, 'results': results}), 200


@app.route('/api/<string:model_type>/predict_corpus', methods=['POST'])
def predict_corpus(model_type):
    start = time.time()

    # Load the model
    model = models[model_type]()
    # Perform Inference
    results = model.predict_corpus(request.json['datapath'])
    dur = time.time() - start
    # Return results and score
    return jsonify({'time': dur, 'results': results}), 200


#################################################################
#							TAGS								#
#################################################################

@app.route('/api/tags', methods=['POST'])
def extract_tags():
    try:
        start = time.time()
        # Retrieve tags
        tags = retrieve_prepare_tags(request.json['url'])
        dur = time.time() - start
        # Return results
        return jsonify({'time': dur, 'tags': tags}), 200
    except:
        return jsonify({'error': "Invalid input or error occured."}), 400


#################################################################
#							TOPICS								#
#################################################################

@app.route('/api/<string:model_type>/topics', methods=['GET'])
def get_topics(model_type):
    start = time.time()
    # Load the model
    model = models[model_type]()
    # Retrieve topics
    topics = model.topics()
    dur = time.time() - start
    # Return results
    return jsonify({'time': dur, 'topics': topics}), 200


#################################################################
#							TRAINING PREDICTIONS								#
#################################################################

@app.route('/api/<string:model_type>/training_predictions', methods=['GET'])
def get_training_prediction(model_type):
    start = time.time()
    # Load the model
    model = models[model_type]()
    # Retrieve topics
    topics = model.get_corpus_predictions()
    dur = time.time() - start
    # Return results
    return jsonify({'time': dur, 'topics': topics}), 200


#################################################################
#							COHERENCE							#
#################################################################


@app.route('/api/<string:model_type>/coherence', methods=['POST'])
def get_coherence(model_type):
    start = time.time()
    # Load the model
    model = models[model_type]()
    # Retrieve topics
    args = request.json
    c = args['metric'] if 'metric' in args else 'c_v'
    print('Coherence %s for %s' % (c, model_type))
    topics = model.coherence(args['datapath'], coherence=c)
    dur = time.time() - start
    # Return results
    response = jsonify({'time': dur, 'topics': topics})
    os.makedirs('/data/out', exist_ok=True)
    with open('/data/out/%s.%s.json' % (model_type, c), 'w') as f:
        json.dump(response, f)
    return response, 200


#################################################################
#							TRAINING							#
#################################################################

@app.route('/api/tfidf/train', methods=['POST'])
def train_tfidf():
    start = time.time()
    # Load model
    model = TfIdfModel()
    # Train model
    results = model.train(request.json['datapath'],
                          (int(request.json['min_ngram']),
                           int(request.json['max_ngram'])),
                          float(request.json['max_df']),
                          float(request.json['min_df']))
    dur = time.time() - start
    print('Training TFIDF done in %f' % dur)
    # return result
    return jsonify({'time': dur, 'result': results}), 200


@app.route('/api/lda/train', methods=['POST'])
def train_lda():
    start = time.time()
    # Load model
    model = LdaModel()
    # Train model
    results = model.train(request.json['datapath'],
                          int(request.json['num_topics']),
                          float(request.json['alpha']),
                          int(request.json['random_seed']),
                          int(request.json['iterations']),
                          int(request.json['optimize_interval']),
                          float(request.json['topic_threshold']))
    dur = time.time() - start
    print('Training LDA done in %f' % dur)
    # Return results
    return jsonify({'time': dur, 'result': results}), 200


@app.route('/api/lftm_0/train', methods=['POST'])
def train_lftm():
    start = time.time()
    # Load model
    model = LftmModel()
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
    print('Training LFTM done in %f' % dur)
    # Return results
    return jsonify({'time': dur, 'result': results}), 200


@app.route('/api/doc2topic/train', methods=['POST'])
def train_ntm():
    start = time.time()
    # Load model
    model = Doc2TopicModel()
    # Train model
    results = model.train(request.json['datapath'],
                          int(request.json['n_topics']),
                          int(request.json['batch_size']),
                          int(request.json['n_epochs']),
                          float(request.json['lr']),
                          float(request.json['l1_doc']),
                          float(request.json['l1_word']),
                          int(request.json['word_dim']), return_scores=True)
    dur = time.time() - start
    print('Training NTM done in %f' % dur)
    # return result
    return jsonify({'time': dur, 'result': results[0], 'fmeasure': str(results[1]), 'loss': str(results[2])}), 200


@app.route('/api/gsdmm/train', methods=['POST'])
def train_gsdmm():
    start = time.time()
    # Load model
    model = GsdmmModel()
    # Train model
    results = model.train(request.json['datapath'],
                          int(request.json['num_topics']),
                          float(request.json['alpha']),
                          float(request.json['beta']),
                          int(request.json['n_iter']))
    dur = time.time() - start
    print('Training GSDMM done in %f' % dur)
    # Return results
    return jsonify({'time': dur, 'result': results}), 200


if __name__ == '__main__':
    app.run(debug=False, threaded=True, host='0.0.0.0')

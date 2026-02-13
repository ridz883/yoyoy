from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'status': 'AllDownloader API by Ridzz',
        'version': '2.0',
        'message': 'API is working!'
    })

@app.route('/api/youtube')
def youtube():
    url = request.args.get('url')
    return jsonify({'success': True, 'url': url, 'message': 'YouTube endpoint'})

@app.route('/api/tiktok')
def tiktok():
    url = request.args.get('url')
    return jsonify({'success': True, 'url': url, 'message': 'TikTok endpoint'})

@app.route('/api/instagram')
def instagram():
    url = request.args.get('url')
    return jsonify({'success': True, 'url': url, 'message': 'Instagram endpoint'})

@app.route('/api/twitter')
def twitter():
    url = request.args.get('url')
    return jsonify({'success': True, 'url': url, 'message': 'Twitter endpoint'})

@app.route('/api/facebook')
def facebook():
    url = request.args.get('url')
    return jsonify({'success': True, 'url': url, 'message': 'Facebook endpoint'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

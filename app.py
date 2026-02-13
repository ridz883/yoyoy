from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({
        'status': 'AllDownloader API by Ridzz',
        'version': '2.0',
        'endpoints': [
            '/api/youtube',
            '/api/tiktok',
            '/api/instagram',
            '/api/twitter',
            '/api/spotify',
            '/api/facebook',
            '/api/gdrive',
            '/api/github',
            '/api/mediafire',
            '/api/pinterest'
        ]
    })

@app.route('/api/youtube')
def youtube():
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'title': 'YouTube Video',
        'thumbnail': 'https://via.placeholder.com/150',
        'download_url': 'https://example.com/download.mp4',
        'quality': '720p',
        'format': format_type,
        'uploader': 'YouTube Channel'
    })

@app.route('/api/tiktok')
def tiktok():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'title': 'TikTok Video',
        'video_url': 'https://example.com/video.mp4',
        'audio_url': 'https://example.com/audio.mp3',
        'thumbnail': 'https://via.placeholder.com/150',
        'author': '@username'
    })

@app.route('/api/instagram')
def instagram():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'title': 'Instagram Post',
        'items': [
            {'type': 'video', 'url': 'https://example.com/video.mp4', 'thumbnail': 'https://via.placeholder.com/150'}
        ]
    })

@app.route('/api/twitter')
def twitter():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'title': 'Twitter Video',
        'download_url': 'https://example.com/video.mp4',
        'thumbnail': 'https://via.placeholder.com/150'
    })

@app.route('/api/spotify')
def spotify():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query required'}), 400
    return jsonify({
        'success': True,
        'query': query,
        'results': [
            {
                'title': f'{query} - Result 1',
                'uploader': 'YouTube Music',
                'thumbnail': 'https://via.placeholder.com/150',
                'url': 'https://youtube.com/watch?v=example1'
            },
            {
                'title': f'{query} - Result 2',
                'uploader': 'YouTube Music',
                'thumbnail': 'https://via.placeholder.com/150',
                'url': 'https://youtube.com/watch?v=example2'
            }
        ]
    })

@app.route('/api/facebook')
def facebook():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'title': 'Facebook Video',
        'formats': [
            {'quality': 'HD', 'url': 'https://example.com/hd.mp4'},
            {'quality': 'SD', 'url': 'https://example.com/sd.mp4'}
        ]
    })

@app.route('/api/gdrive')
def gdrive():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'filename': 'file.zip',
        'download_url': 'https://example.com/file.zip'
    })

@app.route('/api/github')
def github():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'filename': 'file.txt',
        'download_url': 'https://raw.githubusercontent.com/example/file.txt'
    })

@app.route('/api/mediafire')
def mediafire():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'filename': 'file.zip',
        'size': '10 MB',
        'download_url': 'https://example.com/file.zip'
    })

@app.route('/api/pinterest')
def pinterest():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    return jsonify({
        'success': True,
        'title': 'Pinterest Image',
        'image_url': 'https://example.com/image.jpg',
        'thumbnail': 'https://example.com/image.jpg'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

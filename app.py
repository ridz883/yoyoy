from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_real_download_url(platform, url):
    """Get real download URL from external APIs"""
    try:
        if platform == 'tiktok':
            # Using TikWM API
            api_url = f"https://www.tikwm.com/api/?url={url}"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            if data.get('code') == 0:
                return {
                    'success': True,
                    'title': data['data'].get('title', 'TikTok Video'),
                    'video_url': data['data'].get('play', ''),
                    'audio_url': data['data'].get('music', ''),
                    'thumbnail': data['data'].get('cover', ''),
                    'author': data['data'].get('author', {}).get('nickname', '@user')
                }
        
        elif platform == 'youtube':
            # Using Y2Mate API (example)
            return {
                'success': True,
                'title': 'YouTube Video',
                'download_url': f'https://y2mate.com/analyze?url={url}',
                'thumbnail': 'https://via.placeholder.com/300x200',
                'quality': '720p'
            }
            
        elif platform == 'facebook':
            # Using FBDown API
            return {
                'success': True,
                'title': 'Facebook Video',
                'formats': [
                    {'quality': 'HD', 'url': f'https://fbdown.net/download?url={url}'},
                    {'quality': 'SD', 'url': f'https://fbdown.net/download?url={url}&quality=sd'}
                ]
            }
            
        elif platform == 'instagram':
            # Using InstaSave API
            return {
                'success': True,
                'title': 'Instagram Post',
                'items': [
                    {'type': 'video', 'url': f'https://instasave.website/api?url={url}'}
                ]
            }
            
        elif platform == 'twitter':
            # Using SSSTwitter API
            return {
                'success': True,
                'title': 'Twitter Video',
                'download_url': f'https://ssstwitter.com/result?url={url}'
            }
            
    except Exception as e:
        return {'error': str(e)}
    
    return {'error': 'Platform not supported'}

@app.route('/')
def home():
    return jsonify({
        'status': 'AllDownloader API by Ridzz',
        'version': '2.0',
        'message': 'API is working!'
    })

@app.route('/api/tiktok')
def tiktok():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    result = get_real_download_url('tiktok', url)
    return jsonify(result)

@app.route('/api/youtube')
def youtube():
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    result = get_real_download_url('youtube', url)
    result['format'] = format_type
    return jsonify(result)

@app.route('/api/facebook')
def facebook():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    result = get_real_download_url('facebook', url)
    return jsonify(result)

@app.route('/api/instagram')
def instagram():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    result = get_real_download_url('instagram', url)
    return jsonify(result)

@app.route('/api/twitter')
def twitter():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    result = get_real_download_url('twitter', url)
    return jsonify(result)

@app.route('/api/spotify')
def spotify():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    # Search YouTube
    return jsonify({
        'success': True,
        'query': query,
        'results': [
            {
                'title': f'{query} - Official Audio',
                'uploader': 'YouTube Music',
                'thumbnail': 'https://via.placeholder.com/150',
                'url': f'https://youtube.com/results?search_query={query.replace(" ", "+")}'
            }
        ]
    })

@app.route('/api/gdrive')
def gdrive():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    # Extract file ID
    file_id = None
    if '/d/' in url:
        file_id = url.split('/d/')[1].split('/')[0]
    elif 'id=' in url:
        file_id = url.split('id=')[1].split('&')[0]
    
    if file_id:
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return jsonify({
            'success': True,
            'filename': 'file',
            'download_url': direct_url
        })
    
    return jsonify({'error': 'Invalid Google Drive URL'})

@app.route('/api/github')
def github():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    # Convert to raw URL
    raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
    
    return jsonify({
        'success': True,
        'filename': raw_url.split('/')[-1],
        'download_url': raw_url
    })

@app.route('/api/mediafire')
def mediafire():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    return jsonify({
        'success': True,
        'filename': 'file',
        'download_url': url  # Will need scraping for real URL
    })

@app.route('/api/pinterest')
def pinterest():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    return jsonify({
        'success': True,
        'title': 'Pinterest Image',
        'image_url': url  # Will need scraping for real image URL
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

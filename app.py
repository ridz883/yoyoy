from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import requests
import re
import os
import json

app = Flask(__name__)
CORS(app)

# ============================================
# HELPERS
# ============================================

def cors_proxy(url, filename=None):
    """Proxy download dengan CORS headers"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        
        if response.status_code != 200:
            return None
            
        return {
            'url': url,
            'size': len(response.content),
            'content_type': response.headers.get('content-type', 'application/octet-stream')
        }
    except Exception as e:
        print(f"Proxy error: {e}")
        return None

# ============================================
# YOUTUBE SCRAPING (yt-dlp)
# ============================================

@app.route('/api/youtube', methods=['GET'])
def youtube_download():
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')  # mp4 atau mp3
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'best[ext=mp4]/best',
            })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Cari format terbaik
            if format_type == 'mp3':
                # Cari audio format
                formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                best_format = max(formats, key=lambda x: x.get('abr', 0)) if formats else None
            else:
                # Cari video format
                formats = [f for f in info['formats'] if f.get('vcodec') != 'none']
                best_format = max(formats, key=lambda x: x.get('height', 0)) if formats else None
            
            if not best_format:
                return jsonify({'error': 'No suitable format found'}), 404
            
            return jsonify({
                'success': True,
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': best_format['url'],
                'quality': f"{best_format.get('height', 'audio')}p" if format_type == 'mp4' else 'MP3',
                'format': format_type,
                'duration': info.get('duration'),
                'uploader': info.get('uploader', 'Unknown')
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# INSTAGRAM SCRAPING (yt-dlp - tanpa login)
# ============================================

@app.route('/api/instagram', methods=['GET'])
def instagram_download():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle single post atau carousel
            entries = info.get('entries', [info])
            items = []
            
            for entry in entries:
                media_url = entry.get('url') or entry.get('formats', [{}])[0].get('url')
                if media_url:
                    items.append({
                        'type': 'video' if entry.get('ext') == 'mp4' else 'image',
                        'url': media_url,
                        'thumbnail': entry.get('thumbnail', ''),
                        'title': entry.get('title', 'Instagram Media')
                    })
            
            return jsonify({
                'success': True,
                'items': items,
                'title': info.get('title', 'Instagram Post')
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# PINTEREST SCRAPING (requests + regex)
# ============================================

@app.route('/api/pinterest', methods=['GET'])
def pinterest_download():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        # Cari image URL di JSON data
        # Pinterest menyimpan data di <script id="__PWS_DATA__">
        json_match = re.search(r'<script[^>]*id="__PWS_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group(1))
            
            # Navigate through Pinterest's JSON structure
            pins = data.get('props', {}).get('initialReduxState', {}).get('pins', {})
            
            if pins:
                pin_id = list(pins.keys())[0]
                pin_data = pins[pin_id]
                
                # Cari image URL
                images = pin_data.get('images', {})
                orig_image = images.get('orig', {})
                image_url = orig_image.get('url', '')
                
                # Cari video URL (jika ada)
                videos = pin_data.get('videos', {})
                video_url = None
                if videos:
                    video_list = videos.get('video_list', {})
                    if video_list:
                        # Ambil kualitas tertinggi
                        best_video = max(video_list.values(), key=lambda x: x.get('width', 0))
                        video_url = best_video.get('url')
                
                return jsonify({
                    'success': True,
                    'title': pin_data.get('title', 'Pinterest Pin'),
                    'image_url': image_url,
                    'video_url': video_url,
                    'thumbnail': image_url,
                    'is_video': video_url is not None
                })
        
        # Fallback: regex langsung
        image_match = re.search(r'"url":"(https://i\.pinimg\.com/[^"]+)"', html)
        if image_match:
            return jsonify({
                'success': True,
                'title': 'Pinterest Image',
                'image_url': image_match.group(1).replace('\\/', '/'),
                'thumbnail': image_match.group(1).replace('\\/', '/')
            })
        
        return jsonify({'error': 'Could not extract media'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# SPOTIFY ALTERNATIVE (Search YouTube)
# ============================================

@app.route('/api/spotify', methods=['GET'])
def spotify_search():
    query = request.args.get('q')  # Judul lagu + artis
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        # Search di YouTube
        search_query = f"ytsearch5:{query}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_query, download=False)
            
            entries = search_results.get('entries', [])
            results = []
            
            for entry in entries:
                results.append({
                    'title': entry.get('title', 'Unknown'),
                    'uploader': entry.get('uploader', 'Unknown'),
                    'duration': entry.get('duration', 0),
                    'thumbnail': entry.get('thumbnail', ''),
                    'video_id': entry.get('id'),
                    'url': f"https://youtube.com/watch?v={entry.get('id')}"
                })
            
            return jsonify({
                'success': True,
                'query': query,
                'results': results
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# GOOGLE DRIVE (Direct Link)
# ============================================

@app.route('/api/gdrive', methods=['GET'])
def gdrive_download():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        # Extract file ID
        file_id = None
        
        # Pattern: /d/FILE_ID/
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            file_id = match.group(1)
        else:
            # Pattern: id=FILE_ID
            match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
            if match:
                file_id = match.group(1)
        
        if not file_id:
            return jsonify({'error': 'Invalid Google Drive URL'}), 400
        
        # Direct download URL
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Get file info
        session = requests.Session()
        response = session.get(direct_url, stream=True, allow_redirects=True)
        
        # Handle large files
        for key, value in session.cookies.items():
            if key.startswith('download_warning'):
                direct_url = f"{direct_url}&confirm={value}"
                break
        
        # Get filename dari header
        filename = 'download'
        if 'content-disposition' in response.headers:
            cd = response.headers['content-disposition']
            fname_match = re.search(r'filename="?([^"]+)"?', cd)
            if fname_match:
                filename = fname_match.group(1)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': direct_url,
            'file_id': file_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# GITHUB (Raw URL)
# ============================================

@app.route('/api/github', methods=['GET'])
def github_download():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        # Convert ke raw URL
        # https://github.com/user/repo/blob/main/file.txt
        # https://raw.githubusercontent.com/user/repo/main/file.txt
        
        raw_url = url.replace('github.com', 'raw.githubusercontent.com')
        raw_url = raw_url.replace('/blob/', '/')
        
        # Get file info
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        
        response = requests.head(raw_url, headers=headers, allow_redirects=True)
        
        filename = raw_url.split('/')[-1]
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': raw_url,
            'size': response.headers.get('content-length', 'Unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# TWITTER (API yang Anda berikan)
# ============================================

@app.route('/api/twitter', methods=['GET'])
def twitter_download():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        # Gunakan API yang Anda berikan
        api_url = f"https://api.deline.web.id/downloader/twitter?url={url}"
        
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('status') == 'success' or data.get('success'):
            return jsonify({
                'success': True,
                'title': data.get('result', {}).get('title', 'Twitter Video'),
                'thumbnail': data.get('result', {}).get('thumbnail', ''),
                'duration': data.get('result', {}).get('duration', ''),
                'formats': data.get('result', {}).get('formats', []),
                'download_url': data.get('result', {}).get('url', '')
            })
        else:
            return jsonify({'error': 'API returned error'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# TIKTOK, MEDIAFIRE, FACEBOOK (Proxy ke API asli)
# ============================================

@app.route('/api/tiktok', methods=['GET'])
def tiktok_proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        # Proxy ke API yang sudah ada
        apis = [
            f"https://tikwm.com/api/?url={url}",
            f"https://snapx.cab/api/tiktok?url={url}"
        ]
        
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=15)
                data = response.json()
                
                # Parse sesuai API
                if 'tikwm.com' in api_url:
                    if data.get('code') == 0:
                        return jsonify({
                            'success': True,
                            'title': data['data'].get('title', 'TikTok Video'),
                            'video_url': data['data'].get('play'),
                            'audio_url': data['data'].get('music'),
                            'thumbnail': data['data'].get('cover'),
                            'author': data['data'].get('author', {}).get('nickname')
                        })
                else:
                    if data.get('url'):
                        return jsonify({
                            'success': True,
                            'title': data.get('title', 'TikTok Video'),
                            'video_url': data.get('url'),
                            'audio_url': data.get('audioUrl'),
                            'thumbnail': data.get('thumbnail')
                        })
            except:
                continue
        
        return jsonify({'error': 'All TikTok APIs failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mediafire', methods=['GET'])
def mediafire_proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        api_url = f"https://api.danzy.web.id/api/download/mediafire?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        result = data.get('result') or data.get('data') or {}
        
        return jsonify({
            'success': True,
            'filename': result.get('filename') or result.get('name') or 'File',
            'size': result.get('size') or 'Unknown',
            'download_url': result.get('url') or result.get('link')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/facebook', methods=['GET'])
def facebook_proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        api_url = f"https://api.danzy.web.id/api/download/facebook?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        result = data.get('result') or data.get('data') or {}
        
        hd = result.get('hd') or result.get('url') or result.get('link')
        sd = result.get('sd')
        
        formats = []
        if hd:
            formats.append({'quality': 'HD', 'url': hd})
        if sd:
            formats.append({'quality': 'SD', 'url': sd})
        
        return jsonify({
            'success': True,
            'title': result.get('title') or 'Facebook Video',
            'thumbnail': result.get('thumbnail'),
            'formats': formats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/')
def home():
    return jsonify({
        'status': 'AllDownloader API by Ridzz',
        'version': '2.0',
        'endpoints': [
            '/api/youtube',
            '/api/instagram',
            '/api/pinterest',
            '/api/spotify',
            '/api/gdrive',
            '/api/github',
            '/api/twitter',
            '/api/tiktok',
            '/api/mediafire',
            '/api/facebook'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

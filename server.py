from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
from datetime import datetime
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# データ保存用のディレクトリ
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
TICKETS_FILE = os.path.join(DATA_DIR, 'tickets.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

# 初期化
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    if not os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'password': '0000'}, f)

init_files()

# ユーティリティ関数
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ルート
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/organizer')
def organizer():
    return render_template('organizer.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# API: ユーザー登録
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': 'ユーザー名が必要です'}), 400
    
    users = load_json(USERS_FILE)
    
    if username in users:
        user_id = users[username]['id']
    else:
        user_id = secrets.token_hex(16)
        users[username] = {
            'id': user_id,
            'created_at': datetime.now().isoformat()
        }
        save_json(USERS_FILE, users)
    
    return jsonify({'success': True, 'user_id': user_id, 'username': username})

# API: チケット購入
@app.route('/api/purchase', methods=['POST'])
def purchase():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    ticket_date = data.get('date')  # 日付を受け取る
    
    if not user_id or not username:
        return jsonify({'success': False, 'message': '無効なリクエスト'}), 400
    
    # 日付が指定されていない場合は今日の日付
    if not ticket_date:
        ticket_date = datetime.now().strftime('%Y-%m-%d')
    
    tickets = load_json(TICKETS_FILE)
    
    ticket_id = secrets.token_hex(16)
    ticket_data = {
        'id': ticket_id,
        'user_id': user_id,
        'username': username,
        'date': ticket_date,  # 指定された日付を使用
        'created_at': datetime.now().isoformat(),
        'used': False
    }
    
    tickets[ticket_id] = ticket_data
    save_json(TICKETS_FILE, tickets)
    
    return jsonify({'success': True, 'ticket': ticket_data})

# API: ユーザーのチケット一覧取得
@app.route('/api/tickets/<user_id>', methods=['GET'])
def get_tickets(user_id):
    tickets = load_json(TICKETS_FILE)
    user_tickets = [t for t in tickets.values() if t['user_id'] == user_id]
    return jsonify({'success': True, 'tickets': user_tickets})

# API: チケット検証
@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    qr_data = data.get('qr_data')
    
    if not qr_data:
        return jsonify({'success': False, 'valid': False, 'message': 'QRデータが無効です'})
    
    try:
        ticket_info = json.loads(qr_data)
        ticket_id = ticket_info.get('id')
        date = ticket_info.get('date')
        
        tickets = load_json(TICKETS_FILE)
        
        if ticket_id not in tickets:
            return jsonify({'success': True, 'valid': False, 'message': 'チケットが見つかりません'})
        
        ticket = tickets[ticket_id]
        
        # 日付とIDの照合
        if ticket['date'] != date or ticket['id'] != ticket_id:
            return jsonify({'success': True, 'valid': False, 'message': 'チケット情報が一致しません'})
        
        # 使用済みチェック
        if ticket.get('used'):
            return jsonify({'success': True, 'valid': False, 'message': '使用済みチケットです'})
        
        # チケットを使用済みにマーク
        tickets[ticket_id]['used'] = True
        tickets[ticket_id]['used_at'] = datetime.now().isoformat()
        save_json(TICKETS_FILE, tickets)
        
        return jsonify({
            'success': True, 
            'valid': True, 
            'message': 'チケットは有効です',
            'username': ticket['username']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'valid': False, 'message': f'エラー: {str(e)}'})

# API: 主催者認証
@app.route('/api/auth/organizer', methods=['POST'])
def auth_organizer():
    data = request.json
    password = data.get('password')
    
    config = load_json(CONFIG_FILE)
    
    if password == config['password']:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'パスワードが違います'})

# API: パスワード変更
@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    config = load_json(CONFIG_FILE)
    
    if old_password != config['password']:
        return jsonify({'success': False, 'message': '現在のパスワードが違います'})
    
    config['password'] = new_password
    save_json(CONFIG_FILE, config)
    
    return jsonify({'success': True})

# API: 全チケット一覧取得(主催者用)
@app.route('/api/admin/tickets', methods=['GET'])
def get_all_tickets():
    tickets = load_json(TICKETS_FILE)
    ticket_list = sorted(tickets.values(), key=lambda x: x['created_at'], reverse=True)
    return jsonify({'success': True, 'tickets': ticket_list})

# API: チケット削除(主催者用)
@app.route('/api/admin/delete-ticket/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    tickets = load_json(TICKETS_FILE)
    
    if ticket_id in tickets:
        del tickets[ticket_id]
        save_json(TICKETS_FILE, tickets)
        return jsonify({'success': True, 'message': 'チケットを削除しました'})
    else:
        return jsonify({'success': False, 'message': 'チケットが見つかりません'}), 404


if __name__ == '__main__':
    # HTTPS用の自己署名証明書を生成
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("証明書を生成中...")
        os.system(f'openssl req -x509 -newkey rsa:4096 -nodes -out {cert_file} -keyout {key_file} -days 365 -subj "/CN=localhost"')
    
    app.run(host='0.0.0.0', port=5000, ssl_context=(cert_file, key_file), debug=True)

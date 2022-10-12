from datetime import datetime
from flask_api import FlaskAPI
import random
import string
import config
import db
import crypto
import codecs

app = FlaskAPI(__name__)


@app.route('/')
def index():
    return {
        'response': 'OK'
    }


@app.route('/get_score/<token>/<telegram_id>')
def get_score(token, telegram_id):
    conn = db.get_connection(config.db_url)
    cur = conn.cursor()
    cur.execute(
        'SELECT quota from api WHERE token = %s;',
        (token,))
    quota = cur.fetchone()
    if quota:
        if quota[0] >= 1:
            cur.execute(
                'SELECT score from users WHERE user_id = %s;',
                (telegram_id,))
            score = cur.fetchone()
            if score:
                time_now = datetime.now()
                message = f'{telegram_id},{score[0]},{time_now}'
                signature = crypto.sign(message, crypto.load_key(config.api_ecdsa_private_key))
                cur.execute(
                    'UPDATE api SET quota = quota - 1 WHERE token = %s;',
                    (token,))
                cur.close()
                db.close_connection(conn)
                return {
                    'response': 'OK',
                    'telegram_id': telegram_id,
                    'score': score[0],
                    'time': time_now,
                    'message': message,
                    'signature': codecs.encode(signature[0], 'hex_codec').decode('ascii')
                }
            else:
                cur.close()
                db.close_connection(conn)
                return {
                    'response': 'User not found'
                }
        else:
            cur.close()
            db.close_connection(conn)
            return {
                'response': 'Quota exceeded'
            }
    else:
        cur.close()
        db.close_connection(conn)
        return {
            'response': 'Invalid token'
        }


@app.route('/get_quota/<token>')
def get_quota(token):
    conn = db.get_connection(config.db_url)
    cur = conn.cursor()
    cur.execute(
        'SELECT quota from api WHERE token = %s;',
        (token,))
    quota = cur.fetchone()
    cur.close()
    db.close_connection(conn)
    if quota:
        return {
            'response': 'OK',
            'token': token,
            'quota': quota[0]
        }
    else:
        return {
            'response': 'Invalid token'
        }


@app.route('/generate_token/<master_key>/<quota>')
def generate_token(master_key, quota):
    if master_key == config.api_master_key:
        try:
            quota_num = int(quota)
        except:
            quota_num = -1
        if quota_num > 0:
            token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
            conn = db.get_connection(config.db_url)
            conn.cursor().execute(
                'INSERT INTO api (token, quota) VALUES (%s, %s);',
                (token, quota))
            db.close_connection(conn)
            return {
                'response': 'OK',
                'token': token,
                'quota': quota
            }
        else:
            return {
                'response': 'Quota must be a positive integer'
            }
    else:
        return {
            'response': 'Wrong master key'
        }


@app.route('/add_quota/<master_key>/<token>/<quota>')
def add_quota(master_key, token, quota):
    if master_key == config.api_master_key:
        try:
            quota_num = int(quota)
        except:
            quota_num = 0
        if quota_num != 0:
            conn = db.get_connection(config.db_url)
            cur = conn.cursor()
            cur.execute(
                'UPDATE api SET quota = quota + %s WHERE token = %s RETURNING quota;',
                (quota, token))
            new_quota = cur.fetchone()
            cur.close()
            db.close_connection(conn)
            if new_quota:
                return {
                    'response': 'OK',
                    'token': token,
                    'quota': new_quota[0]
                }
            else:
                return {
                    'response': 'Invalid token'
                }
        else:
            return {
                'response': 'Quota must be a non-zero integer'
            }
    else:
        return {
            'response': 'Wrong master key'
        }


if __name__ == '__main__':
    app.run(debug=True)

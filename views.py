from flask import jsonify


def check():
    return jsonify({'status': 'OK'})
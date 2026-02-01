from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Konfigurasi Database (Ambil dari Environment Variable biar aman)
DB_HOST = os.environ.get("DB_HOST", "ep-sg-kamu.aws.neon.tech")
DB_NAME = os.environ.get("DB_NAME", "neondb")
DB_USER = os.environ.get("DB_USER", "neondb_owner")
DB_PASS = os.environ.get("DB_PASS", "npg_password_kamu")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        sslmode='require'
    )
    return conn

@app.route('/upload-csv', methods=['POST'])
def upload_data():
    try:
        # 1. Terima data JSON dari Google Sheet
        data = request.json['rows'] # Bentuknya list of list
        
        if not data:
            return jsonify({"status": "error", "message": "Data kosong"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # 2. Opsional: Kosongkan tabel dulu sebelum timpa baru
        # cur.execute("TRUNCATE TABLE nama_tabel_kamu")

        # 3. Masukkan data (Looping insert)
        # Query disesuaikan dengan jumlah kolom kamu
        sql = "INSERT INTO nama_tabel_kamu (kolom1, kolom2, kolom3) VALUES (%s, %s, %s)"
        
        # Eksekusi batch (lebih cepat)
        cur.executemany(sql, data)
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success", "message": f"{len(data)} baris berhasil masuk!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download-data', methods=['GET'])
def download_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM nama_tabel_kamu")
        rows = cur.fetchall()
        
        # Ambil header kolom
        colnames = [desc[0] for desc in cur.description]
        
        cur.close()
        conn.close()
        
        return jsonify({"headers": colnames, "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
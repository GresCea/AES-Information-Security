# kdc.py
import socket
import json
import secrets
import string
from config import KDC_IP, KDC_PORT
from utils import aes_encrypt

def generate_session_key():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(16))

def get_key(prompt_text):
    while True:
        key = input(prompt_text)
        if len(key) == 16:
            return key
        print("[!] Error: Master Key harus tepat 16 karakter (ASCII) untuk AES-128.")

def start_kdc():

    print("=== KDC (KEY DISTRIBUTION CENTER) ===")
    master_key_alice = get_key("Masukkan Master Key untuk Alice (16 karakter): ")
    master_key_bob = get_key("Masukkan Master Key untuk bob (16 karakter): ")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((KDC_IP, KDC_PORT))
    server.listen(1)
    print(f"\n[*] KDC Menunggu koneksi di {KDC_IP}:{KDC_PORT}")

    while True:
        conn, addr = server.accept()
        print(f"[*] Koneksi masuk dari {addr}")
        
        # Step 1: Menerima request dari Alice (IDA || IDB || N1)
        data = conn.recv(1024).decode('ascii')
        request = json.loads(data)
        ida = request['IDA']
        idb = request['IDB']
        n1 = request['N1']
        print(f"[*] Step 1: Menerima Request dari {ida} untuk ke {idb} dengan Nonce {n1}")
        
        # KDC Generate Session Key (Ks)
        Ks = generate_session_key()
        print(f"[*] KDC Generate Session Key (Ks): {Ks}")
        
        # Step 2: Membuat Ticket untuk Bob dan Mengenkripsi balasan ke Alice
        # Ticket Bob = E_Kb(Ks || IDA)
        ticket_bob_data = json.dumps({'Ks': Ks, 'IDA': ida})
        ticket_bob_enc = aes_encrypt(master_key_bob, ticket_bob_data)
        
        # Balasan ke Alice = E_Ka(Ks || IDB || N1 || Ticket_Bob)
        reply_alice_data = json.dumps({'Ks': Ks, 'IDB': idb, 'N1': n1, 'Ticket': ticket_bob_enc})
        reply_alice_enc = aes_encrypt(master_key_alice, reply_alice_data)
        
        print(f"[*] Step 2: Mengirim balasan ke {ida} (Ciphertext Hex): {reply_alice_enc[:30]}...")
        conn.send(reply_alice_enc.encode('ascii'))
        conn.close()

if __name__ == "__main__":
    start_kdc()
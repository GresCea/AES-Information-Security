# alice.py
import socket
import json
import random
import threading
from config import KDC_IP, KDC_PORT, BOB_IP, BOB_PORT, MASTER_KEY_ALICE
from utils import aes_encrypt, aes_decrypt

SESSION_KEY = None

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode('ascii')
            if data:
                plaintext = aes_decrypt(SESSION_KEY, data)
                print(f"\n[Bob]: {plaintext}\n[Anda]: ", end="")
        except:
            break

def start_alice():
    global SESSION_KEY
    
    # --- Step 1: Minta key ke KDC ---
    print("[*] Menghubungi KDC...")
    kdc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    kdc_sock.connect((KDC_IP, KDC_PORT))
    
    n1 = str(random.randint(1000, 9999))
    req = json.dumps({'IDA': 'Alice', 'IDB': 'Bob', 'N1': n1})
    kdc_sock.send(req.encode('ascii'))
    print(f"[*] Step 1: Request dikirim ke KDC (Nonce: {n1})")
    
    # --- Step 2: Terima dari KDC ---
    reply_enc = kdc_sock.recv(4096).decode('ascii')
    kdc_sock.close()
    
    reply_dec = aes_decrypt(MASTER_KEY_ALICE, reply_enc)
    kdc_data = json.loads(reply_dec)
    
    if kdc_data['N1'] != n1:
        print("[!] Nonce tidak cocok! Berhenti.")
        return
        
    SESSION_KEY = kdc_data['Ks']
    ticket_bob = kdc_data['Ticket']
    print(f"[*] Step 2: Berhasil mendekripsi balasan KDC. Session Key (Ks): {SESSION_KEY}")
    
    # --- Step 3: Hubungi Bob ---
    print(f"[*] Menghubungi Bob di {BOB_IP}:{BOB_PORT}...")
    bob_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bob_sock.connect((BOB_IP, BOB_PORT))
    
    bob_sock.send(ticket_bob.encode('ascii'))
    print("[*] Step 3: Ticket Bob dikirim.")
    
    # --- Step 4: Terima Nonce dari Bob ---
    n2_enc = bob_sock.recv(1024).decode('ascii')
    n2 = aes_decrypt(SESSION_KEY, n2_enc)
    print(f"[*] Step 4: Menerima Nonce N2 dari Bob: {n2}")
    
    # --- Step 5: Kirim balasan f(N2) ke Bob ---
    n2_minus_1 = str(int(n2) - 1)
    n2_minus_1_enc = aes_encrypt(SESSION_KEY, n2_minus_1)
    bob_sock.send(n2_minus_1_enc.encode('ascii'))
    print(f"[*] Step 5: Mengirim balasan N2-1 ke Bob: {n2_minus_1}")
    
    # --- Skenario Distribusi Selesai, Mulai Komunikasi 2 Arah ---
    print("\n--- DISTRIBUSI KUNCI SELESAI. MULAI CHAT (AES) ---")
    threading.Thread(target=receive_messages, args=(bob_sock,), daemon=True).start()
    
    while True:
        msg = input("[Anda]: ")
        msg_enc = aes_encrypt(SESSION_KEY, msg)
        # Menampilkan bentuk ciphertext Hex sesuai syarat no. 3
        print(f"    (Ciphertext dikirim: {msg_enc})")
        bob_sock.send(msg_enc.encode('ascii'))

if __name__ == "__main__":
    start_alice()
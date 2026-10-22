# bob.py
import socket
import json
import random
import threading
from config import BOB_IP, BOB_PORT
from utils import aes_encrypt, aes_decrypt

SESSION_KEY = None

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode('ascii')
            if data:
                plaintext = aes_decrypt(SESSION_KEY, data)
                print(f"\n[Alice]: {plaintext}\n[Anda]: ", end="")
        except:
            break

def start_bob():
    global SESSION_KEY

    print("=== BOB (SERVER) ===")
    master_key_bob = input("Masukkan Master Key untuk bob: ")
    if len(master_key_bob) > 16:
        print("[!] Info: Key dipotong menjadi 16 karakter otomatis.")
        master_key_bob = master_key_bob[:16]
    elif len(master_key_bob) < 16:
        print("[!] Info: Key kurang dari 16 karakter, di-padding otomatis.")
        master_key_bob = master_key_bob.ljust(16, '0')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((BOB_IP, BOB_PORT))
    server.listen(1)
    print(f"[*] Bob standby (Menunggu Alice di {BOB_IP}:{BOB_PORT})")
    
    conn, addr = server.accept()
    print(f"[*] Terhubung dengan Alice dari {addr}")
    
    # --- Step 3: Terima Ticket dari Alice ---
    ticket_enc = conn.recv(2048).decode('ascii')
    ticket_dec = aes_decrypt(master_key_bob, ticket_enc)
    ticket_data = json.loads(ticket_dec)
    
    SESSION_KEY = ticket_data['Ks']
    ida = ticket_data['IDA']
    print(f"[*] Step 3: Menerima & mendekripsi Ticket. Entitas: {ida}, Session Key: {SESSION_KEY}")
    
    # --- Step 4: Kirim Nonce (N2) ke Alice ---
    n2 = str(random.randint(1000, 9999))
    n2_enc = aes_encrypt(SESSION_KEY, n2)
    conn.send(n2_enc.encode('ascii'))
    print(f"[*] Step 4: Mengirim Nonce N2 ke Alice: {n2}")
    
    # --- Step 5: Terima balasan f(N2) dari Alice ---
    n2_reply_enc = conn.recv(1024).decode('ascii')
    n2_reply = aes_decrypt(SESSION_KEY, n2_reply_enc)
    print(f"[*] Step 5: Menerima balasan N2-1 dari Alice: {n2_reply}")
    
    if int(n2_reply) != int(n2) - 1:
        print("[!] Autentikasi Alice gagal!")
        return
    print("[*] Autentikasi Berhasil!")
    
    # --- Skenario Distribusi Selesai, Mulai Komunikasi 2 Arah ---
    print("\n--- DISTRIBUSI KUNCI SELESAI. MULAI CHAT (AES) ---")
    threading.Thread(target=receive_messages, args=(conn,), daemon=True).start()
    
    while True:
        msg = input("[Anda]: ")
        msg_enc = aes_encrypt(SESSION_KEY, msg)
        print(f"    (Ciphertext dikirim: {msg_enc})")
        conn.send(msg_enc.encode('ascii'))

if __name__ == "__main__":
    start_bob()
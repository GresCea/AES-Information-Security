# config.py

# Konfigurasi IP dan Port
KDC_IP = '127.0.0.1'    # Ganti dengan IP aktual KDC
KDC_PORT = 5000

ALICE_IP = '127.0.0.1'  # Ganti dengan IP aktual Alice
ALICE_PORT = 5001       # Port jika Alice bertindak sebagai server untuk komunikasi

BOB_IP = '127.0.0.1'    # Ganti dengan IP aktual Bob
BOB_PORT = 5002

# Master Keys (Dalam ASCII, panjang 16 karakter untuk AES-128)
# Disarankan diinput interaktif, tapi ini sebagai default.
MASTER_KEY_ALICE = "MasterKeyAlice12"
MASTER_KEY_BOB = "MasterKeyBob1234"
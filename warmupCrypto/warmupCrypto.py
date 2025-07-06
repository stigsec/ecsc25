def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

P1_bytes = b"hello world"
P2_bytes = b"did you ever hear the tragedy of darth plagueis the wise"

C1_bytes = bytes.fromhex("b99b4b044a5a40463d4e5d")
C2_bytes = bytes.fromhex("b59743485c1542092a545cbe34623b5ed349c241d9ea6aac70915229e777931467b5ac191e68baff0f824f8e2ca3f9af6a107b24196fcc4d")
C_flag_bytes = bytes.fromhex("b49d540b174f4c4a3d5b49b87b27335ac007c504dfb867ae6599503fff27940b6ab0a30f4767fffb4e8c4e9d64a7f3a27219696a130c")

keystream = xor_bytes(P2_bytes, C2_bytes)

decrypted_flag = xor_bytes(C_flag_bytes[:len(keystream)], keystream)

try:
    print(decrypted_flag.decode('utf-8')) #     ecsc25{crypto-means-cryptography-and-get-off-my-lawn}
except UnicodeDecodeError:
    print(decrypted_flag)

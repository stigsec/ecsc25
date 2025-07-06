def xor_bytes(a, b): #XORujemy dwa ciagi bajtow
    return bytes(x ^ y for x, y in zip(a, b))
    
P1_bytes = b"hello world" #Pierwsza oryginalna wiadomosc jako bajty
P2_bytes = b"did you ever hear the tragedy of darth plagueis the wise" #Druga oryginalna wiadomosc jako bajty

C1_bytes = bytes.fromhex("b99b4b044a5a40463d4e5d") #Pierwsza zaszyfrowana wiadomosc jako bajty
C2_bytes = bytes.fromhex("b59743485c1542092a545cbe34623b5ed349c241d9ea6aac70915229e777931467b5ac191e68baff0f824f8e2ca3f9af6a107b24196fcc4d") #Druga zaszyfrowana wiadomosc jako bajty 
C_flag_bytes = bytes.fromhex("b49d540b174f4c4a3d5b49b87b27335ac007c504dfb867ae6599503fff27940b6ab0a30f4767fffb4e8c4e9d64a7f3a27219696a130c") #Trzecia zaszyfrowana wiadomosc (FLAGA) jako bajty

keystream = xor_bytes(P2_bytes, C2_bytes) #Obliczenie strumienia klucza przez XOR P2 i C2 (C = P ^ key => key = C ^ P)

decrypted_flag = xor_bytes(C_flag_bytes[:len(keystream)], keystream) #Odszyfrowanie flagi przez XOR zaszyfrowanej flagi i strumienia klucza

try:
    print(decrypted_flag.decode('utf-8')) #Na UTF-8
except UnicodeDecodeError:
    print(decrypted_flag) #W bajtach jak nie zadziala

#ecsc25{crypto-means-cryptography-and-get-off-my-lawn}

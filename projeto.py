import random
import math
import hashlib

def miller_rabin(num_aleat, rounds):
    if num_aleat % 2 == 0:
        return False

    d = 0 
    r = num_aleat - 1
    while r == 0:
        d += 1
        r = r >> 1

    for _ in range(rounds):
        a = random.randrange(2, num_aleat - 1)
        x = pow(a, r, num_aleat)
        if x == 1 or x == num_aleat - 1:
            continue
        i = 1
        while i < d and x != num_aleat - 1:
            x = pow(x, 2, num_aleat)
            if x == 1:
                return False
            i += 1
        if x != num_aleat - 1:
            return False

    return True

def inverso_modular(e, n):
    a = 0
    b = n
    u = 1
    while e > 0:
        q = b // e
        e, a, b, u = b % e, u, e, a - q * u
    if b == 1:
        return a % n

def oaep(binary_m):
    #print(bin(binary_m))
    k0 = 24
    k1 = 57      # VER SE O K1 PODE SER TAO PEQUENO, JÁ QUE O DIGEST PODE SER ATÉ 64 BYTES
    tamanho_m_k1 = len(bin(binary_m)) - 2 + k1
    print(tamanho_m_k1)

    padded_m = binary_m << k1   # Padding de m com k1 bits 0

    encoded_p_m = str(padded_m).encode()
    r = random.getrandbits(k0)
    print(r)
    G = hashlib.blake2b(digest_size=int(tamanho_m_k1/8))     # Funcao Hash G
    G.update(str(bin(r))[2:].encode())
    print(G.hexdigest())
    G.update(str(bin(r))[2:].encode())
    print(G.hexdigest())
    G.update(str(bin(r))[2:].encode())
    print(G.hexdigest())
    while len(bin(int(G.hexdigest(), 16))) != tamanho_m_k1: # ENCONTRAR UM HASH QUE POSSA DEFINIR UM TAMANHO FIXO
        G.update(str(bin(r))[2:].encode())
    X = padded_m ^ int(G.hexdigest(), 16)

    print(bin(X))

    H = hashlib.blake2b(digest_size=int(k0/8))
    H.update(str(bin(padded_m))[2:].encode())
    while len(bin(int(H.hexdigest(), 16))) != k0:
        H.update(str(bin(padded_m))[2:].encode())
    Y = r ^ int(H.hexdigest(), 16)

    return X, Y

def reverse_oaep(X, Y):
    k0 = 20
    k1 = 57
    H = hashlib.blake2b(digest_size=int(k0/8))
    H.update(str(bin(X))[2:].encode())
    while len(bin(int(H.hexdigest(), 16))) != k0:
        print(len(bin(int(H.hexdigest(), 16))))
        H.update(str(bin(X))[2:].encode())
    r = Y ^ int(H.hexdigest(), 16)
    print(r)

def gera_chave(tamanho):
    n = 0
    while len(str(bin(n))) != 1024:
        cont = 0
        primos = []
        while cont < 2:
            num_aleat = random.getrandbits(int(tamanho/2))
            num_aleat |= (1 << int(tamanho/2) - 2 - 1) | 1
            if miller_rabin(num_aleat, 40) == True:
                primos.append(num_aleat)
                cont += 1
        n = primos[0] * primos[1]
        #print(len(str(bin(n))))

    phi = (primos[0] - 1) * (primos[1] - 1)
    
    e = 65537
    #e = random.randrange(2, phi)
    #while math.gcd(e, phi) != 1:
    #    e = random.randrange(2, phi)

    d = inverso_modular(e, n)
    chave_pk = [n, e]
    chave_sk = [n, d]
    return chave_pk, chave_sk

pk, sk = gera_chave(1024)
#print(pk, sk)

with open('mensagem.txt', 'r') as file:
    mensagem = file.read().replace('\n', '')
#print(mensagem)
encoded_m = mensagem.encode()
#print(encoded_m)
hashed_m = hashlib.sha3_224(encoded_m)
print(hashed_m.hexdigest())

binary_h_m = int.from_bytes(hashed_m.hexdigest().encode(), 'big')
#print(binary_h_m)
#print(binary_h_m.to_bytes((binary_h_m.bit_length() + 7) // 8, 'big').decode())
X, Y = oaep(binary_h_m)

#reverse_oaep(X, Y)
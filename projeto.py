import random
import math
import hashlib

# Função que determina se um número é provavelmente um primo ou se é composto
def miller_rabin(num_aleat, rounds):
    if num_aleat % 2 == 0:
        return False

    # Encontrar um valor d * 2**r tal que seja igual a n-1
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

#def inverso_modular(e, n):
#    a = 0
#    b = n
#    u = 1
#    while e > 0:
#        q = b // e
#        e, a, b, u = b % e, u, e, a - q * u
#    if b == 1:
#        return a % n

# Oráculo Randômico G do esquema OAEP
def hash_G(r):
    G = hashlib.sha3_384()
    G.update(str(bin(r))[2:].encode())
    return int(G.hexdigest(), 16)

# Oráculo Randômico H do esquema OAEP
def hash_H(padded_m):
    H = hashlib.sha3_224()
    H.update(str(bin(padded_m))[2:].encode())
    return int(H.hexdigest(), 16)
    
# Função que realiza o esquema de padding OAEP
def oaep(binary_m):
    k0 = 224
    k1 = 132

    # Realiza o padding de k1 bits na mensagem
    padded_m = binary_m << k1
    #print('padded: ', hex(padded_m))

    # Escolhe um número randômico de k0 bits
    r = random.getrandbits(k0)


    X = padded_m ^ hash_G(r)
    #print('r:', hex(r))

    Y = r ^ hash_H(X)

    # Retorna mensagem encriptografada de forma que não seja mais determinística
    return X, Y

# Função que reverte o esquema OAEP para receber a mensagem original
def reverse_oaep(X, Y):
    k1 = 132
    r = Y ^ hash_H(X)
    #print('r ver = ', hex(r))

    padded_m = X ^ hash_G(r)
    #print('padded_m ver = ', hex(padded_m))

    m = padded_m >> k1
    return hex(m)


# Função que gera chaves privada e pública a partir de determinado tamanho de bits
def gera_chave(tamanho):
    n = 0
    # São gerados novos primos até que seu produto tenha tamanho de bits igual a entrada desta função
    while len(str(bin(n))) - 2 != tamanho:
        cont = 0
        primos = []
        while cont < 2: 
            # São gerados dois primos que passem por 40 rodadas do teste de miller_rabin
            num_aleat = random.getrandbits(int(tamanho/2))
            num_aleat |= (1 << int(tamanho/2) - 2 - 1) | 1
            if miller_rabin(num_aleat, 40) == True:
                primos.append(num_aleat)
                cont += 1
        n = primos[0] * primos[1]

    # Determina a ordem de n e escolhe uma chave pública
    phi = (primos[0] - 1) * (primos[1] - 1)
    e = 65537
    #e = random.randrange(2, phi)
    #while math.gcd(e, phi) != 1:
    #    e = random.randrange(2, phi)

    # Constrói a chave privada a partir da pública e de phi
    d = pow(e, -1, phi)
    chave_pk = [n, e]
    chave_sk = [n, d]
    return chave_pk, chave_sk

pk, sk = gera_chave(1024)

with open('mensagem.txt', 'r') as file:
    mensagem = file.read().replace('\n', '')

# Codifica a mensagem e passa ela por uma função hash SHA-3
encoded_m = mensagem.encode()
hashed_m = hashlib.sha3_256(encoded_m)

# Realiza o esquema OAEP para tirar a propriedade determinística de RSA
X, Y = oaep(int(hashed_m.hexdigest(), 16))
#print(X, Y)
result_oaep = str(X) + str(Y)
print('Mensagem com OAEP:', result_oaep)

# Cria a assinatura usando a mensagem com padding e a chave privada
assinatura = pow(int(result_oaep), sk[1], sk[0])
print('Assinatura:', assinatura)
print('Chave publica [n, e]:', pk)

# Verifica a assinatura usando a chave pública
check_oaep = pow(assinatura, pk[1], pk[0])
check_oaep = str(check_oaep)

#print(int(check_oaep[0:len(str(X))]), int(check_oaep[len(str(X)):]))

# Reverte a mensagem com padding para a original
hashed_m_oaep = reverse_oaep(int(check_oaep[0:len(str(X))]), int(check_oaep[len(str(X)):]))

if hashed_m_oaep == hex(int(hashed_m.hexdigest(), 16)):
    print('Assinatura válida :)')
else:
    print('Sai daqui, seu bandido safado >:(')
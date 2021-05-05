import random
import math
import hashlib
import base64

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

    print('Primo p:\n', primos[0])
    print('Primo q:\n', primos[1], '\n')

    # Determina a ordem de n e escolhe uma chave pública
    phi = (primos[0] - 1) * (primos[1] - 1)
    e = 65537

    # Constrói a chave privada a partir da pública e de phi
    d = pow(e, -1, phi)
    chave_pk = [n, e]
    chave_sk = [n, d]
    return chave_pk, chave_sk

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
def oaep(m):
    # Tamanho n = 256 + 128 + 224
    # Tamanho hash(m) = 256
    k0 = 224
    k1 = 128

    # Realiza o padding de k1 bits na mensagem
    padded_m = m << k1

    # Escolhe um número randômico de k0 bits
    r = random.getrandbits(k0)
    X = padded_m ^ hash_G(r)
    Y = r ^ hash_H(X)

    # Retorna mensagem encriptografada de forma que não seja mais determinística
    return X, Y

# Função que reverte o esquema OAEP para receber a mensagem original
def reverse_oaep(X, Y):
    k1 = 128
    r = Y ^ hash_H(X)
    ##print('r ver = ', hex(r))

    padded_m = X ^ hash_G(r)
    ##print('padded_m ver = ', hex(padded_m))

    m = padded_m >> k1
    return hex(m)

def gera_assinatura(base64_dados_codificados, sk):

    hashed_m = hashlib.sha3_256(base64_dados_codificados)
    print('Hash da mensagem:\n', bin(int(hashed_m.hexdigest(), 16)), '\n')

    # Realiza o esquema OAEP para tirar a propriedade determinística de RSA
    X, Y = oaep(int(hashed_m.hexdigest(), 16))

    print('X:\n', bin(X))
    print('Y:\n', bin(Y), '\n')
    result_oaep = (X << (len(bin(Y)) - 2)) | Y
    print('X|Y:\n', bin(result_oaep), '\n')

    # Cria a assinatura usando a mensagem com padding e a chave privada
    return pow(result_oaep, sk[1], sk[0]), len(str(bin(X)))

def verifica_assinatura(base64_dados_codificados, assinatura, pk, tam_X):
    k0 = 224

    # Verifica a assinatura usando a chave pública
    check_oaep = pow(assinatura, pk[1], pk[0])
    #check_oaep = str(check_oaep)

    print('Recuperação do X|Y:\n', bin(check_oaep), '\n')

    # Reverte a mensagem com padding para a original
    hashed_m_oaep = reverse_oaep(int(bin(check_oaep)[2:tam_X], 2) , int(bin(check_oaep)[tam_X:], 2))
    m_hashed = hashlib.sha3_256(base64_dados_codificados)

    print('Valor a ser verificado:\n', bin(int(hashed_m_oaep, 16)))
    print('Hash da mensagem:\n',bin(int(m_hashed.hexdigest(), 16)))

    if hashed_m_oaep == hex(int(m_hashed.hexdigest(), 16)):
        print('\nAssinatura válida :)\n')
    else:
        print('\nSai daqui, seu bandido safado >:(\n')


print('\n-------- GERAÇÃO DE CHAVES --------\n')

pk, sk = gera_chave(1024)

print('Chave pública:\n', pk)
print('Chave privada:\n', sk, '\n')

print('\n-------- ASSINATURA --------\n')

print('Nome do arquivo: mensagem.txt\n')

with open('mensagem.txt', 'rb') as binary_file:
    dados_arquivo = binary_file.read()
    base64_dados_codificados = base64.b64encode(dados_arquivo)
print('Arquivo em base64:', base64_dados_codificados, '\n')

assinatura, tam_X = gera_assinatura(base64_dados_codificados, sk)

print('Assinatura:\n', bin(assinatura), '\n')

print('\n-------- VERIFICAÇÃO --------\n')

verifica_assinatura(base64_dados_codificados, assinatura, pk, tam_X)
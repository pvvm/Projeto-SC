import random
import math
import decimal

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
        x = a**r % num_aleat
        if x != 1 and x != num_aleat - 1:
        i = 1
        while i < d and x != num_aleat - 1:
            x = x**2 % num_aleat
            if x == 1:
                return False
            i += 1
        if x != num_aleat - 1:
            return False

    return True



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
                print(primos)
                cont += 1
            
        n = primos[0] * primos[1]

    print(len(str(bin(n)))) #checar sobre o tamanho do n

    phi = (primos[0] - 1) * (primos[1] - 1)
    
    e = 65537
    #e = random.randrange(2, phi)
    #while math.gcd(e, phi) != 1:
    #    e = random.randrange(2, phi)

    #d = 1
    #while True:
    #    if (d * e - 1) % phi == 0:
    #        break
    #    d += 1
    #d = decimal.Decimal(e**-1) % decimal.Decimal(phi)
    #for x in range(1, phi):
    #    if(((e % phi) * (x % phi)) % phi == 1):
    #        d = x
    #        break

    #print(phi,'\n', e, '\n', d)

gera_chave(1024)
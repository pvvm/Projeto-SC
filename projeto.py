import random

def miller_rabin(num_aleat, rounds):
    if num_aleat % 2 == 0:
        return False
    d = 0
    r = num_aleat - 1
    while (r & 1) == 0:
        d += 1
        r = r >> 1

    for _ in range(rounds):
        a = random.randrange(2, num_aleat - 1)
        x = a^d % num_aleat
        if x > 1 and x < (num_aleat - 1):
            for i in range(d - 1):
                if x == num_aleat-1:
                    break
                x = x^2 % num_aleat
                if x == 1:
                    return False
        else:
            return False

    return True



def gera_chave(tamanho):
    cont = 0
    primos = []
    while True and cont < 2:
        num_aleat = random.getrandbits(tamanho)
        num_aleat |= (1 << tamanho - 1) | 1
        if miller_rabin(num_aleat, 40) == True:
            primos.append(num_aleat)
            cont += 1
    return primos

primos = gera_chave(1024)
p = primos[0]
q = primos[1]


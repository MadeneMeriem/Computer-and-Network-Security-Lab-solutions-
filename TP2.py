def pgcd(a, b):
    while b:
        a, b = b, a % b
    return a

def chiffrer_affine(message, a, b):
    if pgcd(a, 26) != 1:
        print(f"ERREUR: a = {a} n'est pas inversible modulo 27")
        return None

    resultat = ""
    message = message.upper()

    for lettre in message:
        # conversion lettre -> nombre
        if lettre == ' ':
            M = 26  # espace = 26
        elif 'A' <= lettre <= 'Z':
            M = ord(lettre) - ord('A')
        else:
            resultat += lettre
            continue

        # chiffrement
        C = (a * M + b) % 27

        # reconversion nombre -> lettre
        if C == 26:
            lettre_chiffree = ' '
        else:
            lettre_chiffree = chr(C + ord('A'))

        resultat += lettre_chiffree

    return resultat

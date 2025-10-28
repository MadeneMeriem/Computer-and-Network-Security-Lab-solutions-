

def pgcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def euclide_etendu(a, m):
    if m == 0:
        return a, 1, 0
    
    gcd, x1, y1 = euclide_etendu(m, a % m)
    x = y1
    y = x1 - (a // m) * y1
    
    return gcd, x, y


def inverse_modulaire(a, m):
    gcd, x, y = euclide_etendu(a, m)
    
    if gcd != 1:
        return None  
    
    return (x % m + m) % m



def chiffrer_affine(message, a, b):
    if pgcd(a, 27) != 1:
        print(f"ERREUR: a = {a} n'est pas inversible modulo 27")
        return None

    resultat = ""
    message = message.upper()

    for lettre in message:
        
        if lettre == ' ':
            M = 26 
        elif 'A' <= lettre <= 'Z':
            M = ord(lettre) - ord('A')
        else:
            resultat += lettre
            continue

       
        C = (a * M + b) % 27

        
        if C == 26:
            lettre_chiffree = ' '
        else:
            lettre_chiffree = chr(C + ord('A'))

        resultat += lettre_chiffree

    return resultat


def dechiffrer_affine(message_chiffre, a, b):

    a_inv = inverse_modulaire(a, 27)
    
    if a_inv is None:
        print(f"\nERREUR: a = {a} n'est pas inversible modulo 27")
        return None
    
    resultat = ""
    message_chiffre = message_chiffre.upper()
    
    for lettre in message_chiffre:
        
        if lettre == ' ':
            C = 26
        elif 'A' <= lettre <= 'Z':
            C = ord(lettre) - ord('A')
        else:
            resultat += lettre
            continue


        M = (a_inv * (C - b)) % 27


        if M == 26:
            lettre_dechiffree = ' '
        else:
            lettre_dechiffree = chr(M + ord('A'))

        resultat += lettre_dechiffree
    
    return resultat



def main():
    print("="*60)
    print("         CHIFFREMENT AFFINE - Alphabet {A, B, ..., Z}")
    print("="*60)
    print("\nFormules:")
    print("  Chiffrement   : C = (a * M + b) mod 27")
    print("  Déchiffrement : M = a^(-1) * (C - b) mod 27")
    print("\nCondition: a doit être inversible modulo 27")
    print("           c'est-à-dire PGCD(a, 27) = 1")
    print("="*60)
    
    while True:
        print("\n" + "-"*60)
        print("MENU PRINCIPAL")
        print("-"*60)
        print("1. Chiffrer un message")
        print("2. Déchiffrer un message")
        print("3. Quitter")
        print("-"*60)
        
        choix = input("\nVotre choix (1, 2 ou 3): ")
        
        if choix == "3":
            print("\nAu revoir!")
            break
        
        if choix not in ["1", "2"]:
            print("\nChoix invalide! Veuillez choisir 1, 2 ou 3.")
            continue
        

        print("\n--- Entrez la clé (a, b) ---")
        try:
            a = int(input("Valeur de a: "))
            b = int(input("Valeur de b: "))
        except ValueError:
            print("\nERREUR: Veuillez entrer des nombres entiers!")
            continue
        

        if pgcd(a, 27) != 1:
            print(f"\nATTENTION: a = {a} n'est pas inversible modulo 27!")
            print(f"PGCD({a}, 27) = {pgcd(a, 27)}")
            print("Veuillez choisir un autre a.")
            continue
        

        message = input("\nEntrez le message: ")
        

        if choix == "1":
            print("\n--- CHIFFREMENT ---")
            resultat = chiffrer_affine(message, a, b)
            if resultat:
                print(f"\nClé utilisée: a = {a}, b = {b}")
                print(f"Message original  : {message}")
                print(f"Message chiffré   : {resultat}")
        
        elif choix == "2":
            print("\n--- DÉCHIFFREMENT ---")

            a_inv = inverse_modulaire(a, 27)
            resultat = dechiffrer_affine(message, a, b)
            if resultat:
                print(f"\nClé utilisée: a = {a}, b = {b}")
                print(f"Inverse de a modulo 27: a^(-1) = {a_inv}")
                print(f"Message chiffré   : {message}")
                print(f"Message déchiffré : {resultat}")



if __name__ == "__main__":
    main()
import random
print("Welkom bij de: StudioDeurbel Python Collection Vol.1!")
scriptkiezer = input("Kies hier je script: 1 (Nummer Woord), 2 (Dobbelsteen), 3 (Rekenmachine), 4 (peos-script) ")
if scriptkiezer == "1":
    print("Oké! Loading Nummer Woord...")
    nummer = int(input("Nummer: "))
    woord = input("Woord: ")
    starter = input("Klik op enter om te starten ")
    for _ in range(nummer):
        print(woord)
elif scriptkiezer == "2":
    print("Oké! Loading Dobbelsteen...")
    gooi = input("Klik op enter om te gooien ")
    print(random.choice(["1", "2", "3", "4", "5", "6"]))
elif scriptkiezer == "3":
    print("Oké! Loading Rekenmachine...")
    a = int(input("Cijfer 1: "))
    b = int(input("Cijfer 2: "))
    som = input("Keer, plus, min of delen door? ")
    startrek = input("Klik op enter voor antwoord ")
    if som == "keer":
        print("Het antwoord is:", a * b)
    elif som == "plus":
        print("Het antwoord is:", a + b)
    elif som == "min":
        print("Het antwoord is:", a - b)
    elif som == "delen door":
        print("Het antwoord is:", a/b)
    else:
        print("Ongeldige invoer")
elif scriptkiezer == "4":
    print("Oké! Loading peos-script...")
    peos = input("Wil je alle honden verwijderen? ")
    if peos == "ja":
        hondverw = input("Oké! Klik op enter om alle honden te verwijderen! ")
        print("Alle honden verwijderd!")
    elif peos == "nee":
        print("MAAR PEOS WIL VAN WEL, DUS ALLE HONDEN WORDEN VERWIJDERD!")
    else:
        print("Ongeldige invoer")
print("Dankjewel voor het gebruiken van de geëmuleerde omgeving van: StudioDeurbel Python Collection Vol.1!")
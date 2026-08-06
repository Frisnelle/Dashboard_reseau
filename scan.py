import subprocess
import re
import socket
import concurrent.futures
from stockage import sauvegarder_scan
from alerte import detecter_nouveaux_appareils


def detecter_sous_reseau():
    """
    Déduit automatiquement le sous-réseau local (ex: "192.168.100")
    à partir de l'IP réelle du PC, sans dépendre d'une valeur codée en dur.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Astuce classique : se "connecter" à une IP externe (aucune donnée
        # n'est réellement envoyée) juste pour lire l'IP locale utilisée.
        s.connect(("8.8.8.8", 80))
        ip_locale = s.getsockname()[0]
    finally:
        s.close()

    parties = ip_locale.split('.')
    return '.'.join(parties[:3])  # ex: "192.168.100"


def ping_sweep(sous_reseau=None):
    """
    Envoie un ping à toutes les IP du sous-réseau pour forcer
    les appareils actifs à répondre et peupler la table ARP de Windows.
    Ne nécessite pas de droits administrateur.
    """
    if sous_reseau is None:
        sous_reseau = detecter_sous_reseau()

    def ping_ip(i):
        ip = f"{sous_reseau}.{i}"
        subprocess.run(
            ['ping', '-n', '1', '-w', '300', ip],
            capture_output=True
        )

    # Pings en parallèle pour aller vite (sinon plusieurs minutes en séquentiel)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(ping_ip, range(1, 255))


def scanner_reseau(sous_reseau=None):
    """
    Lit la table ARP maintenue par Windows pour lister les appareils
    connus sur le réseau local Wifi (pas de scan actif bas niveau,
    pas de permissions spéciales requises).
    """
    if sous_reseau is None:
        sous_reseau = detecter_sous_reseau()

    resultat = subprocess.run(['arp', '-a'], capture_output=True, text=True, encoding='cp850')
    lignes = resultat.stdout.split('\n')

    appareils = []
    motif = re.compile(r'(\d+\.\d+\.\d+\.\d+)\s+([\w-]+)\s+(\w+)')

    for ligne in lignes:
        correspondance = motif.search(ligne)
        if correspondance:
            ip, mac, type_entree = correspondance.groups()

            # On garde uniquement le sous-réseau détecté, avec une vraie adresse MAC
            if (ip.startswith(sous_reseau + '.')
                    and not ip.endswith('.255')
                    and mac != '---'
                    and type_entree == 'dynamique'):
                appareils.append({
                    'ip': ip,
                    'mac': mac
                })

    return appareils


if __name__ == "__main__":
    sous_reseau = detecter_sous_reseau()
    print(f"Sous-réseau détecté : {sous_reseau}.0/24\n")

    print("Sondage du réseau en cours (quelques secondes)...\n")
    ping_sweep(sous_reseau)

    print("Lecture de la table ARP...\n")
    appareils_trouves = scanner_reseau(sous_reseau)

    # Détection AVANT de sauvegarder (sinon on compare le scan à lui-même)
    nouveaux = detecter_nouveaux_appareils(appareils_trouves)

    print(f"{len(appareils_trouves)} appareil(s) trouvé(s) :\n")
    for appareil in appareils_trouves:
        marqueur = " 🆕 NOUVEAU" if appareil in nouveaux else ""
        print(f"IP: {appareil['ip']:<15} MAC: {appareil['mac']}{marqueur}")

    if nouveaux:
        print(f"\n⚠️  {len(nouveaux)} appareil(s) jamais vu(s) avant !")

    sauvegarder_scan(appareils_trouves)
    print("\n✅ Scan sauvegardé dans historique.json")
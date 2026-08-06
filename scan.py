import subprocess
import re
import concurrent.futures


def ping_sweep(sous_reseau="192.168.100"):
    """
    Envoie un ping à toutes les IP du sous-réseau pour forcer
    les appareils actifs à répondre et peupler la table ARP de Windows.
    Ne nécessite pas de droits administrateur.
    """
    def ping_ip(i):
        ip = f"{sous_reseau}.{i}"
        subprocess.run(
            ['ping', '-n', '1', '-w', '300', ip],
            capture_output=True
        )

    # Pings en parallèle pour aller vite (sinon plusieurs minutes en séquentiel)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(ping_ip, range(1, 255))


def scanner_reseau():
    """
    Lit la table ARP maintenue par Windows pour lister les appareils
    connus sur le réseau local Wifi (pas de scan actif bas niveau,
    pas de permissions spéciales requises).
    """
    resultat = subprocess.run(['arp', '-a'], capture_output=True, text=True, encoding='cp850')
    lignes = resultat.stdout.split('\n')

    appareils = []
    motif = re.compile(r'(\d+\.\d+\.\d+\.\d+)\s+([\w-]+)\s+(\w+)')

    for ligne in lignes:
        correspondance = motif.search(ligne)
        if correspondance:
            ip, mac, type_entree = correspondance.groups()

            # On garde uniquement le réseau Wifi réel, avec une vraie adresse MAC
            if (ip.startswith('192.168.100.')
                    and not ip.endswith('.255')
                    and mac != '---'
                    and type_entree == 'dynamique'):
                appareils.append({
                    'ip': ip,
                    'mac': mac
                })

    return appareils


if __name__ == "__main__":
    print("Sondage du réseau en cours (quelques secondes)...\n")
    ping_sweep()

    print("Lecture de la table ARP...\n")
    appareils_trouves = scanner_reseau()

    print(f"{len(appareils_trouves)} appareil(s) trouvé(s) :\n")
    for appareil in appareils_trouves:
        print(f"IP: {appareil['ip']:<15} MAC: {appareil['mac']}")
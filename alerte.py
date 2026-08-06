from stockage import charger_historique


def detecter_nouveaux_appareils(scan_actuel):
    """
    Compare les appareils du scan actuel à TOUS les appareils déjà vus
    dans l'historique. Retourne la liste des appareils jamais vus avant.
    """
    historique = charger_historique()
    
    # On construit l'ensemble de toutes les adresses MAC déjà connues
    mac_connues = set()
    for scan in historique:
        for appareil in scan['appareils']:
            mac_connues.add(appareil['mac'])
    
    # On compare aux appareils du scan actuel
    nouveaux = []
    for appareil in scan_actuel:
        if appareil['mac'] not in mac_connues:
            nouveaux.append(appareil)
    
    return nouveaux
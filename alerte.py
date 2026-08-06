from datetime import datetime
from stockage import charger_historique

HEURE_DEBUT_INHABITUELLE = 0  # minuit
HEURE_FIN_INHABITUELLE = 6     # 6h du matin


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


def heure_est_inhabituelle(date_scan_iso=None):
    """
    Indique si l'horodatage donné tombe dans la plage horaire jugée inhabituelle
    (par défaut : minuit à 6h). Si aucune date n'est fournie, utilise l'heure actuelle.
    """
    dt = datetime.fromisoformat(date_scan_iso) if date_scan_iso else datetime.now()
    return HEURE_DEBUT_INHABITUELLE <= dt.hour < HEURE_FIN_INHABITUELLE


def detecter_connexions_suspectes(scan_actuel, date_scan_iso=None):
    """
    Une connexion est jugée "suspecte" si l'appareil est à la fois :
    - jamais vu avant (nouveau)
    - détecté pendant une plage horaire inhabituelle
    Retourne la liste des appareils suspects.
    """
    nouveaux = detecter_nouveaux_appareils(scan_actuel)
    
    if not heure_est_inhabituelle(date_scan_iso):
        return []
    
    return nouveaux
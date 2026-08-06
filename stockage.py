import json
import os
from datetime import datetime

FICHIER_HISTORIQUE = "historique.json"


def charger_historique():
    """Charge l'historique des scans depuis le fichier JSON. Retourne une liste vide si le fichier n'existe pas encore."""
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []
    
    with open(FICHIER_HISTORIQUE, 'r', encoding='utf-8') as f:
        return json.load(f)


def sauvegarder_scan(appareils):
    """Ajoute un nouveau scan (avec horodatage) à l'historique et sauvegarde le tout."""
    historique = charger_historique()
    
    nouveau_scan = {
        'date': datetime.now().isoformat(),
        'appareils': appareils
    }
    
    historique.append(nouveau_scan)
    
    with open(FICHIER_HISTORIQUE, 'w', encoding='utf-8') as f:
        json.dump(historique, f, indent=2, ensure_ascii=False)
    
    return nouveau_scan
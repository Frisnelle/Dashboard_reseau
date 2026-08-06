from flask import Flask, render_template, redirect, url_for
from stockage import charger_historique, sauvegarder_scan
from scan import ping_sweep, scanner_reseau
from alerte import heure_est_inhabituelle

app = Flask(__name__)


@app.route('/')
def index():
    historique = charger_historique()
    dernier_scan = historique[-1] if historique else None
    appareils = dernier_scan['appareils'] if dernier_scan else []
    date_scan = dernier_scan['date'] if dernier_scan else None

    # Un appareil est "nouveau" s'il n'apparaissait dans AUCUN scan précédent
    historique_precedent = historique[:-1] if len(historique) > 1 else []
    mac_connues = set()
    for scan in historique_precedent:
        for a in scan['appareils']:
            mac_connues.add(a['mac'])

    heure_suspecte = heure_est_inhabituelle(date_scan) if date_scan else False

    for appareil in appareils:
        appareil['nouveau'] = appareil['mac'] not in mac_connues
        # Suspect = nouveau ET détecté à une heure inhabituelle
        appareil['suspect'] = appareil['nouveau'] and heure_suspecte

    return render_template(
        'index.html',
        appareils=appareils,
        date_scan=date_scan,
        nb_appareils=len(appareils),
        nb_nouveaux=sum(1 for a in appareils if a['nouveau']),
        nb_suspects=sum(1 for a in appareils if a['suspect'])
    )


@app.route('/scan', methods=['POST'])
def lancer_scan():
    ping_sweep()
    appareils = scanner_reseau()
    sauvegarder_scan(appareils)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
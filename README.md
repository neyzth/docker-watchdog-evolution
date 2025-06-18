# docker-watchdog
Un outil Python destiné aux administrateurs système pour suivre et obtenir des statistiques
sur les conteneurs Docker en cours d'exécution.
## Modification apportée 
Extension 5 – Export automatique de rapports hebdomadaires (PDF ou HTML)

## Cron
0 8 * * 1 /usr/bin/python3 /chemin/vers/src/cron_export.py >> /var/log/rapport_watchdog.log 2>&1

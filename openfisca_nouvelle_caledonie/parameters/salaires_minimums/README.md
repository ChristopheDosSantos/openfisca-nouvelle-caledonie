# Paramètres SMG et SMAG - Nouvelle-Calédonie

## Description

Ce dossier contient les paramètres du Salaire Minimum Garanti (SMG) et du Salaire Minimum Agricole Garanti (SMAG) de la Nouvelle-Calédonie depuis 2018.

Les données sont extraites de la page officielle du gouvernement de la Nouvelle-Calédonie :
https://dtenc.gouv.nc/vos-droits-vos-obligations/remuneration/le-salaire-minimum-garanti

## Fichiers

### 1. `salaire_minimum_garanti.yml`
Salaire Minimum Garanti (SMG) - Taux horaire brut en F.CFP

- **Unité** : F.CFP (Francs CFP)
- **Format** : Taux horaire
- **Plage de dates** : 2018-10-01 à 2026-08-01

### 2. `salaire_minimum_garanti_mensuel.yml`
Salaire Minimum Garanti (SMG) - Rémunération mensuelle (169 heures)

- **Unité** : F.CFP (Francs CFP)
- **Format** : Salaire mensuel calculé sur 169 heures
- **Plage de dates** : 2018-10-01 à 2026-08-01

### 3. `salaire_minimum_agricole_garanti.yml`
Salaire Minimum Agricole Garanti (SMAG) - Taux horaire brut en F.CFP

- **Unité** : F.CFP (Francs CFP)
- **Format** : Taux horaire
- **Plage de dates** : 2018-10-01 à 2026-08-01

### 4. `salaire_minimum_agricole_garanti_mensuel.yml`
Salaire Minimum Agricole Garanti (SMAG) - Rémunération mensuelle (169 heures)

- **Unité** : F.CFP (Francs CFP)
- **Format** : Salaire mensuel calculé sur 169 heures
- **Plage de dates** : 2018-10-01 à 2026-08-01

## Versions historiques

| Date | SMG (€/h) | SMAG (€/h) | Texte législatif |
|------|-----------|-----------|------------------|
| 2026-08-01 | 1000.08 | 850.07 | Arrêté n AG-2026-DTEFP-0648 du 29-07-2026 (JONC n 11112 du 31-07-2026 - page 17334) |
| 2025-06-01 | 991.73 | 842.97 | Arrêté n 2025-837/GNC du 21-05-2025 (JONC n 10924 du 27-05-2025 - page 8362) |
| 2024-08-01 | 985.42 | 837.61 | Arrêté n 2024-1389/GNC du 17-07-2024 (JONC n 10778 du 25-07-2024 - page 14408) |
| 2023-03-01 | 976.52 | 830.06 | Arrêté n 2023-295/GNC du 15-02-2023 (JONC n 10530 du 23-02-2023 - page 3831) |
| 2023-02-01 | 971.37 | 825.68 | Arrêté n 2023-31/GNC du 18-01-2023 (JONC n 10513 du 26-01-2023 - page 743) |
| 2022-10-01 | 965.10 | 820.35 | Arrêté n 2022-2201/GNC du 21-09-2022 (JONC n 10449 du 30-09-2022 - page 17950) |
| 2022-07-01 | 955.64 | 812.31 | Arrêté n 2022-1513/GNC du 22-06-2022 (JONC n 10405 du 28-06-2022 - page 12426) |
| 2022-06-01 | 945.90 | 804.03 | Arrêté n 2022-1267/GNC du 18-05-2022 (JONC n 10389 du 26-05-2022 - page 11088) |
| 2022-05-01 | 937.46 | 796.86 | Arrêté n 2022-1063/GNC du 27-04-2022 (JONC n 10373 du 28-04-2022 - page 8819) |
| 2018-10-01 | 926.44 | 787.49 | Arrêté n 2018-2337/GNC du 25-09-2018 (JONC n 9615 du 27-09-2018 - page 14005) |

## Utilisation dans OpenFisca

Pour accéder aux paramètres depuis le code Python :

```python
from openfisca_nouvelle_caledonie import CountryTaxBenefitSystem

tbs = CountryTaxBenefitSystem()
salaires = tbs.parameters.salaires_minimums

# Taux horaire SMG
smg_horaire = salaires.salaire_minimum_garanti('2026-08-01')
print(f"SMG horaire: {smg_horaire} F.CFP")  # 1000.08 F.CFP

# Salaire mensuel SMG (169 heures)
smg_mensuel = salaires.salaire_minimum_garanti_mensuel('2026-08-01')
print(f"SMG mensuel: {smg_mensuel} F.CFP")  # 169014 F.CFP

# Taux horaire SMAG
smag_horaire = salaires.salaire_minimum_agricole_garanti('2026-08-01')
print(f"SMAG horaire: {smag_horaire} F.CFP")  # 850.07 F.CFP

# Salaire mensuel SMAG (169 heures)
smag_mensuel = salaires.salaire_minimum_agricole_garanti_mensuel('2026-08-01')
print(f"SMAG mensuel: {smag_mensuel} F.CFP")  # 143662 F.CFP
```

## Sources

- Page officielle : https://dtenc.gouv.nc/vos-droits-vos-obligations/remuneration/le-salaire-minimum-garanti
- Journal Officiel de la Nouvelle-Calédonie (JONC) : https://juridoc.gouv.nc/juridoc/jdwebe.nsf/Juristart

## Notes

- Les valeurs mensuelles sont calculées sur la base de 169 heures de travail
- Les taux indiqués sont les taux bruts en F.CFP
- Les données couvrent la période de 2018-10-01 à 2026-08-01
- Les arrêtés originaux contiennent les références complètes et la documentation juridique


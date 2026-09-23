# Restructuration : Centralisation des paramètres de salaires minimums

## 📋 Résumé

Le projet contenait une duplication de paramètres : les taux horaires du SMG et SMAG étaient définis à deux endroits différents :
- 🗂️ Dans `/contribution_insertion_handicap/obligation_emploi/`
- 🗂️ Potentiellement utilisables ailleurs

Cette restructuration centralise ces paramètres à la **racine de `parameters/`**, facilitant la maintenance et évitant la désynchronisation.

---

## ✅ Changements effectués

### 1️⃣ Création de la structure centralisée

**Nouveau dossier :** `parameters/salaires_minimums/`

```
parameters/
└── salaires_minimums/
    ├── index.yaml
    ├── salaire_minimum_garanti.yml
    └── salaire_minimum_agricole_garanti.yml
```

### 2️⃣ Suppression des doublons

Fichiers supprimés (qui causaient la duplication) :
- ❌ `parameters/contribution_insertion_handicap/obligation_emploi/taux_horaire_smg.yaml`
- ❌ `parameters/contribution_insertion_handicap/obligation_emploi/taux_horaire_smag.yaml`

### 3️⃣ Mise à jour des variables

#### Fichier : `variables/contribution_insertion_handicap/entreprise.py`
- **Fonction :** `contribution_avant_depenses_deductibles` (lignes 230-256)
- **Ancien code :**
  ```python
  params = parameters(period).contribution_insertion_handicap.obligation_emploi
  taux = where(est_smag, params.taux_horaire_smag, params.taux_horaire_smg)
  ```
- **Nouveau code :**
  ```python
  taux_smag = parameters(period).salaires_minimums.salaire_minimum_agricole_garanti
  taux_smg = parameters(period).salaires_minimums.salaire_minimum_garanti
  taux = where(est_smag, taux_smag, taux_smg)
  ```

#### Fichier : `variables/contribution_insertion_handicap/unite_contrat.py`
- **Fonction :** `unite_contrats_service` (lignes 63-75)
  - Ancien : `p.taux_horaire_smg`
  - Nouveau : `parameters(period).salaires_minimums.salaire_minimum_garanti`

- **Fonction :** `unite_contrat_disposition` (lignes 95-107)
  - Ancien : `p.taux_horaire_smg`
  - Nouveau : `parameters(period).salaires_minimums.salaire_minimum_garanti`

### 4️⃣ Paramètres centralisés disponibles

Accès aux paramètres via :

```python
# SMG - Salaire Minimum Garanti
parameters(period).salaires_minimums.salaire_minimum_garanti
# Valeur 2026-08-01 : 1000.08 F.CFP

# SMAG - Salaire Minimum Agricole Garanti  
parameters(period).salaires_minimums.salaire_minimum_agricole_garanti
# Valeur 2026-08-01 : 850.07 F.CFP
```

---

## 🎯 Avantages

| Critère | Avant | Après |
|---------|-------|-------|
| **Unicité** | Paramètres dupliqués ❌ | Source unique ✅ |
| **Scalabilité** | Difficile à étendre | Facile d'ajouter des usages |
| **Cohérence** | Risque de désync | Garantie de cohérence |
| **Maintenabilité** | Architecture floue | Architecture claire |
| **Performance** | Identique | Identique ✅ |

---

## 📊 Historique des valeurs

Tous les taux historiques sont préservés dans les fichiers centralisés :

```yaml
# Extrait : salaires_minimums/salaire_minimum_garanti.yml
values:
  2026-08-01: 1000.08
  2025-06-01: 991.73
  2024-08-01: 985.42
  2023-03-01: 976.52
  2023-02-01: 971.37
  # ... (historique complet conservé)
```

---

## 🧪 Tests

Les tests existants dans `tests/contribution_insertion_handicap/` sont **compatibles** avec cette restructuration :

- ✅ `entreprise.yaml` - Tous les calculs donnent les mêmes résultats
- ✅ `contrat.yaml` - Les unités de contrats sont calculées correctement
- ✅ Les valeurs attendues sont identiques

### Exemple de test validé :
```yaml
- name: Contribution H - effectif < 100 SMG
  period: 2026
  input:
    effectif_salarie: [50]
    regime_smag: [false]
  output:
    contribution_avant_depenses_deductibles: [400032.00]
    # Calculé comme : 1 * 400 * 1000.08 = 400032.00
    # où 1000.08 provient de salaires_minimums.salaire_minimum_garanti ✅
```

---

## 🔍 Vérification

Le système a été validé avec :

```bash
✓ Système de paramètres chargé avec succès
✓ SMG (2026-08-01): 1000.08
✓ SMAG (2026-08-01): 850.07
✓ Les anciens paramètres ont été supprimés
✓ Les variables sont correctement chargées
```

---

## 📝 Recommandations futures

Si d'autres règles de calcul nécessitent les salaires minimums, elles peuvent maintenant :

1. Accéder directement aux paramètres centralisés
2. Utiliser les mêmes chemins : `parameters(period).salaires_minimums.*`
3. Éviter la duplication

**Exemple pour une future variable :**
```python
def formula(individu, period, parameters):
    taux_smg = parameters(period).salaires_minimums.salaire_minimum_garanti
    # ... utiliser taux_smg directement
```

---

## 📎 Fichiers impactés

### ✅ Créés
- `parameters/salaires_minimums/index.yaml`
- `parameters/salaires_minimums/salaire_minimum_garanti.yml`
- `parameters/salaires_minimums/salaire_minimum_agricole_garanti.yml`

### 📝 Modifiés
- `variables/contribution_insertion_handicap/entreprise.py`
- `variables/contribution_insertion_handicap/unite_contrat.py`

### ❌ Supprimés
- `parameters/contribution_insertion_handicap/obligation_emploi/taux_horaire_smg.yaml`
- `parameters/contribution_insertion_handicap/obligation_emploi/taux_horaire_smag.yaml`

### 📚 Non affectés
- Tous les tests (compatibles avec la restructuration)
- Tous les autres calculs et paramètres

---

**Date de restructuration :** 2026-09-23  
**Statut :** ✅ Complété avec succès


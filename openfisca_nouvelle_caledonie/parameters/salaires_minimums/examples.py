"""
Exemple d'utilisation des paramètres SMG et SMAG dans OpenFisca

Ce module montre comment accéder et utiliser les paramètres
Salaire Minimum Garanti (SMG) et Salaire Minimum Agricole Garanti (SMAG)
dans une variable OpenFisca.
"""

# Exemple 1: Accès basique aux paramètres
# ================================================
def exemple_acces_basic():
    """Accès basique aux paramètres SMG et SMAG."""
    from openfisca_nouvelle_caledonie import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    salaires = tbs.parameters.salaires_minimums

    # Récupérer le SMG pour une date donnée
    smg_2026 = salaires.salaire_minimum_garanti('2026-08-01')
    print(f"SMG horaire 2026-08-01: {smg_2026} F.CFP")

    # Récupérer le SMAG pour une date donnée
    smag_2026 = salaires.salaire_minimum_agricole_garanti('2026-08-01')
    print(f"SMAG horaire 2026-08-01: {smag_2026} F.CFP")

    # Récupérer les valeurs mensuelles
    smg_mensuel = salaires.salaire_minimum_garanti_mensuel('2026-08-01')
    smag_mensuel = salaires.salaire_minimum_agricole_garanti_mensuel('2026-08-01')
    print(f"SMG mensuel 2026-08-01: {smg_mensuel} F.CFP")
    print(f"SMAG mensuel 2026-08-01: {smag_mensuel} F.CFP")


# Exemple 2: Utilisation dans une variable OpenFisca
# ================================================
def exemple_variable_openfisca():
    """
    Exemple de création d'une variable OpenFisca
    qui vérifie si un salaire respecte le SMG.
    """
    from openfisca_core.variables import Variable
    from openfisca_core.periods import MONTH
    from openfisca_nouvelle_caledonie.entities import Individu
    import numpy as np

    class respects_smg(Variable):
        """
        Indique si le salaire brut respecte le Salaire Minimum Garanti (SMG).

        Cette variable retourne True si le salaire brut mensuel est >= SMG,
        False sinon.
        """
        value_type = bool
        entity = Individu
        definition_period = MONTH
        label = "Salaire brut respecte le SMG"

        def formula(individu, period, parameters):
            salaire_brut = individu('salaire_brut', period)
            smg = parameters(period).salaires_minimums.salaire_minimum_garanti_mensuel
            return salaire_brut >= smg


# Exemple 3: Comparaison entre SMG et SMAG
# ================================================
def exemple_comparaison():
    """
    Exemple montrant la comparaison entre SMG et SMAG
    pour déterminer le salaire minimum applicable.
    """
    from openfisca_nouvelle_caledonie import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    salaires = tbs.parameters.salaires_minimums

    # Comparer SMG et SMAG
    smg = salaires.salaire_minimum_garanti('2026-08-01')
    smag = salaires.salaire_minimum_agricole_garanti('2026-08-01')

    print(f"SMG: {smg} F.CFP")
    print(f"SMAG: {smag} F.CFP")
    print(f"Différence: {smg - smag} F.CFP ({(smag/smg - 1)*100:.1f}%)")
    print(f"Salaire minimum le plus élevé: {'SMG' if smg >= smag else 'SMAG'}")


# Exemple 4: Historique des valeurs
# ================================================
def exemple_historique():
    """
    Exemple montrant comment accéder à l'historique
    des valeurs SMG et SMAG.
    """
    from openfisca_nouvelle_caledonie import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    salaires = tbs.parameters.salaires_minimums

    # Dates importantes
    dates = [
        '2018-10-01',
        '2020-01-01',
        '2022-05-01',
        '2024-08-01',
        '2026-08-01',
    ]

    print("Évolution historique du SMG et SMAG:")
    print("=" * 70)
    print(f"{'Date':<15} {'SMG (€/h)':<15} {'SMAG (€/h)':<15} {'Évolution SMG':<15}")
    print("-" * 70)

    previous_smg = None
    for date in dates:
        try:
            smg = salaires.salaire_minimum_garanti(date)
            smag = salaires.salaire_minimum_agricole_garanti(date)

            if previous_smg is not None:
                evolution = ((smg - previous_smg) / previous_smg) * 100
                evolution_str = f"{evolution:+.2f}%"
            else:
                evolution_str = "-"

            print(f"{date:<15} {smg:<15.2f} {smag:<15.2f} {evolution_str:<15}")
            previous_smg = smg
        except Exception:
            print(f"{date:<15} Données non disponibles")


# Exemple 5: Calcul de salaires horaires et mensuels
# ================================================
def exemple_calcul_salaires():
    """
    Exemple montrant comment calculer les salaires
    horaires et mensuels basés sur le SMG.
    """
    from openfisca_nouvelle_caledonie import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    salaires = tbs.parameters.salaires_minimums

    # Récupérer les valeurs SMG
    smg_horaire = salaires.salaire_minimum_garanti('2026-08-01')
    smg_mensuel = salaires.salaire_minimum_garanti_mensuel('2026-08-01')

    # Calculs
    print("Calculs basés sur le SMG 2026-08-01:")
    print(f"  Taux horaire: {smg_horaire} F.CFP")
    print(f"  Heures mensuelles: 169")
    print(f"  Salaire mensuel: {smg_mensuel} F.CFP")
    print()

    # Calculs pour différentes durées de travail
    heures = [20, 35, 40, 160, 169]
    print("Salaires selon la durée de travail:")
    print(f"{'Heures/mois':<15} {'Salaire (F.CFP)':<20}")
    print("-" * 35)

    for h in heures:
        salaire = smg_horaire * h
        print(f"{h:<15} {salaire:<20.0f}")


if __name__ == '__main__':
    print("=" * 70)
    print("EXEMPLES D'UTILISATION DES PARAMÈTRES SMG ET SMAG")
    print("=" * 70)

    print("\n1. ACCÈS BASIQUE AUX PARAMÈTRES")
    print("-" * 70)
    exemple_acces_basic()

    print("\n2. COMPARAISON SMG vs SMAG")
    print("-" * 70)
    exemple_comparaison()

    print("\n3. HISTORIQUE DES VALEURS")
    print("-" * 70)
    exemple_historique()

    print("\n4. CALCUL DE SALAIRES")
    print("-" * 70)
    exemple_calcul_salaires()

    print("\n" + "=" * 70)
    print("✓ Exemples terminés")
    print("=" * 70)


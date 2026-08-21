from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Entreprise
import numpy as np



class effectif_salarie(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Effectif salarié de l'entreprise"
    # C'est une variable d'INPUT : pas de formula, elle est fournie directement
    # (par l'utilisateur de l'API, ou par un autre calcul plus tard)


class soumis_obligation_emploi_handicapes(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise est soumise à l'obligation d'emploi de travailleurs handicapés"
    reference = "https://code.travail.gouv.fr/code-du-travail/L5212-1"

    def formula(entreprise, period, parameters):
        effectif = entreprise("effectif_salarie", period)
        seuil = (
            parameters(period)
            .contribution_insertion_handicap.obligation_emploi.seuil_effectif
        )
        return effectif > seuil


class nb_beneficiaires_devant_etre_employes(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Nombre de bénéficiaires que l'entreprise doit employer"

    def formula(entreprise, period, parameters):
        effectif = entreprise("effectif_salarie", period)
        params = parameters(period).contribution_insertion_handicap.obligation_emploi

        seuil = params.seuil_effectif
        taux = params.taux_beneficiaires
        minimum = params.minimum_fraction

        valeur = effectif * taux
        valeur_avec_minimum = where(
            (valeur >= minimum) & (valeur < 1),
            minimum,
            valeur // 1,
        )

        return where(effectif > seuil, valeur_avec_minimum, 0)

class somme_unites_beneficiaires(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des unités de bénéficiaires, arrondie à 2 décimales par défaut"

    def formula(entreprise, period):
        unites_individuelles = entreprise.members('unite_beneficiaire', period)
        total = entreprise.sum(unites_individuelles)

        # équivalent de .setScale(2, RoundingMode.DOWN) en Java
        return np.floor(total * 100) / 100

class somme_unites_contrats_services(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des unités des contrats SERVICES (calculée en amont, agrégée depuis Contrat)"

class somme_unites_contrats_disposition(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des unités des contrats DISPOSITION (calculée en amont, agrégée depuis Contrat)"


class total_general_unites_contrats(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Total des unités contrats, plafonné à la moitié des bénéficiaires dus"

    def formula(entreprise, period):
        services = entreprise('somme_unites_contrats_services', period)
        disposition = entreprise('somme_unites_contrats_disposition', period)
        nb_beneficiaires_dus = entreprise('nb_beneficiaires_devant_etre_employes', period)

        somme_totale = services + disposition
        moitie = np.floor(nb_beneficiaires_dus / 2 * 100) / 100

        return np.minimum(somme_totale, moitie)


class beneficiaires_manquants(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Beneficiaires manquants apres prise en compte des unites"

    def formula(entreprise, period):
        unites_beneficiaires = entreprise('somme_unites_beneficiaires', period)
        unites_contrats = entreprise('total_general_unites_contrats', period)
        nb_beneficiaires_dus = entreprise('nb_beneficiaires_devant_etre_employes', period)

        total_unites = unites_beneficiaires + unites_contrats
        manque = nb_beneficiaires_dus - total_unites
        manque_tronque = np.floor(manque * 100) / 100

        return np.maximum(manque_tronque, 0)


class exonere_contribution_insertion_handicap(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "L'entreprise est exonérée de la contribution (création d'entreprise ou "
        "effectif inférieur ou égal au seuil)"
    )
    # Variable d'INPUT : pas de formula — fournie directement par l'appelant.
    # Couvre les deux cas de la logique métier Java :
    #   - isReponseCreation() : entreprise nouvellement créée
    #   - isReponseSeuil()    : entreprise sous le seuil d'effectif


class regime_smag(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "L'entreprise relève du Salaire Minimum Agricole Garanti (SMAG) "
        "pour le calcul de la contribution"
    )
    # Variable d'INPUT : pas de formula.


class contribution_avant_depenses_deductibles(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Étape H — Contribution avant dépenses déductibles "
        "(bénéficiaires manquants × multiplicateur × taux horaire)"
    )

    def formula(entreprise, period, parameters):
        # --- Exonération (création d'entreprise ou effectif sous seuil) ---
        exonere = entreprise("exonere_contribution_insertion_handicap", period)

        # --- Multiplicateur selon effectif (lu depuis les paramètres) ---
        effectif = entreprise("effectif_salarie", period)
        mult = (
            parameters(period)
            .contribution_insertion_handicap.obligation_emploi.multiplicateur_contribution
        )
        multiplicateur = where(
            effectif < mult.seuil,
            mult.bas,
            mult.haut,
        )

        # --- Taux horaire (SMG ou SMAG) ---
        params = parameters(period).contribution_insertion_handicap.obligation_emploi
        est_smag = entreprise("regime_smag", period)
        taux = where(est_smag, params.taux_horaire_smag, params.taux_horaire_smg)

        # --- Montant brut, tronqué à 2 décimales (RoundingMode.DOWN) ---
        manquants = entreprise("beneficiaires_manquants", period)
        montant = np.floor(manquants * multiplicateur * taux * 100) / 100

        return where(exonere, 0.0, montant)


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


# ── Étape I : Doublement de la contribution ───────────────────────────────────

class a_employe_beneficiaires_annee_en_cours(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise a employé des bénéficiaires handicapés l'année en cours"
    # INPUT — correspond à emploisAnneeEnCours dans le domaine Java


class a_employe_beneficiaires_annees_precedentes(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise a employé des bénéficiaires handicapés lors d'années précédentes"
    # INPUT — correspond à emploisAnneesPrecedentes dans le domaine Java


class eligible_doublement_cotisation_beneficiaire(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Éligibilité au doublement de la cotisation côté bénéficiaires "
        "(vrai si aucun emploi ni cette année ni les années précédentes)"
    )

    def formula(entreprise, period):
        # Éligible seulement si l'entreprise n'a JAMAIS employé de bénéficiaires
        emplois_en_cours = entreprise("a_employe_beneficiaires_annee_en_cours", period)
        emplois_precedents = entreprise("a_employe_beneficiaires_annees_precedentes", period)
        return ~emplois_en_cours & ~emplois_precedents


class a_contracte_annee_en_cours(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "L'entreprise a conclu des contrats de sous-traitance ou de mise à disposition "
        "l'année en cours"
    )
    # INPUT — correspond à contratsAnneeEnCours dans le domaine Java


class a_contracte_annees_precedentes(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "L'entreprise a conclu des contrats de sous-traitance ou de mise à disposition "
        "lors d'années précédentes"
    )
    # INPUT — correspond à contratsAnneesPrecedentes dans le domaine Java


class eligible_doublement_cotisation_contrat(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Éligibilité au doublement de la cotisation côté contrats "
        "(vrai si aucun contrat ni cette année ni les années précédentes)"
    )

    def formula(entreprise, period):
        # Éligible seulement si l'entreprise n'a JAMAIS contracté
        contrats_en_cours = entreprise("a_contracte_annee_en_cours", period)
        contrats_precedents = entreprise("a_contracte_annees_precedentes", period)
        return ~contrats_en_cours & ~contrats_precedents


class eligible_doublement_cotisation(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Éligibilité globale au doublement de la cotisation "
        "(bénéficiaires ET contrats doivent être tous deux éligibles)"
    )

    def formula(entreprise, period):
        elig_benef = entreprise("eligible_doublement_cotisation_beneficiaire", period)
        elig_contrat = entreprise("eligible_doublement_cotisation_contrat", period)
        return elig_benef & elig_contrat


class montant_doublement_contribution(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Étape I — Montant du doublement de la contribution "
        "(contribution × 2, tronqué à l'entier inférieur ; 0 si non éligible)"
    )

    def formula(entreprise, period):
        eligible = entreprise("eligible_doublement_cotisation", period)
        contribution = entreprise("contribution_avant_depenses_deductibles", period)

        # × 2 puis RoundingMode.DOWN vers l'entier (setScale(0, DOWN) en Java)
        montant = np.floor(contribution * 2)

        return where(eligible, montant, 0.0)


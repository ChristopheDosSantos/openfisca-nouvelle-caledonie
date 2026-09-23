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
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-1"
    documentation = """
    Détermine si l'entreprise est soumise à l'obligation d'emploi de travailleurs handicapés.
    L'obligation s'applique à tout employeur occupant plus de 20 salariés.
    """

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
    reference = [
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-3",
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-8",
    ]
    documentation = """
    Calcule le nombre théorique de bénéficiaires que l'entreprise doit employer,
    basé sur le pourcentage défini de l'effectif total, avec application d'un minimum
    pour les calculs entre 0,5 et 1.
    """

    def formula(entreprise, period, parameters):
        effectif = entreprise("effectif_salarie", period)
        params = parameters(period).contribution_insertion_handicap.obligation_emploi

        seuil = params.seuil_effectif
        taux = params.taux_beneficiaires
        minimum = params.minimum_fraction

        # Calcul théorique du nombre de bénéficiaires à employer
        nombre_theorique = effectif * taux

        # Application du minimum : si compris entre [minimum, 1[, retenir minimum
        # Sinon, arrondir à l'entier inférieur
        nombre_ajuste = where(
            (nombre_theorique >= minimum) & (nombre_theorique < 1),
            minimum,
            nombre_theorique // 1,
        )

        # Appliquer le seuil d'effectif : 0 si entreprise sous le seuil
        return where(effectif > seuil, nombre_ajuste, 0)

class somme_unites_beneficiaires(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des unités de bénéficiaires, arrondie à 2 décimales par défaut"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-8"
    documentation = """
    Agrège les unités individuelles de bénéficiaires au niveau de l'entreprise,
    selon le mode de calcul défini à l'article Lp. 473-8 (1 unité pour présence ≥ 6 mois et ≥ mi-temps,
    ou au prorata des heures pour les travailleurs temporaires).
    """

    def formula(entreprise, period):
        unites_individuelles = entreprise.members("unite_beneficiaire", period)
        unites_f64 = unites_individuelles.astype(np.float64)
        # Somme d'abord, puis floor à 2 décimales comme en Java (setScale(2, RoundingMode.DOWN))
        total = entreprise.sum(unites_f64)
        return np.floor(total * 100) / 100

class somme_unites_contrats_services(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des unités des contrats SERVICES"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-9"
    documentation = """
    Agrège les unités générées par les contrats de prestations de services passés
    avec des structures d'emploi adapté, conformément aux dispositions de l'article Lp. 473-9.
    """

    def formula(entreprise, period):
        unites_services = entreprise.members("unite_contrats_service", period)
        # Les unités sont déjà tronquées à 2 décimales au niveau individuel.
        # On somme en centièmes pour reproduire la logique BigDecimal (évite
        # les effets de précision float qui peuvent transformer 0.01 + 0.02 en 0.02 après floor).
        total_centiemes = entreprise.sum(np.rint(unites_services * 100))
        return total_centiemes / 100

class somme_unites_contrats_disposition(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des unités des contrats DISPOSITION"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-9"
    documentation = """
    Agrège les unités générées par les contrats de mise à disposition (fournitures de sous-traitance)
    passés avec des structures d'emploi adapté, conformément aux dispositions de l'article Lp. 473-9.
    """

    def formula(entreprise, period):
        unites_disposition = entreprise.members("unite_contrat_disposition", period)
        total_centiemes = entreprise.sum(np.rint(unites_disposition * 100))
        return total_centiemes / 100


class total_general_unites_contrats(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Total des unités contrats, plafonné à la moitié des bénéficiaires dus"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-9"
    documentation = """
    Somme des unités de contrats (services et mise à disposition), plafonné à la moitié
    du nombre de bénéficiaires que l'entreprise devait employer, selon l'article Lp. 473-9.
    """

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
    reference = [
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-10",
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-11",
    ]
    documentation = """
    Calcule le nombre de bénéficiaires non satisfaits après déduction des unités
    provenant des emplois directs et des contrats de services ou mise à disposition.
    Cette valeur constitue la base de calcul de la contribution annuelle.
    """

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
    reference = [
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-1",
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-4",
    ]
    documentation = """
    Indique si l'entreprise bénéficie d'une exonération de contribution. Deux cas d'application :
    1. Entreprise créée avec délai de mise en conformité (article Lp. 473-4)
    2. Entreprise dont l'effectif est inférieur ou égal au seuil (article Lp. 473-1)
    """
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
    reference = [
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-10",
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-11",
    ]
    documentation = """
    Calcule la contribution annuelle de base au fonds pour l'insertion professionnelle,
    selon la formule : bénéficiaires manquants × multiplicateur × taux horaire (SMG ou SMAG).
    Cette contribution est versée pour chaque bénéficiaire de l'obligation que l'entreprise
    n'a pas employé.
    """

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


# ── Étape J : Dépenses déductibles ───────────────────────────────────────────

class a_depenses_annee_en_cours(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise a engagé des dépenses déductibles l'année en cours"
    # INPUT — correspond à isDepensesAnneeEnCours() dans le domaine Java


class somme_depenses_ttc(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Somme des montants TTC des dépenses déductibles déclarées"

    def formula(entreprise, period):
        depenses_individuelles = entreprise.members("depense_handicap", period)
        depenses_f64 = depenses_individuelles.astype(np.float64)
        total = entreprise.sum(depenses_f64)
        return np.floor(total * 100) / 100


class montant_depenses_deductibles(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Étape J — Montant des dépenses déductibles "
        "(plafonné à la contribution applicable, tronqué à l'entier)"
    )

    def formula(entreprise, period):
        a_depenses = entreprise("a_depenses_annee_en_cours", period)

        # Somme TTC tronquée à l'entier inférieur (setScale(0, DOWN) en Java)
        somme = np.floor(entreprise("somme_depenses_ttc", period))

        # Plafond : doublement si applicable, sinon contribution de base
        doublement = entreprise("montant_doublement_contribution", period)
        contribution = entreprise("contribution_avant_depenses_deductibles", period)
        plafond = where(doublement == 0, contribution, doublement)

        deductible = np.minimum(somme, plafond)

        return where(a_depenses, deductible, 0.0)


# ── Étape K : Contribution finale ────────────────────────────────────────────

class montant_contribution(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Étape K — Contribution finale "
        "(base − dépenses déductibles, tronquée à l'entier inférieur)"
    )
    reference = [
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-10",
        "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-11",
    ]
    documentation = """
    Contribution finalement due au fonds pour l'insertion professionnelle des personnes
    en situation de handicap, après déduction des dépenses engagées pour l'emploi
    ou l'insertion de ces travailleurs.
    """

    def formula(entreprise, period):
        doublement = entreprise("montant_doublement_contribution", period)
        contribution = entreprise("contribution_avant_depenses_deductibles", period)
        depenses = entreprise("montant_depenses_deductibles", period)

        # Même logique de sélection de la base que pour le plafond des dépenses
        base = where(doublement == 0, contribution, doublement)

        # Soustraction puis RoundingMode.DOWN vers l'entier (setScale(0, DOWN))
        return np.floor(base - depenses)


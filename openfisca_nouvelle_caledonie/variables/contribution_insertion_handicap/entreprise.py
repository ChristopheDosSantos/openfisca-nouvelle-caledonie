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
from openfisca_core.variables import Variable
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import YEAR
from openfisca_nouvelle_caledonie.entities import Individu
import numpy as np

#  ------ Bénéficiaires Handicapés ------

class TypeQualiteBeneficiaire(Enum):
    beneficiaire_a = "Choix A - CDI/CDD/intérim ≥ 6 mois et ≥ mi-temps"
    beneficiaire_b = "Choix B - intérim < 6 mois, au prorata des heures"


class qualite_beneficiaire(Variable):
    value_type = Enum
    possible_values = TypeQualiteBeneficiaire
    # Valeur technique: si la qualite n'est pas renseignée, l'unité vaut 0
    # car nb_heures_travaillees est 0 par défaut pour le choix B.
    default_value = TypeQualiteBeneficiaire.beneficiaire_b
    entity = Individu
    definition_period = YEAR
    label = "Choix A ou B du formulaire de déclaration pour ce bénéficiaire"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-8"
    documentation = """
    Détermine le mode de calcul de l'unité comptabilisée au titre de l'obligation d'emploi :
    - Choix A : CDI/CDD/intérim d'au moins 6 mois et au moins mi-temps → 1 unité
    - Choix B : intérim de moins de 6 mois ou autres → au prorata des heures travaillées
    """


class nb_heures_travaillees(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Nombre d'heures travaillées (saisi uniquement si choix B)"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-8"
    documentation = """
    Nombre d'heures travaillées par le bénéficiaire au cours de l'année.
    Utilisé uniquement pour le choix B (travail temporaire), pour le calcul au prorata
    du nombre d'unités comptabilisé au titre de l'obligation d'emploi.
    """

class unite_beneficiaire(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Unité comptabilisée au titre de l'obligation d'emploi, avant arrondi global"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-8"
    documentation = """
    Calcule l'unité comptabilisée pour chaque bénéficiaire selon le choix retenu :
    - Choix A (CDI/CDD/intérim ≥ 6 mois et ≥ mi-temps) : 1 unité
    - Choix B (autre) : nombre d'heures travaillées / nombre d'heures de référence annuel
    """

    def formula(individu, period, parameters):
        qualite = individu('qualite_beneficiaire', period)
        nb_heures = individu('nb_heures_travaillees', period)
        Qualite = qualite.possible_values

        heures_reference = (
            parameters(period)
            .contribution_insertion_handicap.obligation_emploi.heures_reference
        )

        return np.select(
            [qualite == Qualite.beneficiaire_a, qualite == Qualite.beneficiaire_b],
            [1.0, nb_heures / heures_reference],
            default=0.0
        )

# Variables liées aux contrats déplacées dans `unite_contrat.py`.

# ------ Dépenses déductibles ------

class depense_handicap(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Montant TTC d'une dépense déductible engagée pour l'emploi ou l'insertion de travailleurs handicapés"
    # INPUT : cette variable est fournie directement par l'utilisateur ou un calcul externes

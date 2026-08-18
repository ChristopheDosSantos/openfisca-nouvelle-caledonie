from openfisca_core.variables import Variable
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import YEAR
from openfisca_nouvelle_caledonie.entities import Individu
import numpy as np


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


class nb_heures_travaillees(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Nombre d'heures travaillées (saisi uniquement si choix B)"

class unite_beneficiaire(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Unité comptabilisée au titre de l'obligation d'emploi, avant arrondi global"

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


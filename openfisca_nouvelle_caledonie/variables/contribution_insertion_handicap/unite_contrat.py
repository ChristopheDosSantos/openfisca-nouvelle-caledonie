# variables/contrat/unite_contrat.py
import numpy as np
from openfisca_core.variables import Variable
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import YEAR
from openfisca_nouvelle_caledonie.entities import Contrat


class TypeContratCIH(Enum):
    services = "Contrat de type SERVICES"
    disposition = "Contrat de mise à disposition (DISPOSITION)"


class type_contrat(Variable):
    value_type = Enum
    possible_values = TypeContratCIH
    default_value = TypeContratCIH.services
    entity = Contrat
    definition_period = YEAR
    label = "Type du contrat"


class prix_ht_fourniture(Variable):
    value_type = float
    entity = Contrat
    definition_period = YEAR
    label = "Prix HT de la fourniture au titre du contrat"


class cout_matiere_premiere(Variable):
    value_type = float
    entity = Contrat
    definition_period = YEAR
    label = "Coût des matières premières associé au contrat"


class unite_contrat(Variable):
    value_type = float
    entity = Contrat
    definition_period = YEAR
    label = "Unités générées par ce contrat"

    def formula(contrat, period, parameters):
        prix = contrat('prix_ht_fourniture', period)
        cout_matiere = contrat('cout_matiere_premiere', period)

        p = parameters(period).contribution_insertion_handicap.obligation_emploi
        base = prix - cout_matiere

        # le diviseur pourrait différer entre SERVICES et DISPOSITION un jour,
        # donc on le sort en paramètre plutôt qu'en constante en dur
        return np.floor(base / (p.diviseur_unite_contrat * p.taux_horaire_smg) * 100) / 100
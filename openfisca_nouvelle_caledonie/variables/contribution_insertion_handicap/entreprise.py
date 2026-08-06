from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Entreprise


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
        effectif = entreprise('effectif_salarie', period)
        return effectif > 20
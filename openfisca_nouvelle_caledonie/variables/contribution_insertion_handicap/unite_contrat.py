# variables/contrat/unite_contrat.py
import numpy as np
from openfisca_core.variables import Variable
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import YEAR
from openfisca_nouvelle_caledonie.entities import Individu


class TypeContratCIH(Enum):
    services = "Contrat de type SERVICES"
    disposition = "Contrat de mise à disposition (DISPOSITION)"


class type_contrat(Variable):
    value_type = Enum
    possible_values = TypeContratCIH
    default_value = TypeContratCIH.services
    entity = Individu
    definition_period = YEAR
    label = "Type du contrat"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-9"
    documentation = """
    Détermine le type de contrat passé avec une structure d'emploi adapté :
    - SERVICES : contrat de prestations de services ou de fournitures
    - DISPOSITION : contrat de mise à disposition (sous-traitance)
    
    Les deux modes permettent à l'employeur de s'acquitter partiellement de son obligation
    d'emploi, proportionnellement au volume de travail fourni à ces structures.
    """


class prix_ht_fourniture(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Prix HT de la fourniture au titre du contrat"


class cout_matiere_premiere(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Coût des matières premières associé au contrat"


class unite_contrats_service(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Unités générées par un contrat de type SERVICES"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-9"
    documentation = """
    Calcule le nombre d'unités au titre de l'obligation d'emploi généré par un contrat
    de prestations de services avec une structure d'emploi adapté.
    
    Formule : (Prix HT - Coût matières premières) / (diviseur × taux horaire SMG),
    tronqué à 2 décimales.
    
    L'acquittement partiel est proportionnel au volume de travail fourni, conformément
    à l'article Lp. 473-9.
    """

    def formula(individu, period, parameters):
        type_ctr = individu("type_contrat", period)
        types = type_ctr.possible_values
        prix = individu("prix_ht_fourniture", period)
        cout_matiere = individu("cout_matiere_premiere", period)

        p = parameters(period).contribution_insertion_handicap.obligation_emploi
        base = prix - cout_matiere
        unites = np.floor(
            base / (p.diviseur_unite_contrat_services * p.taux_horaire_smg) * 100,
        ) / 100

        return np.where(type_ctr == types.services, unites, 0.0)


class unite_contrat_disposition(Variable):
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Unités générées par un contrat de type DISPOSITION"
    reference = "https://juridoc.gouv.nc/juridoc/jdtextes.nsf/(web-All)/7388DD772A16E5544B25755E007A9AF0/$File/Loi-du-pays_2009-1_du_07-01-2009.pdf#Art.%20Lp.%20473-9"
    documentation = """
    Calcule le nombre d'unités au titre de l'obligation d'emploi généré par un contrat
    de mise à disposition (sous-traitance) avec une structure d'emploi adapté.
    
    Formule : (Prix HT - Coût matières premières) / (diviseur × taux horaire SMG),
    tronqué à 2 décimales.
    
    L'acquittement partiel est proportionnel au volume de travail fourni, conformément
    à l'article Lp. 473-9.
    """

    def formula(individu, period, parameters):
        type_ctr = individu("type_contrat", period)
        types = type_ctr.possible_values
        prix = individu("prix_ht_fourniture", period)
        cout_matiere = individu("cout_matiere_premiere", period)

        p = parameters(period).contribution_insertion_handicap.obligation_emploi
        base = prix - cout_matiere
        unites = np.floor(
            base / (p.diviseur_unite_contrat_disposition * p.taux_horaire_smg) * 100,
        ) / 100

        return np.where(type_ctr == types.disposition, unites, 0.0)


# La variable de compatibilite `unite_contrat` est supprimee volontairement.

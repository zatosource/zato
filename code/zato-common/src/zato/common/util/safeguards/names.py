# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex.detectors import get_registry

# Zato
from zato.common.typing_ import strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Type aliases - a choice is what select widgets consume, a grouped choice keeps one land's detectors together.
choice_tuple        = tuple[str, str]
choice_list         = list[choice_tuple]
choice_group        = tuple[str, choice_list]
grouped_choice_list = list[choice_group]
choice_dict         = dict[str, choice_list]

# ################################################################################################################################
# ################################################################################################################################

# The land whose detectors are not tied to any single country - it always sorts first.
Land_International = 'intl'

# Full names of the lands whose detectors the underlying library ships.
Land_Names:'strstrdict' = {
    'at':   'Austria',
    'be':   'Belgium',
    'bg':   'Bulgaria',
    'cz':   'Czech Republic',
    'de':   'Germany',
    'dk':   'Denmark',
    'ee':   'Estonia',
    'es':   'Spain',
    'fi':   'Finland',
    'fr':   'France',
    'gr':   'Greece',
    'hr':   'Croatia',
    'hu':   'Hungary',
    'ie':   'Ireland',
    'intl': 'International',
    'it':   'Italy',
    'lt':   'Lithuania',
    'nl':   'Netherlands',
    'pl':   'Poland',
    'pt':   'Portugal',
    'ro':   'Romania',
    'se':   'Sweden',
    'si':   'Slovenia',
    'sk':   'Slovakia',
    'us':   'United States',
}

# Full labels of every detector the underlying library ships, keyed by detector name.
Detector_Labels:'strstrdict' = {

    # Austria
    'at_vnr': 'Social insurance number (VNR)',

    # Belgium
    'be_bis':               'BIS number',
    'be_eid':               'eID card number',
    'be_nn':                'National number',
    'be_ogm_vcs_delimited': 'Structured payment reference (OGM/VCS)',
    'be_phone':             'Phone number',
    'be_vat':               'VAT number',

    # Bulgaria
    'bg_egn': 'Personal number (EGN)',
    'bg_pnf': 'Foreigner personal number (PNF)',

    # Czech Republic
    'cz_dic': 'Tax identifier (DIC)',
    'cz_rc':  'Birth number',

    # Germany
    'de_idnr':  'Tax identifier (IdNr)',
    'de_phone': 'Phone number',
    'de_svnr':  'Social insurance number (SVNR)',
    'de_vat':   'VAT number',

    # Denmark
    'dk_cpr': 'Personal number (CPR)',
    'dk_cvr': 'Business number (CVR)',

    # Estonia
    'ee_ik': 'Personal code (Isikukood)',

    # Spain
    'es_ccc':                  'Bank account code (CCC)',
    'es_cif':                  'Company tax code (CIF)',
    'es_dni':                  'Identity number (DNI)',
    'es_matricula':            'Vehicle registration plate',
    'es_nie':                  'Foreigner identity number (NIE)',
    'es_nss':                  'Social security number (NSS)',
    'es_passport':             'Passport number',
    'es_phone':                'Phone number',
    'es_referencia_catastral': 'Cadastral reference',

    # Finland
    'fi_hetu':    'Personal identity code (HETU)',
    'fi_ytunnus': 'Business ID (Y-tunnus)',

    # France
    'fr_cni':   'Identity card number (CNI)',
    'fr_nif':   'Tax identifier (NIF)',
    'fr_nir':   'Social security number (NIR)',
    'fr_phone': 'Phone number',
    'fr_siren': 'Business number (SIREN)',
    'fr_siret': 'Establishment number (SIRET)',
    'fr_tva':   'VAT number (TVA)',

    # Greece
    'gr_amka': 'Social security number (AMKA)',

    # Croatia
    'hr_oib': 'Personal identification number (OIB)',

    # Hungary
    'hu_anum': 'Tax number (ANUM)',

    # Ireland
    'ie_pps': 'Personal public service number (PPS)',

    # International
    'intl_bic':         'Bank identifier code (BIC)',
    'intl_credit_card': 'Credit card number',
    'intl_email':       'Email address',
    'intl_eu_vat':      'EU VAT number',
    'intl_iban':        'Bank account number (IBAN)',
    'intl_ipv4':        'IPv4 address',
    'intl_ipv6':        'IPv6 address',
    'intl_mac':         'MAC address',
    'intl_phone_e164':  'Phone number (E.164)',

    # Italy
    'it_codice_fiscale': 'Tax code (Codice fiscale)',
    'it_partita_iva':    'VAT number (Partita IVA)',
    'it_phone':          'Phone number',

    # Lithuania
    'lt_asmens': 'Personal code (Asmens kodas)',

    # Netherlands
    'nl_bsn':      'Citizen service number (BSN)',
    'nl_btw':      'VAT number (BTW)',
    'nl_passport': 'Passport number',
    'nl_phone':    'Phone number',

    # Poland
    'pl_nip':   'Tax identifier (NIP)',
    'pl_pesel': 'Personal number (PESEL)',
    'pl_regon': 'Business number (REGON)',

    # Portugal
    'pt_cc':       'Citizen card number',
    'pt_nif':      'Tax number (NIF)',
    'pt_niss':     'Social security number (NISS)',
    'pt_passport': 'Passport number',
    'pt_phone':    'Phone number',

    # Romania
    'ro_cf':  'Tax code (CF)',
    'ro_cnp': 'Personal numeric code (CNP)',

    # Sweden
    'se_orgnr':        'Business number (Organisationsnummer)',
    'se_personnummer': 'Personal number (Personnummer)',

    # Slovenia
    'si_emso':    'Personal number (EMSO)',
    'si_maticna': 'Business registration number (Maticna)',

    # Slovakia
    'sk_rc': 'Birth number',

    # United States
    'us_atin':     'Adoption taxpayer number (ATIN)',
    'us_dea':      'DEA registration number',
    'us_ein':      'Employer identification number (EIN)',
    'us_itin':     'Individual taxpayer number (ITIN)',
    'us_mbi':      'Medicare beneficiary identifier (MBI)',
    'us_npi':      'National provider identifier (NPI)',
    'us_passport': 'Passport number',
    'us_phone':    'Phone number',
    'us_ptin':     'Preparer taxpayer number (PTIN)',
    'us_rtn':      'Bank routing number (RTN)',
    'us_ssn':      'Social Security number',
}

# ################################################################################################################################
# ################################################################################################################################

def _choice_label(item:'choice_tuple') -> 'str':
    """ Returns the display label of a choice pair, for use as a sort key.
    """
    out = item[1]
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_land_choices() -> 'choice_list':
    """ Returns (code, full name) pairs for every land with at least one registered detector.
    International always comes first, the rest sorts by full name.
    """
    registry = get_registry()

    # Collect each land that has at least one detector registered ..
    lands:'strset' = set()

    for detector in registry.values():
        lands.add(detector.region)

    # .. build the country choices, keeping International aside for now ..
    countries:'choice_list' = []

    for land in lands:
        if land == Land_International:
            continue
        countries.append((land, Land_Names[land]))

    countries.sort(key=_choice_label)

    # .. and International leads the list.
    out:'choice_list' = [(Land_International, Land_Names[Land_International])]
    out.extend(countries)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_detector_choices() -> 'grouped_choice_list':
    """ Returns detector choices grouped per land, each group being (land full name, [(detector name, label), ...]),
    in the same land order as get_land_choices, with detectors sorted by label within each group.
    """
    registry = get_registry()

    # Group the detectors under their lands ..
    by_land:'choice_dict' = {}

    for detector in registry.values():
        label = Detector_Labels[detector.name]

        if group := by_land.get(detector.region):
            group.append((detector.name, label))
        else:
            by_land[detector.region] = [(detector.name, label)]

    # .. and emit the groups in land order, each sorted by label.
    land_choices = get_land_choices()

    out:'grouped_choice_list' = []

    for land, land_name in land_choices:
        group = by_land[land]
        group.sort(key=_choice_label)
        out.append((land_name, group))

    return out

# ################################################################################################################################
# ################################################################################################################################

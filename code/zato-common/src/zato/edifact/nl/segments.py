# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The segment definitions of the Dutch Medeur EDIFACT dialect, as specified by Nictiz in
# "Specificatie berichten 3i-project, versie 3.BSN" - the segments shared by the MEDLAB,
# MEDVRI, MEDRAD and MEDSPE messages exchanged over ZorgMail and its peers.

from __future__ import annotations

# Zato
from zato.edifact.base import EDIComponent, EDIComposite, EDIElement, EDISegment, Usage

# ################################################################################################################################
# ################################################################################################################################

class Address(EDIComposite):
    """ Adres - a Dutch postal address as a composite data element.
    """
    street          = EDIComponent[str](position=1, usage=Usage.CONDITIONAL, format='an..30')
    building_number = EDIComponent[str](position=2, usage=Usage.CONDITIONAL, format='an..8')
    po_box          = EDIComponent[str](position=3, usage=Usage.CONDITIONAL, format='n..8')
    city            = EDIComponent[str](position=4, usage=Usage.REQUIRED, format='a..20')
    postcode        = EDIComponent[str](position=5, usage=Usage.OPTIONAL, format='an..9')
    province        = EDIComponent[str](position=6, usage=Usage.OPTIONAL, format='a..20')
    country         = EDIComponent[str](position=7, usage=Usage.OPTIONAL, format='a..20')

# ################################################################################################################################
# ################################################################################################################################

class DateOfBirth(EDIComposite):
    """ Geboortedatum - a full date with a four-digit year.
    """
    year  = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='n4')
    month = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='n2')
    day   = EDIComponent[str](position=3, usage=Usage.REQUIRED, format='n2')

# ################################################################################################################################
# ################################################################################################################################

class Date(EDIComposite):
    """ Datum - a date with a two-digit year.
    """
    year  = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='n2')
    month = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='n2')
    day   = EDIComponent[str](position=3, usage=Usage.REQUIRED, format='n2')

# ################################################################################################################################
# ################################################################################################################################

class Time(EDIComposite):
    """ Tijd - hour and minute.
    """
    hour   = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='n2')
    minute = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='n2')

# ################################################################################################################################
# ################################################################################################################################

class PatientName(EDIComposite):
    """ Patientnaam - the patient's name with married and maiden components.
    """
    married_name          = EDIComponent[str](position=1, usage=Usage.CONDITIONAL, format='a..30')
    married_name_prefix   = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='a..8')
    maiden_name           = EDIComponent[str](position=3, usage=Usage.CONDITIONAL, format='a..30')
    maiden_name_prefix    = EDIComponent[str](position=4, usage=Usage.OPTIONAL, format='a..8')
    first_name            = EDIComponent[str](position=5, usage=Usage.OPTIONAL, format='a..12')
    initials              = EDIComponent[str](position=6, usage=Usage.OPTIONAL, format='a..8')

# ################################################################################################################################
# ################################################################################################################################

class DoctorName(EDIComposite):
    """ Artsnaam - a doctor's name.
    """
    last_name = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='a..30')
    prefix    = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='a..8')
    initials  = EDIComponent[str](position=3, usage=Usage.OPTIONAL, format='a..8')
    titles    = EDIComponent[str](position=4, usage=Usage.OPTIONAL, format='a..10')

# ################################################################################################################################
# ################################################################################################################################

class ZKH(EDISegment):
    """ Ziekenhuisgegevens - the sending hospital or institution.
    """
    _segment_tag = 'ZKH'

    institution_name = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a..70')
    address          = EDIElement[Address](position=2, usage=Usage.OPTIONAL, composite='Address')
    phone            = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='an..20')
    hospital_code    = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='n3')

# ################################################################################################################################
# ################################################################################################################################

class PID(EDISegment):
    """ Persoonsgegevens patient - the patient's personal details.
    """
    _segment_tag = 'PID'

    date_of_birth      = EDIElement[DateOfBirth](position=1, usage=Usage.REQUIRED, composite='DateOfBirth')
    sex                = EDIElement[str](position=2, usage=Usage.REQUIRED, format='a1')
    patient_name       = EDIElement[PatientName](position=3, usage=Usage.REQUIRED, composite='PatientName')
    sender_reference   = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='an..12')
    receiver_reference = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='an..12')

# ################################################################################################################################
# ################################################################################################################################

class PAD(EDISegment):
    """ Adresgegevens patient - the patient's address.
    """
    _segment_tag = 'PAD'

    address = EDIElement[Address](position=1, usage=Usage.REQUIRED, composite='Address')
    phone   = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class GGA(EDISegment):
    """ Gegevens afzender - the sender of a free-format message.
    """
    _segment_tag = 'GGA'

    person_name      = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a..40')
    department       = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='an..70')
    institution_name = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='a..70')
    address          = EDIElement[Address](position=4, usage=Usage.OPTIONAL, composite='Address')
    phone            = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class GGO(EDISegment):
    """ Gegevens ontvanger - the recipient of a free-format message.
    """
    _segment_tag = 'GGO'

    person_name      = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a..40')
    department       = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='an..70')
    institution_name = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='a..70')
    address          = EDIElement[Address](position=4, usage=Usage.OPTIONAL, composite='Address')
    phone            = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class DET(EDISegment):
    """ Datum/tijdstip - the date and time of an event, e.g. specimen collection or message creation.
    """
    _segment_tag = 'DET'

    date = EDIElement[Date](position=1, usage=Usage.REQUIRED, composite='Date')
    time = EDIElement[Time](position=2, usage=Usage.OPTIONAL, composite='Time')

# ################################################################################################################################
# ################################################################################################################################

class TXT(EDISegment):
    """ Vrije tekst - one line of free text.
    """
    _segment_tag = 'TXT'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class ART(EDISegment):
    """ Artsgegevens - the addressed or requesting doctor.
    """
    _segment_tag = 'ART'

    doctor_type = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a1')
    doctor_code = EDIElement[str](position=2, usage=Usage.REQUIRED, format='n6')
    doctor_name = EDIElement[DoctorName](position=3, usage=Usage.REQUIRED, composite='DoctorName')
    address     = EDIElement[Address](position=4, usage=Usage.OPTIONAL, composite='Address')
    phone       = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class AFD(EDISegment):
    """ Gegevens afdeling - the department, e.g. the laboratory or radiology unit.
    """
    _segment_tag = 'AFD'

    department = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')
    phone      = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class ARA(EDISegment):
    """ Artsen afdeling - a doctor of the reporting department.
    """
    _segment_tag = 'ARA'

    person_name = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..40')
    phone       = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class KOP(EDISegment):
    """ Kopie rapport van/naar arts - copy recipients of a report.
    """
    _segment_tag = 'KOP'

    copy_indicator = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a3..4')
    person_name_1  = EDIElement[str](position=2, usage=Usage.REQUIRED, format='a..40')
    person_name_2  = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='a..40')
    person_name_3  = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='a..40')
    person_name_4  = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='a..40')
    person_name_5  = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='a..40')

# ################################################################################################################################
# ################################################################################################################################

class BLG(EDISegment):
    """ Bloedgroep patient - the patient's blood group.
    """
    _segment_tag = 'BLG'

    blood_group = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..20')

# ################################################################################################################################
# ################################################################################################################################

class IDE(EDISegment):
    """ Identificatie materiaal/aanvraag - identification of a specimen or request.
    """
    _segment_tag = 'IDE'

    complete_code         = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a1')
    identification_number = EDIElement[str](position=2, usage=Usage.REQUIRED, format='an..9')
    material_type         = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='an..12')
    material_volume       = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='an..8')

# ################################################################################################################################
# ################################################################################################################################

class OPM(EDISegment):
    """ Opmerking materiaal/aanvraag - a remark about a specimen or request.
    """
    _segment_tag = 'OPM'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class SEC(EDISegment):
    """ Sectiegegevens - the name of a laboratory section, e.g. HAEMATOLOGIE.
    """
    _segment_tag = 'SEC'

    section_name = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..30')

# ################################################################################################################################
# ################################################################################################################################

class BEP(EDISegment):
    """ Gegevens laboratoriumbepaling - one laboratory determination and its result.
    """
    _segment_tag = 'BEP'

    determination_type   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='n1')
    determination        = EDIElement[str](position=2, usage=Usage.REQUIRED, format='an..30')
    result               = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='an..9')
    changed_indicator    = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='n1')
    unit                 = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='an..9')
    normality_indicator  = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='an1')
    lower_limit          = EDIElement[str](position=7, usage=Usage.OPTIONAL, format='an..9')
    upper_limit          = EDIElement[str](position=8, usage=Usage.OPTIONAL, format='an..9')
    determination_code   = EDIElement[str](position=9, usage=Usage.OPTIONAL, format='an..10')

# ################################################################################################################################
# ################################################################################################################################

class OPB(EDISegment):
    """ Opmerking laboratoriumbepaling - a remark about a determination.
    """
    _segment_tag = 'OPB'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class NUB(EDISegment):
    """ Nog uit te voeren laboratoriumbepaling - a determination that is still to be performed.
    """
    _segment_tag = 'NUB'

    determination = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..30')

# ################################################################################################################################
# ################################################################################################################################

class OPU(EDISegment):
    """ Opmerking uit te voeren lab. bepaling - a remark about a pending determination.
    """
    _segment_tag = 'OPU'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class COM(EDISegment):
    """ Algemeen commentaar laboratorium - general laboratory commentary.
    """
    _segment_tag = 'COM'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class VRG(EDISegment):
    """ Vraagstelling aanvrager - the requester's clinical question.
    """
    _segment_tag = 'VRG'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class OND(EDISegment):
    """ Uitgevoerde onderzoeken - an examination that was performed.
    """
    _segment_tag = 'OND'

    text             = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')
    examination_code = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='n4..7')

# ################################################################################################################################
# ################################################################################################################################

class VRS(EDISegment):
    """ Verslag radiologie - one line of the radiology report.
    """
    _segment_tag = 'VRS'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class CON(EDISegment):
    """ Algemene conclusie - one line of the general conclusion.
    """
    _segment_tag = 'CON'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class ADD(EDISegment):
    """ Addendum - one line of an addendum to a report.
    """
    _segment_tag = 'ADD'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..70')

# ################################################################################################################################
# ################################################################################################################################

class SPE(EDISegment):
    """ Specialist-/specialismegegevens - the specialist and their specialty.
    """
    _segment_tag = 'SPE'

    specialty   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='a..30')
    person_name = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='a..40')
    doctor_code = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='n6')

# ################################################################################################################################
# ################################################################################################################################

class REF(EDISegment):
    """ Referentie/kenmerk - a reference of the sending party.
    """
    _segment_tag = 'REF'

    reference = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..12')

# ################################################################################################################################
# ################################################################################################################################

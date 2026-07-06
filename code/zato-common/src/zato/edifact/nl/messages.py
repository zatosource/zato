# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The message definitions of the Dutch Medeur EDIFACT dialect, as specified by Nictiz in
# "Specificatie berichten 3i-project, versie 3.BSN" - MEDLAB (laboratory results),
# MEDVRI (free-format messages), MEDRAD (radiology reports) and MEDSPE (specialist letters).

from __future__ import annotations

# Zato
from zato.edifact.base import EDIGroup, EDIGroupAttr, EDIMessage, EDIRepeatableList, EDISegmentAttr
from zato.edifact.nl.segments import ADD, AFD, ARA, ART, BEP, BLG, COM, CON, DET, GGA, GGO, IDE, KOP, NUB, OND, OPB, OPM, OPU, \
     PAD, PID, REF, SEC, SPE, TXT, VRG, VRS, ZKH
from zato.edifact.service import UNH, UNT

# ################################################################################################################################
# ################################################################################################################################

class MEDVRI(EDIMessage):
    """ Vrij bericht - a free-format message between doctors or from an institution to doctors.
    """
    _message_type = 'MEDVRI'
    _message_version = '1'

    unh    = EDISegmentAttr[UNH](UNH)
    sender = EDISegmentAttr[GGA](GGA)
    det    = EDISegmentAttr[DET](DET)
    pid    = EDISegmentAttr[PID](PID, optional=True)
    pad    = EDISegmentAttr[PAD](PAD, optional=True)
    text   = EDISegmentAttr[EDIRepeatableList](TXT, repeatable=True)
    receiver = EDISegmentAttr[GGO](GGO, optional=True)
    unt    = EDISegmentAttr[UNT](UNT)

# ################################################################################################################################
# ################################################################################################################################

class MedlabMaterial(EDIGroup):
    """ One specimen or request of a MEDLAB message - the repeating group that starts at
    each DET and carries the identification, remarks, determinations and their results.
    """
    _leader_tag = 'DET'

    det                   = EDISegmentAttr[DET](DET)
    ide                   = EDISegmentAttr[IDE](IDE)
    remarks               = EDISegmentAttr[EDIRepeatableList](OPM, optional=True, repeatable=True)
    section               = EDISegmentAttr[SEC](SEC, optional=True)
    determinations        = EDISegmentAttr[EDIRepeatableList](BEP, optional=True, repeatable=True)
    determination_remarks = EDISegmentAttr[EDIRepeatableList](OPB, optional=True, repeatable=True)
    pending               = EDISegmentAttr[EDIRepeatableList](NUB, optional=True, repeatable=True)
    pending_remarks       = EDISegmentAttr[EDIRepeatableList](OPU, optional=True, repeatable=True)
    comments              = EDISegmentAttr[EDIRepeatableList](COM, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class MEDLAB(EDIMessage):
    """ Laboratoriumbericht - clinical chemistry and haematology results from a laboratory
    to general practitioners.
    """
    _message_type = 'MEDLAB'
    _message_version = '1'

    unh         = EDISegmentAttr[UNH](UNH)
    hospital    = EDISegmentAttr[ZKH](ZKH)
    pid         = EDISegmentAttr[PID](PID)
    pad         = EDISegmentAttr[PAD](PAD, optional=True)
    blood_group = EDISegmentAttr[BLG](BLG, optional=True)
    doctor      = EDISegmentAttr[ART](ART, optional=True)
    department  = EDISegmentAttr[AFD](AFD)
    lab_doctors = EDISegmentAttr[EDIRepeatableList](ARA, repeatable=True)
    copies      = EDISegmentAttr[KOP](KOP, optional=True)
    materials   = EDIGroupAttr[EDIRepeatableList](MedlabMaterial)
    unt         = EDISegmentAttr[UNT](UNT)

# ################################################################################################################################
# ################################################################################################################################

class MEDRAD(EDIMessage):
    """ Radiologiebericht - a radiology report from the hospital to the requesting doctor.
    """
    _message_type = 'MEDRAD'
    _message_version = '1'

    unh          = EDISegmentAttr[UNH](UNH)
    hospital     = EDISegmentAttr[ZKH](ZKH)
    pid          = EDISegmentAttr[PID](PID)
    pad          = EDISegmentAttr[PAD](PAD, optional=True)
    doctor       = EDISegmentAttr[ART](ART, optional=True)
    department   = EDISegmentAttr[AFD](AFD)
    radiologists = EDISegmentAttr[EDIRepeatableList](ARA, repeatable=True)
    det          = EDISegmentAttr[DET](DET)
    copies       = EDISegmentAttr[KOP](KOP, optional=True)
    questions    = EDISegmentAttr[EDIRepeatableList](VRG, optional=True, repeatable=True)
    examinations = EDISegmentAttr[EDIRepeatableList](OND, repeatable=True)
    report       = EDISegmentAttr[EDIRepeatableList](VRS, repeatable=True)
    conclusions  = EDISegmentAttr[EDIRepeatableList](CON, optional=True, repeatable=True)
    addenda      = EDISegmentAttr[EDIRepeatableList](ADD, optional=True, repeatable=True)
    unt          = EDISegmentAttr[UNT](UNT)

# ################################################################################################################################
# ################################################################################################################################

class MEDSPE(EDIMessage):
    """ Specialistenbrief - a letter from a specialist to the general practitioner about
    the progress of the examination or treatment of a patient.
    """
    _message_type = 'MEDSPE'
    _message_version = '1'

    unh         = EDISegmentAttr[UNH](UNH)
    doctors     = EDISegmentAttr[EDIRepeatableList](ART, repeatable=True)
    specialist  = EDISegmentAttr[SPE](SPE)
    hospital    = EDISegmentAttr[ZKH](ZKH, optional=True)
    department  = EDISegmentAttr[AFD](AFD, optional=True)
    pid         = EDISegmentAttr[PID](PID, optional=True)
    pad         = EDISegmentAttr[PAD](PAD, optional=True)
    det         = EDISegmentAttr[DET](DET)
    copies      = EDISegmentAttr[KOP](KOP, optional=True)
    reference   = EDISegmentAttr[REF](REF, optional=True)
    text        = EDISegmentAttr[EDIRepeatableList](TXT, repeatable=True)
    conclusions = EDISegmentAttr[EDIRepeatableList](CON, optional=True, repeatable=True)
    unt         = EDISegmentAttr[UNT](UNT)

# ################################################################################################################################
# ################################################################################################################################

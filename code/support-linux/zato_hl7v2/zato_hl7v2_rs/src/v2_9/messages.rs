// Generated - do not edit
use crate::{RawMessage, RawGroup, RawSegment, ParseError, SegmentCursor};

pub fn parse_ack(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ACK");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_adt_a01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
        let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
        grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_next_of_kin.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_next_of_kin);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IAM"]) {
        if let Some(s) = segments.optional("IAM") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "IN1", "IN2", "IN3", "PRT", "RF1", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AUT", "PRT"]) {
            let mut grp_authorization = RawGroup::new("AUTHORIZATION");
            grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_authorization.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_authorization);
        }
        while segments.peek_matches_any(&["PRT", "RF1"]) {
            let mut grp_referral = RawGroup::new("REFERRAL");
            grp_referral.push(RawSegment::from_tokens(&segments.expect("RF1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_referral.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_referral);
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UB1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UB2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("PDA") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    if let Some(s) = segments.optional("PDA") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
        let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
        grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_next_of_kin.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_next_of_kin);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IAM"]) {
        if let Some(s) = segments.optional("IAM") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "IN1", "IN2", "IN3", "PRT", "RF1", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AUT", "PRT"]) {
            let mut grp_authorization = RawGroup::new("AUTHORIZATION");
            grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_authorization.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_authorization);
        }
        while segments.peek_matches_any(&["PRT", "RF1"]) {
            let mut grp_referral = RawGroup::new("REFERRAL");
            grp_referral.push(RawSegment::from_tokens(&segments.expect("RF1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_referral.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_referral);
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("PDA") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a05(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A05");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
        let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
        grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_next_of_kin.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_next_of_kin);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IAM"]) {
        if let Some(s) = segments.optional("IAM") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "IN1", "IN2", "IN3", "PRT", "RF1", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AUT", "PRT"]) {
            let mut grp_authorization = RawGroup::new("AUTHORIZATION");
            grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_authorization.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_authorization);
        }
        while segments.peek_matches_any(&["PRT", "RF1"]) {
            let mut grp_referral = RawGroup::new("REFERRAL");
            grp_referral.push(RawSegment::from_tokens(&segments.expect("RF1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_referral.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_referral);
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UB1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UB2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a06(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A06");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("MRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
        let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
        grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_next_of_kin.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_next_of_kin);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IAM"]) {
        if let Some(s) = segments.optional("IAM") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3", "PRT", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UB1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UB2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a09(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A09");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_adt_a12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    if let Some(s) = segments.optional("DG1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a15(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A15");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PRT")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    Ok(msg)
}
pub fn parse_adt_a16(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A16");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
        let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
        grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_next_of_kin.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_next_of_kin);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IAM"]) {
        if let Some(s) = segments.optional("IAM") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "IN1", "IN2", "IN3", "PRT", "RF1", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AUT", "PRT"]) {
            let mut grp_authorization = RawGroup::new("AUTHORIZATION");
            grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_authorization.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_authorization);
        }
        while segments.peek_matches_any(&["PRT", "RF1"]) {
            let mut grp_referral = RawGroup::new("REFERRAL");
            grp_referral.push(RawSegment::from_tokens(&segments.expect("RF1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_referral.push(RawSegment::from_tokens(&s));
                }
            }
            grp_insurance.push_group(grp_referral);
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a17(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A17");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation_result_1 = RawGroup::new("OBSERVATION_RESULT_1");
        grp_observation_result_1.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation_result_1.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation_result_1);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation_result_2 = RawGroup::new("OBSERVATION_RESULT_2");
        grp_observation_result_2.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation_result_2.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation_result_2);
    }
    Ok(msg)
}
pub fn parse_adt_a20(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A20");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("NPU")?));
    Ok(msg)
}
pub fn parse_adt_a21(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A21");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    Ok(msg)
}
pub fn parse_adt_a24(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A24");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("PV1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("PV1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_adt_a37(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A37");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("PV1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("PV1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_adt_a38(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A38");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a39(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A39");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    while segments.peek_matches_any(&["MRG", "PD1", "PID", "PV1"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        grp_patient.push(RawSegment::from_tokens(&segments.expect("MRG")?));
        if let Some(s) = segments.optional("PV1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_adt_a43(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A43");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    while segments.peek_matches_any(&["MRG", "PD1", "PID"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        grp_patient.push(RawSegment::from_tokens(&segments.expect("MRG")?));
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_adt_a44(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A44");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    while segments.peek_matches_any(&["ARV", "MRG", "PD1", "PID"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        grp_patient.push(RawSegment::from_tokens(&segments.expect("MRG")?));
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_adt_a45(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A45");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["MRG", "PV1"]) {
        let mut grp_merge_info = RawGroup::new("MERGE_INFO");
        grp_merge_info.push(RawSegment::from_tokens(&segments.expect("MRG")?));
        grp_merge_info.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        msg.push_group(grp_merge_info);
    }
    Ok(msg)
}
pub fn parse_adt_a50(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A50");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MRG")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    Ok(msg)
}
pub fn parse_adt_a52(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A52");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_adt_a54(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A54");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_adt_a60(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A60");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "PV1", "PV2"]) {
        let mut grp_visit_group = RawGroup::new("VISIT_GROUP");
        grp_visit_group.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit_group.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_visit_group.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_visit_group);
    }
    while segments.peek_matches_any(&["IAM", "IAR", "NTE"]) {
        let mut grp_adverse_reaction_group = RawGroup::new("ADVERSE_REACTION_GROUP");
        grp_adverse_reaction_group.push(RawSegment::from_tokens(&segments.expect("IAM")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_adverse_reaction_group.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IAR"]) {
            if let Some(s) = segments.optional("IAR") {
                grp_adverse_reaction_group.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_adverse_reaction_group);
    }
    Ok(msg)
}
pub fn parse_adt_a61(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ADT_A61");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_bar_p01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BAR_P01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ACC", "AL1", "DB1", "DG1", "DRG", "GT1", "IN1", "IN2", "IN3", "NK1", "OBX", "PR1", "PRT", "PV1", "PV2", "ROL", "UB1", "UB2"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DB1"]) {
            if let Some(s) = segments.optional("DB1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DG1"]) {
            let mut grp_diagnosis = RawGroup::new("DIAGNOSIS");
            grp_diagnosis.push(RawSegment::from_tokens(&segments.expect("DG1")?));
            grp_visit.push_group(grp_diagnosis);
        }
        if let Some(s) = segments.optional("DRG") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
            let mut grp_procedure = RawGroup::new("PROCEDURE");
            grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            grp_visit.push_group(grp_procedure);
        }
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3", "PRT", "ROL"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["IN3"]) {
                if let Some(s) = segments.optional("IN3") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            grp_visit.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("ACC") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("UB1") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("UB2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_visit);
    }
    Ok(msg)
}
pub fn parse_bar_p02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BAR_P02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    while segments.peek_matches_any(&["DB1", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("PV1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["DB1"]) {
            if let Some(s) = segments.optional("DB1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_bar_p05(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BAR_P05");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ABS", "ACC", "AL1", "BLC", "DB1", "DG1", "DRG", "GT1", "IN1", "IN2", "IN3", "NK1", "OBX", "PR1", "PRT", "PV1", "PV2", "RMI", "ROL", "UB1", "UB2"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DB1"]) {
            if let Some(s) = segments.optional("DB1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DG1"]) {
            let mut grp_diagnosis = RawGroup::new("DIAGNOSIS");
            grp_diagnosis.push(RawSegment::from_tokens(&segments.expect("DG1")?));
            grp_visit.push_group(grp_diagnosis);
        }
        if let Some(s) = segments.optional("DRG") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
            let mut grp_procedure = RawGroup::new("PROCEDURE");
            grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            grp_visit.push_group(grp_procedure);
        }
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3", "PRT", "ROL"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["IN3"]) {
                if let Some(s) = segments.optional("IN3") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            grp_visit.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("ACC") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("UB1") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("UB2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("ABS") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["BLC"]) {
            if let Some(s) = segments.optional("BLC") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("RMI") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_visit);
    }
    Ok(msg)
}
pub fn parse_bar_p06(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BAR_P06");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    while segments.peek_matches_any(&["PID", "PRT", "PV1"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("PV1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_bar_p10(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BAR_P10");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    while segments.peek_matches_any(&["DG1"]) {
        let mut grp_diagnosis = RawGroup::new("DIAGNOSIS");
        grp_diagnosis.push(RawSegment::from_tokens(&segments.expect("DG1")?));
        msg.push_group(grp_diagnosis);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("GP1")?));
    while segments.peek_matches_any(&["GP2", "PR1"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        if let Some(s) = segments.optional("GP2") {
            grp_procedure.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_procedure);
    }
    Ok(msg)
}
pub fn parse_bar_p12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BAR_P12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    while segments.peek_matches_any(&["DG1"]) {
        let mut grp_diagnosis = RawGroup::new("DIAGNOSIS");
        grp_diagnosis.push(RawSegment::from_tokens(&segments.expect("DG1")?));
        msg.push_group(grp_diagnosis);
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_procedure.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_procedure);
    }
    if let Some(s) = segments.optional("OBX") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_bps_o29(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BPS_O29");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BPO", "BPX", "NTE", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("BPO")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["BPX", "NTE"]) {
            let mut grp_product = RawGroup::new("PRODUCT");
            grp_product.push(RawSegment::from_tokens(&segments.expect("BPX")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_product.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_product);
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_brp_o30(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BRP_O30");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "BPO", "BPX", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "BPO", "BPX", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["BPO", "BPX", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing);
                }
                if let Some(s) = segments.optional("BPO") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["BPX"]) {
                    if let Some(s) = segments.optional("BPX") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_patient.push_group(grp_order);
            }
            grp_response.push_group(grp_patient);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_brt_o32(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BRT_O32");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "BPO", "BTX", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["BPO", "BTX", "ORC", "PRT", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if let Some(s) = segments.optional("BPO") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["BTX"]) {
                if let Some(s) = segments.optional("BTX") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_bts_o31(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("BTS_O31");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BPO", "BTX", "NTE", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("BPO")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["BTX", "NTE"]) {
            let mut grp_product_status = RawGroup::new("PRODUCT_STATUS");
            grp_product_status.push(RawSegment::from_tokens(&segments.expect("BTX")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_product_status.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_product_status);
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_ccf_i22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CCF_I22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    Ok(msg)
}
pub fn parse_cci_i22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CCI_I22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "RGS", "SCH"]) {
        let mut grp_appointment_history = RawGroup::new("APPOINTMENT_HISTORY");
        grp_appointment_history.push(RawSegment::from_tokens(&segments.expect("SCH")?));
        while segments.peek_matches_any(&["OBX", "PRT", "RGS"]) {
            let mut grp_resources = RawGroup::new("RESOURCES");
            grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_resource_detail = RawGroup::new("RESOURCE_DETAIL");

                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_resource_observation = RawGroup::new("RESOURCE_OBSERVATION");
                    grp_resource_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_resource_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_resource_detail.push_group(grp_resource_observation);
                }
                grp_resources.push_group(grp_resource_detail);
            }
            grp_appointment_history.push_group(grp_resources);
        }
        msg.push_group(grp_appointment_history);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "VAR"]) {
        let mut grp_clinical_history = RawGroup::new("CLINICAL_HISTORY");
        grp_clinical_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_clinical_history_detail = RawGroup::new("CLINICAL_HISTORY_DETAIL");

            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_clinical_history_observation = RawGroup::new("CLINICAL_HISTORY_OBSERVATION");
                grp_clinical_history_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_clinical_history_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_clinical_history_detail.push_group(grp_clinical_history_observation);
            }
            grp_clinical_history.push_group(grp_clinical_history_detail);
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_clinical_history = RawGroup::new("PARTICIPATION_CLINICAL_HISTORY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_clinical_history.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clinical_history.push_group(grp_participation_clinical_history);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_clinical_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_clinical_history);
    }
    while segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visits = RawGroup::new("PATIENT_VISITS");
        grp_patient_visits.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visits.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visits);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "RXA", "RXC", "RXE", "RXO", "RXR"]) {
        let mut grp_medication_history = RawGroup::new("MEDICATION_HISTORY");
        grp_medication_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_medication_order_detail = RawGroup::new("MEDICATION_ORDER_DETAIL");
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_order_observation = RawGroup::new("MEDICATION_ORDER_OBSERVATION");
                grp_medication_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_order_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_order_detail.push_group(grp_medication_order_observation);
            }
            grp_medication_history.push_group(grp_medication_order_detail);
        }
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXE", "RXR"]) {
            let mut grp_medication_encoding_detail = RawGroup::new("MEDICATION_ENCODING_DETAIL");
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_encoding_observation = RawGroup::new("MEDICATION_ENCODING_OBSERVATION");
                grp_medication_encoding_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_encoding_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_encoding_detail.push_group(grp_medication_encoding_observation);
            }
            grp_medication_history.push_group(grp_medication_encoding_detail);
        }
        while segments.peek_matches_any(&["OBX", "PRT", "RXA", "RXR"]) {
            let mut grp_medication_administration_detail = RawGroup::new("MEDICATION_ADMINISTRATION_DETAIL");
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXA")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_administration_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_administration_observation = RawGroup::new("MEDICATION_ADMINISTRATION_OBSERVATION");
                grp_medication_administration_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_administration_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_administration_detail.push_group(grp_medication_administration_observation);
            }
            grp_medication_history.push_group(grp_medication_administration_detail);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_medication_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_medication_history);
    }
    while segments.peek_matches_any(&["OBX", "PRB", "PRT", "VAR"]) {
        let mut grp_problem = RawGroup::new("PROBLEM");
        grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_problem = RawGroup::new("PARTICIPATION_PROBLEM");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_problem.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_participation_problem);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
            grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_problem_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_problem_observation);
        }
        msg.push_group(grp_problem);
    }
    while segments.peek_matches_any(&["GOL", "OBX", "PRT", "VAR"]) {
        let mut grp_goal = RawGroup::new("GOAL");
        grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_goal = RawGroup::new("PARTICIPATION_GOAL");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_goal.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_participation_goal);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
            grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_goal_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_goal_observation);
        }
        msg.push_group(grp_goal);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "PTH", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_pathway = RawGroup::new("PARTICIPATION_PATHWAY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_participation_pathway);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_pathway_observation = RawGroup::new("PATHWAY_OBSERVATION");
            grp_pathway_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_pathway_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_observation);
        }
        msg.push_group(grp_pathway);
    }
    while segments.peek_matches_any(&["REL"]) {
        if let Some(s) = segments.optional("REL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_ccm_i21(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CCM_I21");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "RGS", "SCH"]) {
        let mut grp_appointment_history = RawGroup::new("APPOINTMENT_HISTORY");
        grp_appointment_history.push(RawSegment::from_tokens(&segments.expect("SCH")?));
        while segments.peek_matches_any(&["OBX", "PRT", "RGS"]) {
            let mut grp_resources = RawGroup::new("RESOURCES");
            grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_resource_detail = RawGroup::new("RESOURCE_DETAIL");

                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_resource_observation = RawGroup::new("RESOURCE_OBSERVATION");
                    grp_resource_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_resource_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_resource_detail.push_group(grp_resource_observation);
                }
                grp_resources.push_group(grp_resource_detail);
            }
            grp_appointment_history.push_group(grp_resources);
        }
        msg.push_group(grp_appointment_history);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "VAR"]) {
        let mut grp_clinical_history = RawGroup::new("CLINICAL_HISTORY");
        grp_clinical_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_clinical_history_detail = RawGroup::new("CLINICAL_HISTORY_DETAIL");

            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_clinical_history_observation = RawGroup::new("CLINICAL_HISTORY_OBSERVATION");
                grp_clinical_history_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_clinical_history_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_clinical_history_detail.push_group(grp_clinical_history_observation);
            }
            grp_clinical_history.push_group(grp_clinical_history_detail);
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_clinical_history = RawGroup::new("PARTICIPATION_CLINICAL_HISTORY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_clinical_history.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clinical_history.push_group(grp_participation_clinical_history);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_clinical_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_clinical_history);
    }
    while segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visits = RawGroup::new("PATIENT_VISITS");
        grp_patient_visits.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visits.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visits);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "RXA", "RXC", "RXE", "RXO", "RXR"]) {
        let mut grp_medication_history = RawGroup::new("MEDICATION_HISTORY");
        grp_medication_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_medication_order_detail = RawGroup::new("MEDICATION_ORDER_DETAIL");
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_order_observation = RawGroup::new("MEDICATION_ORDER_OBSERVATION");
                grp_medication_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_order_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_order_detail.push_group(grp_medication_order_observation);
            }
            grp_medication_history.push_group(grp_medication_order_detail);
        }
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXE", "RXR"]) {
            let mut grp_medication_encoding_detail = RawGroup::new("MEDICATION_ENCODING_DETAIL");
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_encoding_observation = RawGroup::new("MEDICATION_ENCODING_OBSERVATION");
                grp_medication_encoding_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_encoding_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_encoding_detail.push_group(grp_medication_encoding_observation);
            }
            grp_medication_history.push_group(grp_medication_encoding_detail);
        }
        while segments.peek_matches_any(&["OBX", "PRT", "RXA", "RXR"]) {
            let mut grp_medication_administration_detail = RawGroup::new("MEDICATION_ADMINISTRATION_DETAIL");
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXA")?));
            while segments.peek_matches_any(&["RXA"]) {
                if let Some(s) = segments.optional("RXA") {
                    grp_medication_administration_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_administration_observation = RawGroup::new("MEDICATION_ADMINISTRATION_OBSERVATION");
                grp_medication_administration_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_administration_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_administration_detail.push_group(grp_medication_administration_observation);
            }
            grp_medication_history.push_group(grp_medication_administration_detail);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_medication_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_medication_history);
    }
    while segments.peek_matches_any(&["OBX", "PRB", "PRT", "VAR"]) {
        let mut grp_problem = RawGroup::new("PROBLEM");
        grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_problem = RawGroup::new("PARTICIPATION_PROBLEM");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_problem.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_participation_problem);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
            grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_problem_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_problem_observation);
        }
        msg.push_group(grp_problem);
    }
    while segments.peek_matches_any(&["GOL", "OBX", "PRT", "VAR"]) {
        let mut grp_goal = RawGroup::new("GOAL");
        grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_goal = RawGroup::new("PARTICIPATION_GOAL");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_goal.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_participation_goal);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
            grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_goal_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_goal_observation);
        }
        msg.push_group(grp_goal);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "PTH", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_pathway = RawGroup::new("PARTICIPATION_PATHWAY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_participation_pathway);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_pathway_observation = RawGroup::new("PATHWAY_OBSERVATION");
            grp_pathway_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_pathway_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_observation);
        }
        msg.push_group(grp_pathway);
    }
    while segments.peek_matches_any(&["REL"]) {
        if let Some(s) = segments.optional("REL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_ccq_i19(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CCQ_I19");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RF1")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider_contact = RawGroup::new("PROVIDER_CONTACT");
        grp_provider_contact.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider_contact.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider_contact);
    }
    while segments.peek_matches_any(&["REL"]) {
        if let Some(s) = segments.optional("REL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_ccr_i16(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CCR_I16");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RF1")?));
    while segments.peek_matches_any(&["RF1"]) {
        if let Some(s) = segments.optional("RF1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider_contact = RawGroup::new("PROVIDER_CONTACT");
        grp_provider_contact.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider_contact.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider_contact);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_clinical_order = RawGroup::new("CLINICAL_ORDER");
        grp_clinical_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_clinical_order_timing = RawGroup::new("CLINICAL_ORDER_TIMING");
            grp_clinical_order_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_clinical_order_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clinical_order.push_group(grp_clinical_order_timing);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_clinical_order_detail = RawGroup::new("CLINICAL_ORDER_DETAIL");

            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_clinical_order_observation = RawGroup::new("CLINICAL_ORDER_OBSERVATION");
                grp_clinical_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_clinical_order_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_clinical_order_detail.push_group(grp_clinical_order_observation);
            }
            grp_clinical_order.push_group(grp_clinical_order_detail);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_clinical_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_clinical_order);
    }
    while segments.peek_matches_any(&["PD1", "PID"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "RGS", "SCH"]) {
        let mut grp_appointment_history = RawGroup::new("APPOINTMENT_HISTORY");
        grp_appointment_history.push(RawSegment::from_tokens(&segments.expect("SCH")?));
        while segments.peek_matches_any(&["OBX", "PRT", "RGS"]) {
            let mut grp_resources = RawGroup::new("RESOURCES");
            grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_resource_detail = RawGroup::new("RESOURCE_DETAIL");

                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_resource_observation = RawGroup::new("RESOURCE_OBSERVATION");
                    grp_resource_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_resource_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_resource_detail.push_group(grp_resource_observation);
                }
                grp_resources.push_group(grp_resource_detail);
            }
            grp_appointment_history.push_group(grp_resources);
        }
        msg.push_group(grp_appointment_history);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "VAR"]) {
        let mut grp_clinical_history = RawGroup::new("CLINICAL_HISTORY");
        grp_clinical_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_clinical_history_detail = RawGroup::new("CLINICAL_HISTORY_DETAIL");

            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_clinical_history_observation = RawGroup::new("CLINICAL_HISTORY_OBSERVATION");
                grp_clinical_history_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_clinical_history_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_clinical_history_detail.push_group(grp_clinical_history_observation);
            }
            grp_clinical_history.push_group(grp_clinical_history_detail);
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_clinical_history = RawGroup::new("PARTICIPATION_CLINICAL_HISTORY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_clinical_history.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clinical_history.push_group(grp_participation_clinical_history);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_clinical_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_clinical_history);
    }
    while segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visits = RawGroup::new("PATIENT_VISITS");
        grp_patient_visits.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visits.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visits);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "RXA", "RXC", "RXE", "RXO", "RXR"]) {
        let mut grp_medication_history = RawGroup::new("MEDICATION_HISTORY");
        grp_medication_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_medication_order_detail = RawGroup::new("MEDICATION_ORDER_DETAIL");
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_order_observation = RawGroup::new("MEDICATION_ORDER_OBSERVATION");
                grp_medication_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_order_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_order_detail.push_group(grp_medication_order_observation);
            }
            grp_medication_history.push_group(grp_medication_order_detail);
        }
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXE", "RXR"]) {
            let mut grp_medication_encoding_detail = RawGroup::new("MEDICATION_ENCODING_DETAIL");
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_encoding_observation = RawGroup::new("MEDICATION_ENCODING_OBSERVATION");
                grp_medication_encoding_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_encoding_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_encoding_detail.push_group(grp_medication_encoding_observation);
            }
            grp_medication_history.push_group(grp_medication_encoding_detail);
        }
        while segments.peek_matches_any(&["OBX", "PRT", "RXA", "RXR"]) {
            let mut grp_medication_administration_detail = RawGroup::new("MEDICATION_ADMINISTRATION_DETAIL");
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXA")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_administration_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_administration_observation = RawGroup::new("MEDICATION_ADMINISTRATION_OBSERVATION");
                grp_medication_administration_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_administration_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_administration_detail.push_group(grp_medication_administration_observation);
            }
            grp_medication_history.push_group(grp_medication_administration_detail);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_medication_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_medication_history);
    }
    while segments.peek_matches_any(&["OBX", "PRB", "PRT", "VAR"]) {
        let mut grp_problem = RawGroup::new("PROBLEM");
        grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_problem = RawGroup::new("PARTICIPATION_PROBLEM");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_problem.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_participation_problem);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_participation_observation = RawGroup::new("PARTICIPATION_OBSERVATION");
            grp_participation_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_participation_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_participation_observation);
        }
        msg.push_group(grp_problem);
    }
    while segments.peek_matches_any(&["GOL", "OBX", "PRT", "VAR"]) {
        let mut grp_goal = RawGroup::new("GOAL");
        grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_goal = RawGroup::new("PARTICIPATION_GOAL");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_goal.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_participation_goal);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
            grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_goal_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_goal_observation);
        }
        msg.push_group(grp_goal);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "PTH", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_pathway = RawGroup::new("PARTICIPATION_PATHWAY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_participation_pathway);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_pathway_observation = RawGroup::new("PATHWAY_OBSERVATION");
            grp_pathway_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_pathway_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_observation);
        }
        msg.push_group(grp_pathway);
    }
    while segments.peek_matches_any(&["REL"]) {
        if let Some(s) = segments.optional("REL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_ccu_i20(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CCU_I20");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RF1")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider_contact = RawGroup::new("PROVIDER_CONTACT");
        grp_provider_contact.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider_contact.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider_contact);
    }
    while segments.peek_matches_any(&["PD1", "PID"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "RGS", "SCH"]) {
        let mut grp_appointment_history = RawGroup::new("APPOINTMENT_HISTORY");
        grp_appointment_history.push(RawSegment::from_tokens(&segments.expect("SCH")?));
        while segments.peek_matches_any(&["OBX", "PRT", "RGS"]) {
            let mut grp_resources = RawGroup::new("RESOURCES");
            grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_resource_detail = RawGroup::new("RESOURCE_DETAIL");

                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_resource_observation = RawGroup::new("RESOURCE_OBSERVATION");
                    grp_resource_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_resource_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_resource_detail.push_group(grp_resource_observation);
                }
                grp_resources.push_group(grp_resource_detail);
            }
            grp_appointment_history.push_group(grp_resources);
        }
        msg.push_group(grp_appointment_history);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "VAR"]) {
        let mut grp_clinical_history = RawGroup::new("CLINICAL_HISTORY");
        grp_clinical_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_clinical_history_detail = RawGroup::new("CLINICAL_HISTORY_DETAIL");

            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_clinical_history_observation = RawGroup::new("CLINICAL_HISTORY_OBSERVATION");
                grp_clinical_history_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_clinical_history_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_clinical_history_detail.push_group(grp_clinical_history_observation);
            }
            grp_clinical_history.push_group(grp_clinical_history_detail);
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_clinical_history = RawGroup::new("PARTICIPATION_CLINICAL_HISTORY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_clinical_history.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clinical_history.push_group(grp_participation_clinical_history);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_clinical_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_clinical_history);
    }
    while segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visits = RawGroup::new("PATIENT_VISITS");
        grp_patient_visits.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visits.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visits);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "RXA", "RXC", "RXE", "RXO", "RXR"]) {
        let mut grp_medication_history = RawGroup::new("MEDICATION_HISTORY");
        grp_medication_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_medication_order_detail = RawGroup::new("MEDICATION_ORDER_DETAIL");
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_order_observation = RawGroup::new("MEDICATION_ORDER_OBSERVATION");
                grp_medication_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_order_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_order_detail.push_group(grp_medication_order_observation);
            }
            grp_medication_history.push_group(grp_medication_order_detail);
        }
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXE", "RXR"]) {
            let mut grp_medication_encoding_detail = RawGroup::new("MEDICATION_ENCODING_DETAIL");
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_encoding_observation = RawGroup::new("MEDICATION_ENCODING_OBSERVATION");
                grp_medication_encoding_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_encoding_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_encoding_detail.push_group(grp_medication_encoding_observation);
            }
            grp_medication_history.push_group(grp_medication_encoding_detail);
        }
        while segments.peek_matches_any(&["OBX", "PRT", "RXA", "RXR"]) {
            let mut grp_medication_administration_detail = RawGroup::new("MEDICATION_ADMINISTRATION_DETAIL");
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXA")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_administration_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_administration_observation = RawGroup::new("MEDICATION_ADMINISTRATION_OBSERVATION");
                grp_medication_administration_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_administration_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_administration_detail.push_group(grp_medication_administration_observation);
            }
            grp_medication_history.push_group(grp_medication_administration_detail);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_medication_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_medication_history);
    }
    while segments.peek_matches_any(&["OBX", "PRB", "PRT", "VAR"]) {
        let mut grp_problem = RawGroup::new("PROBLEM");
        grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_problem = RawGroup::new("PARTICIPATION_PROBLEM");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_problem.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_participation_problem);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
            grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_problem_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_problem_observation);
        }
        msg.push_group(grp_problem);
    }
    while segments.peek_matches_any(&["GOL", "OBX", "PRT", "VAR"]) {
        let mut grp_goal = RawGroup::new("GOAL");
        grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_goal = RawGroup::new("PARTICIPATION_GOAL");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_goal.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_participation_goal);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
            grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_goal_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_goal_observation);
        }
        msg.push_group(grp_goal);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "PTH", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_pathway = RawGroup::new("PARTICIPATION_PATHWAY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_participation_pathway);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_pathway_observation = RawGroup::new("PATHWAY_OBSERVATION");
            grp_pathway_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_pathway_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_observation);
        }
        msg.push_group(grp_pathway);
    }
    while segments.peek_matches_any(&["REL"]) {
        if let Some(s) = segments.optional("REL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_cqu_i19(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CQU_I19");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RF1")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider_contact = RawGroup::new("PROVIDER_CONTACT");
        grp_provider_contact.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider_contact.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider_contact);
    }
    while segments.peek_matches_any(&["PD1", "PID"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "RGS", "SCH"]) {
        let mut grp_appointment_history = RawGroup::new("APPOINTMENT_HISTORY");
        grp_appointment_history.push(RawSegment::from_tokens(&segments.expect("SCH")?));
        while segments.peek_matches_any(&["OBX", "PRT", "RGS"]) {
            let mut grp_resources = RawGroup::new("RESOURCES");
            grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_resource_detail = RawGroup::new("RESOURCE_DETAIL");

                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_resource_observation = RawGroup::new("RESOURCE_OBSERVATION");
                    grp_resource_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_resource_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_resource_detail.push_group(grp_resource_observation);
                }
                grp_resources.push_group(grp_resource_detail);
            }
            grp_appointment_history.push_group(grp_resources);
        }
        msg.push_group(grp_appointment_history);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "VAR"]) {
        let mut grp_clinical_history = RawGroup::new("CLINICAL_HISTORY");
        grp_clinical_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_clinical_history_detail = RawGroup::new("CLINICAL_HISTORY_DETAIL");

            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_clinical_history_observation = RawGroup::new("CLINICAL_HISTORY_OBSERVATION");
                grp_clinical_history_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_clinical_history_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_clinical_history_detail.push_group(grp_clinical_history_observation);
            }
            grp_clinical_history.push_group(grp_clinical_history_detail);
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_clinical_history = RawGroup::new("PARTICIPATION_CLINICAL_HISTORY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_clinical_history.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clinical_history.push_group(grp_participation_clinical_history);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_clinical_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_clinical_history);
    }
    while segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visits = RawGroup::new("PATIENT_VISITS");
        grp_patient_visits.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visits.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visits);
    }
    while segments.peek_matches_any(&["CTI", "OBX", "ORC", "PRT", "RXA", "RXC", "RXE", "RXO", "RXR"]) {
        let mut grp_medication_history = RawGroup::new("MEDICATION_HISTORY");
        grp_medication_history.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_medication_order_detail = RawGroup::new("MEDICATION_ORDER_DETAIL");
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_order_observation = RawGroup::new("MEDICATION_ORDER_OBSERVATION");
                grp_medication_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_order_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_order_detail.push_group(grp_medication_order_observation);
            }
            grp_medication_history.push_group(grp_medication_order_detail);
        }
        if segments.peek_matches_any(&["OBX", "PRT", "RXC", "RXE", "RXR"]) {
            let mut grp_medication_encoding_detail = RawGroup::new("MEDICATION_ENCODING_DETAIL");
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_encoding_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_medication_encoding_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_encoding_observation = RawGroup::new("MEDICATION_ENCODING_OBSERVATION");
                grp_medication_encoding_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_encoding_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_encoding_detail.push_group(grp_medication_encoding_observation);
            }
            grp_medication_history.push_group(grp_medication_encoding_detail);
        }
        while segments.peek_matches_any(&["OBX", "PRT", "RXA", "RXR"]) {
            let mut grp_medication_administration_detail = RawGroup::new("MEDICATION_ADMINISTRATION_DETAIL");
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXA")?));
            while segments.peek_matches_any(&["RXA"]) {
                if let Some(s) = segments.optional("RXA") {
                    grp_medication_administration_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_medication_administration_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_medication_administration_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_medication_administration_observation = RawGroup::new("MEDICATION_ADMINISTRATION_OBSERVATION");
                grp_medication_administration_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_medication_administration_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_medication_administration_detail.push_group(grp_medication_administration_observation);
            }
            grp_medication_history.push_group(grp_medication_administration_detail);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_medication_history.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_medication_history);
    }
    while segments.peek_matches_any(&["OBX", "PRB", "PRT", "VAR"]) {
        let mut grp_problem = RawGroup::new("PROBLEM");
        grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_problem = RawGroup::new("PARTICIPATION_PROBLEM");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_problem.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_participation_problem);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
            grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_problem_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_problem_observation);
        }
        msg.push_group(grp_problem);
    }
    while segments.peek_matches_any(&["GOL", "OBX", "PRT", "VAR"]) {
        let mut grp_goal = RawGroup::new("GOAL");
        grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_goal = RawGroup::new("PARTICIPATION_GOAL");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_goal.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_participation_goal);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
            grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_goal_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_goal_observation);
        }
        msg.push_group(grp_goal);
    }
    while segments.peek_matches_any(&["OBX", "PRT", "PTH", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            let mut grp_participation_pathway = RawGroup::new("PARTICIPATION_PATHWAY");

            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_participation_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_participation_pathway);
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_pathway_observation = RawGroup::new("PATHWAY_OBSERVATION");
            grp_pathway_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_pathway_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_observation);
        }
        msg.push_group(grp_pathway);
    }
    while segments.peek_matches_any(&["REL"]) {
        if let Some(s) = segments.optional("REL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_crm_c01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CRM_C01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV", "CSP", "CSR", "PID", "PRT", "PV1"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        grp_patient.push(RawSegment::from_tokens(&segments.expect("CSR")?));
        while segments.peek_matches_any(&["CSP"]) {
            if let Some(s) = segments.optional("CSP") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_csu_c09(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("CSU_C09");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV", "CSP", "CSR", "CSS", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "RXA", "RXR", "TQ1", "TQ2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_visit = RawGroup::new("VISIT");
            grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_visit);
        }
        grp_patient.push(RawSegment::from_tokens(&segments.expect("CSR")?));
        while segments.peek_matches_any(&["CSP", "CSS", "OBR", "OBX", "ORC", "PRT", "RXA", "RXR", "TQ1", "TQ2"]) {
            let mut grp_study_phase = RawGroup::new("STUDY_PHASE");
            if let Some(s) = segments.optional("CSP") {
                grp_study_phase.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["CSS", "OBR", "OBX", "ORC", "PRT", "RXA", "RXR", "TQ1", "TQ2"]) {
                let mut grp_study_schedule = RawGroup::new("STUDY_SCHEDULE");
                if let Some(s) = segments.optional("CSS") {
                    grp_study_schedule.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                    let mut grp_study_observation = RawGroup::new("STUDY_OBSERVATION");
                    if segments.peek_matches_any(&["ORC", "PRT"]) {
                        let mut grp_study_observation_order = RawGroup::new("STUDY_OBSERVATION_ORDER");
                        grp_study_observation_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_study_observation_order.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_study_observation.push_group(grp_study_observation_order);
                    }
                    grp_study_observation.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_study_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                        let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
                        grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                        while segments.peek_matches_any(&["TQ2"]) {
                            if let Some(s) = segments.optional("TQ2") {
                                grp_timing_qty.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_study_observation.push_group(grp_timing_qty);
                    }
                    grp_study_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_study_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_study_schedule.push_group(grp_study_observation);
                }
                while segments.peek_matches_any(&["ORC", "PRT", "RXA", "RXR"]) {
                    let mut grp_study_pharm = RawGroup::new("STUDY_PHARM");
                    if segments.peek_matches_any(&["ORC", "PRT"]) {
                        let mut grp_common_order = RawGroup::new("COMMON_ORDER");
                        grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_common_order.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_study_pharm.push_group(grp_common_order);
                    }
                    while segments.peek_matches_any(&["PRT", "RXA", "RXR"]) {
                        let mut grp_rx_admin = RawGroup::new("RX_ADMIN");
                        grp_rx_admin.push(RawSegment::from_tokens(&segments.expect("RXA")?));
                        grp_rx_admin.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_rx_admin.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_study_pharm.push_group(grp_rx_admin);
                    }
                    grp_study_schedule.push_group(grp_study_pharm);
                }
                grp_study_phase.push_group(grp_study_schedule);
            }
            grp_patient.push_group(grp_study_phase);
        }
        msg.push_group(grp_patient);
    }
    Ok(msg)
}
pub fn parse_dbc_o41(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DBC_O41");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donor);
    }
    Ok(msg)
}
pub fn parse_dbc_o42(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DBC_O42");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donor);
    }
    Ok(msg)
}
pub fn parse_del_o46(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DEL_O46");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("DON")?));
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_deo_o45(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DEO_O45");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["ARV", "NTE", "OBX", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("Donor");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
        let mut grp_donation_order = RawGroup::new("DONATION_ORDER");
        grp_donation_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donation_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donation_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_donation_observation = RawGroup::new("DONATION_OBSERVATION");
            grp_donation_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donation_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donation_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donation_order.push_group(grp_donation_observation);
        }
        msg.push_group(grp_donation_order);
    }
    Ok(msg)
}
pub fn parse_der_o44(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DER_O44");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
        let mut grp_donor_order = RawGroup::new("DONOR_ORDER");
        grp_donor_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donor_order);
    }
    Ok(msg)
}
pub fn parse_dft_p03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DFT_P03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["PRT", "PV1", "PV2", "ROL"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        if let Some(s) = segments.optional("PV1") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_visit);
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_common_order = RawGroup::new("COMMON_ORDER");
        grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_quantity = RawGroup::new("TIMING_QUANTITY");
            grp_timing_quantity.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_quantity.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_timing_quantity);
        }
        if segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_order);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_observation);
        }
        msg.push_group(grp_common_order);
    }
    while segments.peek_matches_any(&["FT1", "NTE", "OBR", "OBX", "ORC", "PR1", "PRT", "ROL", "TQ1", "TQ2"]) {
        let mut grp_financial = RawGroup::new("FINANCIAL");
        grp_financial.push(RawSegment::from_tokens(&segments.expect("FT1")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_financial.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_financial.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_financial.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
            let mut grp_financial_procedure = RawGroup::new("FINANCIAL_PROCEDURE");
            grp_financial_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_financial_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            grp_financial.push_group(grp_financial_procedure);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_financial_observation_standalone = RawGroup::new("FINANCIAL_OBSERVATION_STANDALONE");
            grp_financial_observation_standalone.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_observation_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            grp_financial_observation_standalone.push(RawSegment::from_tokens(&segments.expect("NTE")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_financial_observation_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            grp_financial.push_group(grp_financial_observation_standalone);
        }
        while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
            let mut grp_financial_order_standalone = RawGroup::new("FINANCIAL_ORDER_STANDALONE");
            grp_financial_order_standalone.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_order_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_financial_order_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_financial_observation_2 = RawGroup::new("FINANCIAL_OBSERVATION_2");
                grp_financial_observation_2.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_financial_observation_2.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_financial_observation_2.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_order_standalone.push_group(grp_financial_observation_2);
            }
            grp_financial.push_group(grp_financial_order_standalone);
        }
        while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
            let mut grp_financial_common_order = RawGroup::new("FINANCIAL_COMMON_ORDER");
            grp_financial_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_financial_timing_quantity = RawGroup::new("FINANCIAL_TIMING_QUANTITY");
                grp_financial_timing_quantity.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_financial_timing_quantity.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_common_order.push_group(grp_financial_timing_quantity);
            }
            if segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
                let mut grp_financial_order = RawGroup::new("FINANCIAL_ORDER");
                grp_financial_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_financial_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_financial_order.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_common_order.push_group(grp_financial_order);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_financial_observation = RawGroup::new("FINANCIAL_OBSERVATION");
                grp_financial_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_financial_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_financial_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_common_order.push_group(grp_financial_observation);
            }
            grp_financial.push_group(grp_financial_common_order);
        }
        msg.push_group(grp_financial);
    }
    while segments.peek_matches_any(&["DG1"]) {
        let mut grp_diagnosis = RawGroup::new("DIAGNOSIS");
        grp_diagnosis.push(RawSegment::from_tokens(&segments.expect("DG1")?));
        msg.push_group(grp_diagnosis);
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3", "PRT", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_dft_p11(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DFT_P11");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["PRT", "PV1", "PV2", "ROL"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        if let Some(s) = segments.optional("PV1") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_visit);
    }
    while segments.peek_matches_any(&["DB1"]) {
        if let Some(s) = segments.optional("DB1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_common_order = RawGroup::new("COMMON_ORDER");
        grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_quantity = RawGroup::new("TIMING_QUANTITY");
            grp_timing_quantity.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_quantity.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_timing_quantity);
        }
        if segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_order);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_observation);
        }
        msg.push_group(grp_common_order);
    }
    while segments.peek_matches_any(&["DG1"]) {
        let mut grp_diagnosis = RawGroup::new("DIAGNOSIS");
        grp_diagnosis.push(RawSegment::from_tokens(&segments.expect("DG1")?));
        msg.push_group(grp_diagnosis);
    }
    if let Some(s) = segments.optional("DRG") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3", "PRT", "ROL"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["IN3"]) {
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DG1", "DRG", "FT1", "GT1", "IN1", "IN2", "IN3", "NTE", "OBR", "OBX", "ORC", "PR1", "PRT", "ROL", "TQ1", "TQ2"]) {
        let mut grp_financial = RawGroup::new("FINANCIAL");
        grp_financial.push(RawSegment::from_tokens(&segments.expect("FT1")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_financial.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_financial.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PR1", "PRT", "ROL"]) {
            let mut grp_financial_procedure = RawGroup::new("FINANCIAL_PROCEDURE");
            grp_financial_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_financial_procedure.push(RawSegment::from_tokens(&s));
                }
            }
            grp_financial.push_group(grp_financial_procedure);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT"]) {
            let mut grp_financial_observation_standalone = RawGroup::new("FINANCIAL_OBSERVATION_STANDALONE");
            grp_financial_observation_standalone.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_observation_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_financial_observation_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            grp_financial.push_group(grp_financial_observation_standalone);
        }
        while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
            let mut grp_financial_order_standalone = RawGroup::new("FINANCIAL_ORDER_STANDALONE");
            grp_financial_order_standalone.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_order_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_financial_order_standalone.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_financial_observation_2 = RawGroup::new("FINANCIAL_OBSERVATION_2");
                grp_financial_observation_2.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_financial_observation_2.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_financial_observation_2.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_order_standalone.push_group(grp_financial_observation_2);
            }
            grp_financial.push_group(grp_financial_order_standalone);
        }
        while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
            let mut grp_financial_common_order = RawGroup::new("FINANCIAL_COMMON_ORDER");
            grp_financial_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_financial_timing_quantity = RawGroup::new("FINANCIAL_TIMING_QUANTITY");
                grp_financial_timing_quantity.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_financial_timing_quantity.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_common_order.push_group(grp_financial_timing_quantity);
            }
            if segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
                let mut grp_financial_order = RawGroup::new("FINANCIAL_ORDER");
                grp_financial_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_financial_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_financial_order.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_common_order.push_group(grp_financial_order);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_financial_observation = RawGroup::new("FINANCIAL_OBSERVATION");
                grp_financial_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_financial_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_financial_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_financial_common_order.push_group(grp_financial_observation);
            }
            grp_financial.push_group(grp_financial_common_order);
        }
        while segments.peek_matches_any(&["DG1"]) {
            let mut grp_diagnosis_ft1 = RawGroup::new("DIAGNOSIS_FT1");
            grp_diagnosis_ft1.push(RawSegment::from_tokens(&segments.expect("DG1")?));
            grp_financial.push_group(grp_diagnosis_ft1);
        }
        if let Some(s) = segments.optional("DRG") {
            grp_financial.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_financial.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3", "PRT", "ROL"]) {
            let mut grp_financial_insurance = RawGroup::new("FINANCIAL_INSURANCE");
            grp_financial_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_financial_insurance.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["IN3"]) {
                if let Some(s) = segments.optional("IN3") {
                    grp_financial_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_financial_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ROL"]) {
                if let Some(s) = segments.optional("ROL") {
                    grp_financial_insurance.push(RawSegment::from_tokens(&s));
                }
            }
            grp_financial.push_group(grp_financial_insurance);
        }
        msg.push_group(grp_financial);
    }
    Ok(msg)
}
pub fn parse_dpr_o48(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DPR_O48");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
        let mut grp_donation_order = RawGroup::new("DONATION_ORDER");
        grp_donation_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donation_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donation_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donation_order);
    }
    if segments.peek_matches_any(&["BUI", "DON", "NTE", "OBX", "PRT"]) {
        let mut grp_donation = RawGroup::new("DONATION");
        grp_donation.push(RawSegment::from_tokens(&segments.expect("DON")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donation_observations = RawGroup::new("DONATION_OBSERVATIONS");
            grp_donation_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donation_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donation.push_group(grp_donation_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donation.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["BUI", "NTE"]) {
            let mut grp_blood_unit = RawGroup::new("BLOOD_UNIT");
            while segments.peek_matches_any(&["BUI"]) {
                if let Some(s) = segments.optional("BUI") {
                    grp_blood_unit.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_blood_unit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donation.push_group(grp_blood_unit);
        }
        msg.push_group(grp_donation);
    }
    Ok(msg)
}
pub fn parse_drc_o47(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DRC_O47");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
        let mut grp_donation_order = RawGroup::new("DONATION_ORDER");
        grp_donation_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donation_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donation_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donation_order);
    }
    Ok(msg)
}
pub fn parse_drg_o43(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("DRG_O43");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    Ok(msg)
}
pub fn parse_eac_u07(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EAC_U07");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["CNS", "DST", "ECD", "OBR", "PRT", "SAC", "SPM", "TQ1"]) {
        let mut grp_command = RawGroup::new("COMMAND");
        grp_command.push(RawSegment::from_tokens(&segments.expect("ECD")?));
        if let Some(s) = segments.optional("TQ1") {
            grp_command.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["DST", "OBR", "PRT", "SAC", "SPM"]) {
            let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
            grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
            while segments.peek_matches_any(&["OBR", "PRT"]) {
                let mut grp_order_for_specimen_container = RawGroup::new("ORDER_FOR_SPECIMEN_CONTAINER");
                while segments.peek_matches_any(&["OBR"]) {
                    if let Some(s) = segments.optional("OBR") {
                        grp_order_for_specimen_container.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order_for_specimen_container.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen_container.push_group(grp_order_for_specimen_container);
            }
            while segments.peek_matches_any(&["SPM"]) {
                if let Some(s) = segments.optional("SPM") {
                    grp_specimen_container.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["DST"]) {
                if let Some(s) = segments.optional("DST") {
                    grp_specimen_container.push(RawSegment::from_tokens(&s));
                }
            }
            grp_command.push_group(grp_specimen_container);
        }
        if let Some(s) = segments.optional("CNS") {
            grp_command.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_command);
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_ean_u09(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EAN_U09");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["NDS", "NTE"]) {
        let mut grp_notification = RawGroup::new("NOTIFICATION");
        grp_notification.push(RawSegment::from_tokens(&segments.expect("NDS")?));
        if let Some(s) = segments.optional("NTE") {
            grp_notification.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_notification);
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_ear_u08(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EAR_U08");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["ECD", "ECR", "SAC", "SPM"]) {
        let mut grp_command_response = RawGroup::new("COMMAND_RESPONSE");
        grp_command_response.push(RawSegment::from_tokens(&segments.expect("ECD")?));
        if segments.peek_matches_any(&["SAC", "SPM"]) {
            let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
            grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
            while segments.peek_matches_any(&["SPM"]) {
                if let Some(s) = segments.optional("SPM") {
                    grp_specimen_container.push(RawSegment::from_tokens(&s));
                }
            }
            grp_command_response.push_group(grp_specimen_container);
        }
        grp_command_response.push(RawSegment::from_tokens(&segments.expect("ECR")?));
        msg.push_group(grp_command_response);
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_ehc_e01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_ehc_e02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_ehc_e04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_ehc_e10(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E10");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ADJ", "IN1", "IN2", "IPR", "IVC", "NTE", "PSG", "PSL", "PSS", "PYE"]) {
        let mut grp_invoice_processing_results_info = RawGroup::new("INVOICE_PROCESSING_RESULTS_INFO");
        grp_invoice_processing_results_info.push(RawSegment::from_tokens(&segments.expect("IPR")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_invoice_processing_results_info.push(RawSegment::from_tokens(&s));
            }
        }
        grp_invoice_processing_results_info.push(RawSegment::from_tokens(&segments.expect("PYE")?));
        grp_invoice_processing_results_info.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_invoice_processing_results_info.push(RawSegment::from_tokens(&s));
        }
        grp_invoice_processing_results_info.push(RawSegment::from_tokens(&segments.expect("IVC")?));
        while segments.peek_matches_any(&["ADJ", "PSG", "PSL", "PSS"]) {
            let mut grp_product_service_section = RawGroup::new("PRODUCT_SERVICE_SECTION");
            grp_product_service_section.push(RawSegment::from_tokens(&segments.expect("PSS")?));
            while segments.peek_matches_any(&["ADJ", "PSG", "PSL"]) {
                let mut grp_product_service_group = RawGroup::new("PRODUCT_SERVICE_GROUP");
                grp_product_service_group.push(RawSegment::from_tokens(&segments.expect("PSG")?));
                while segments.peek_matches_any(&["ADJ", "PSL"]) {
                    let mut grp_product_service_line_info = RawGroup::new("PRODUCT_SERVICE_LINE_INFO");
                    grp_product_service_line_info.push(RawSegment::from_tokens(&segments.expect("PSL")?));
                    while segments.peek_matches_any(&["ADJ"]) {
                        if let Some(s) = segments.optional("ADJ") {
                            grp_product_service_line_info.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_product_service_group.push_group(grp_product_service_line_info);
                }
                grp_product_service_section.push_group(grp_product_service_group);
            }
            grp_invoice_processing_results_info.push_group(grp_product_service_section);
        }
        msg.push_group(grp_invoice_processing_results_info);
    }
    Ok(msg)
}
pub fn parse_ehc_e12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RFI")?));
    while segments.peek_matches_any(&["CTD"]) {
        if let Some(s) = segments.optional("CTD") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("IVC")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PSS")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PSG")?));
    if let Some(s) = segments.optional("PID") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PSL"]) {
        if let Some(s) = segments.optional("PSL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CTD", "NTE", "OBR", "OBX", "PRT"]) {
        let mut grp_request = RawGroup::new("REQUEST");
        if let Some(s) = segments.optional("CTD") {
            grp_request.push(RawSegment::from_tokens(&s));
        }
        grp_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_request.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("NTE") {
            grp_request.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_request.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_request.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_request);
    }
    Ok(msg)
}
pub fn parse_ehc_e13(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E13");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RFI")?));
    while segments.peek_matches_any(&["CTD"]) {
        if let Some(s) = segments.optional("CTD") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("IVC")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PSS")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PSG")?));
    if let Some(s) = segments.optional("PID") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("PSL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["CTD", "NTE", "OBR", "OBX", "PRT", "TXA"]) {
        let mut grp_request = RawGroup::new("REQUEST");
        if let Some(s) = segments.optional("CTD") {
            grp_request.push(RawSegment::from_tokens(&s));
        }
        grp_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_request.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("NTE") {
            grp_request.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT", "TXA"]) {
            let mut grp_response = RawGroup::new("RESPONSE");
            grp_response.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_response.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("NTE") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("TXA") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
            grp_request.push_group(grp_response);
        }
        msg.push_group(grp_request);
    }
    Ok(msg)
}
pub fn parse_ehc_e15(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E15");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    while segments.peek_matches_any(&["ADJ", "IPR", "IVC", "PSG", "PSL", "PSS"]) {
        let mut grp_payment_remittance_detail_info = RawGroup::new("PAYMENT_REMITTANCE_DETAIL_INFO");
        grp_payment_remittance_detail_info.push(RawSegment::from_tokens(&segments.expect("IPR")?));
        grp_payment_remittance_detail_info.push(RawSegment::from_tokens(&segments.expect("IVC")?));
        while segments.peek_matches_any(&["ADJ", "PSG", "PSL", "PSS"]) {
            let mut grp_product_service_section = RawGroup::new("PRODUCT_SERVICE_SECTION");
            grp_product_service_section.push(RawSegment::from_tokens(&segments.expect("PSS")?));
            while segments.peek_matches_any(&["ADJ", "PSG", "PSL"]) {
                let mut grp_product_service_group = RawGroup::new("PRODUCT_SERVICE_GROUP");
                grp_product_service_group.push(RawSegment::from_tokens(&segments.expect("PSG")?));
                while segments.peek_matches_any(&["ADJ", "PSL"]) {
                    let mut grp_psl_item_info = RawGroup::new("PSL_ITEM_INFO");
                    grp_psl_item_info.push(RawSegment::from_tokens(&segments.expect("PSL")?));
                    while segments.peek_matches_any(&["ADJ"]) {
                        if let Some(s) = segments.optional("ADJ") {
                            grp_psl_item_info.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_product_service_group.push_group(grp_psl_item_info);
                }
                grp_product_service_section.push_group(grp_product_service_group);
            }
            grp_payment_remittance_detail_info.push_group(grp_product_service_section);
        }
        msg.push_group(grp_payment_remittance_detail_info);
    }
    while segments.peek_matches_any(&["ADJ", "PRT", "ROL"]) {
        let mut grp_adjustment_payee = RawGroup::new("ADJUSTMENT_PAYEE");
        grp_adjustment_payee.push(RawSegment::from_tokens(&segments.expect("ADJ")?));
        if let Some(s) = segments.optional("PRT") {
            grp_adjustment_payee.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("ROL") {
            grp_adjustment_payee.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_adjustment_payee);
    }
    Ok(msg)
}
pub fn parse_ehc_e20(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E20");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_ehc_e21(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E21");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_ehc_e24(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("EHC_E24");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_esr_u02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ESR_U02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_esu_u01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ESU_U01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["ISD"]) {
        if let Some(s) = segments.optional("ISD") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_inr_u06(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("INR_U06");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    msg.push(RawSegment::from_tokens(&segments.expect("INV")?));
    while segments.peek_matches_any(&["INV"]) {
        if let Some(s) = segments.optional("INV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_inr_u14(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("INR_U14");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["INV"]) {
        if let Some(s) = segments.optional("INV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_inu_u05(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("INU_U05");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    msg.push(RawSegment::from_tokens(&segments.expect("INV")?));
    while segments.peek_matches_any(&["INV"]) {
        if let Some(s) = segments.optional("INV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_lsu_u12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("LSU_U12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    msg.push(RawSegment::from_tokens(&segments.expect("EQP")?));
    while segments.peek_matches_any(&["EQP"]) {
        if let Some(s) = segments.optional("EQP") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_mdm_t01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MDM_T01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE", "OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_common_order = RawGroup::new("COMMON_ORDER");
        grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_timing);
        }
        grp_common_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_common_order);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("TXA")?));
    while segments.peek_matches_any(&["CON"]) {
        if let Some(s) = segments.optional("CON") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_mdm_t02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MDM_T02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE", "OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_common_order = RawGroup::new("COMMON_ORDER");
        grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_common_order.push_group(grp_timing);
        }
        grp_common_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_common_order);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("TXA")?));
    while segments.peek_matches_any(&["CON"]) {
        if let Some(s) = segments.optional("CON") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    Ok(msg)
}
pub fn parse_mfk_m01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFK_M01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFA"]) {
        if let Some(s) = segments.optional("MFA") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_mfn_m02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["AFF", "CER", "EDU", "LAN", "MFE", "NTE", "ORG", "PRA", "STF"]) {
        let mut grp_mf_staff = RawGroup::new("MF_STAFF");
        grp_mf_staff.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_staff.push(RawSegment::from_tokens(&segments.expect("STF")?));
        while segments.peek_matches_any(&["PRA"]) {
            if let Some(s) = segments.optional("PRA") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ORG"]) {
            if let Some(s) = segments.optional("ORG") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AFF"]) {
            if let Some(s) = segments.optional("AFF") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["LAN"]) {
            if let Some(s) = segments.optional("LAN") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["EDU"]) {
            if let Some(s) = segments.optional("EDU") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CER"]) {
            if let Some(s) = segments.optional("CER") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_mf_staff.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_mf_staff);
    }
    Ok(msg)
}
pub fn parse_mfn_m04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CDM", "MFE", "NTE", "PRC"]) {
        let mut grp_mf_cdm = RawGroup::new("MF_CDM");
        grp_mf_cdm.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_mf_cdm.push(RawSegment::from_tokens(&s));
            }
        }
        grp_mf_cdm.push(RawSegment::from_tokens(&segments.expect("CDM")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_mf_cdm.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRC"]) {
            if let Some(s) = segments.optional("PRC") {
                grp_mf_cdm.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_mf_cdm);
    }
    Ok(msg)
}
pub fn parse_mfn_m05(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M05");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["LCC", "LCH", "LDP", "LOC", "LRL", "MFE"]) {
        let mut grp_mf_location = RawGroup::new("MF_LOCATION");
        grp_mf_location.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_location.push(RawSegment::from_tokens(&segments.expect("LOC")?));
        while segments.peek_matches_any(&["LCH"]) {
            if let Some(s) = segments.optional("LCH") {
                grp_mf_location.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["LRL"]) {
            if let Some(s) = segments.optional("LRL") {
                grp_mf_location.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["LCC", "LCH", "LDP"]) {
            let mut grp_mf_loc_dept = RawGroup::new("MF_LOC_DEPT");
            grp_mf_loc_dept.push(RawSegment::from_tokens(&segments.expect("LDP")?));
            while segments.peek_matches_any(&["LCH"]) {
                if let Some(s) = segments.optional("LCH") {
                    grp_mf_loc_dept.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["LCC"]) {
                if let Some(s) = segments.optional("LCC") {
                    grp_mf_loc_dept.push(RawSegment::from_tokens(&s));
                }
            }
            grp_mf_location.push_group(grp_mf_loc_dept);
        }
        msg.push_group(grp_mf_location);
    }
    Ok(msg)
}
pub fn parse_mfn_m06(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M06");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["CM0", "CM1", "CM2", "MFE"]) {
        let mut grp_mf_clin_study = RawGroup::new("MF_CLIN_STUDY");
        grp_mf_clin_study.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_clin_study.push(RawSegment::from_tokens(&segments.expect("CM0")?));
        while segments.peek_matches_any(&["CM1", "CM2"]) {
            let mut grp_mf_phase_sched_detail = RawGroup::new("MF_PHASE_SCHED_DETAIL");
            grp_mf_phase_sched_detail.push(RawSegment::from_tokens(&segments.expect("CM1")?));
            while segments.peek_matches_any(&["CM2"]) {
                if let Some(s) = segments.optional("CM2") {
                    grp_mf_phase_sched_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_mf_clin_study.push_group(grp_mf_phase_sched_detail);
        }
        msg.push_group(grp_mf_clin_study);
    }
    Ok(msg)
}
pub fn parse_mfn_m07(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M07");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["CM0", "CM2", "MFE"]) {
        let mut grp_mf_clin_study_sched = RawGroup::new("MF_CLIN_STUDY_SCHED");
        grp_mf_clin_study_sched.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_clin_study_sched.push(RawSegment::from_tokens(&segments.expect("CM0")?));
        while segments.peek_matches_any(&["CM2"]) {
            if let Some(s) = segments.optional("CM2") {
                grp_mf_clin_study_sched.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_mf_clin_study_sched);
    }
    Ok(msg)
}
pub fn parse_mfn_m08(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M08");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFE", "OM1", "OM2", "OM3", "OM4", "OMC", "PRT"]) {
        let mut grp_mf_test_numeric = RawGroup::new("MF_TEST_NUMERIC");
        grp_mf_test_numeric.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_test_numeric.push(RawSegment::from_tokens(&segments.expect("OM1")?));
        while segments.peek_matches_any(&["OMC"]) {
            if let Some(s) = segments.optional("OMC") {
                grp_mf_test_numeric.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_mf_test_numeric.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OM2") {
            grp_mf_test_numeric.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("OM3") {
            grp_mf_test_numeric.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["OM4"]) {
            if let Some(s) = segments.optional("OM4") {
                grp_mf_test_numeric.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_mf_test_numeric);
    }
    Ok(msg)
}
pub fn parse_mfn_m09(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M09");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFE", "OM1", "OM3", "OM4", "OMC", "PRT"]) {
        let mut grp_mf_test_categorical = RawGroup::new("MF_TEST_CATEGORICAL");
        grp_mf_test_categorical.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_test_categorical.push(RawSegment::from_tokens(&segments.expect("OM1")?));
        while segments.peek_matches_any(&["OMC"]) {
            if let Some(s) = segments.optional("OMC") {
                grp_mf_test_categorical.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_mf_test_categorical.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OM3", "OM4"]) {
            let mut grp_mf_test_cat_detail = RawGroup::new("MF_TEST_CAT_DETAIL");
            grp_mf_test_cat_detail.push(RawSegment::from_tokens(&segments.expect("OM3")?));
            while segments.peek_matches_any(&["OM4"]) {
                if let Some(s) = segments.optional("OM4") {
                    grp_mf_test_cat_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_mf_test_categorical.push_group(grp_mf_test_cat_detail);
        }
        msg.push_group(grp_mf_test_categorical);
    }
    Ok(msg)
}
pub fn parse_mfn_m10(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M10");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFE", "OM1", "OM4", "OM5", "OMC", "PRT"]) {
        let mut grp_mf_test_batteries = RawGroup::new("MF_TEST_BATTERIES");
        grp_mf_test_batteries.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_test_batteries.push(RawSegment::from_tokens(&segments.expect("OM1")?));
        while segments.peek_matches_any(&["OMC"]) {
            if let Some(s) = segments.optional("OMC") {
                grp_mf_test_batteries.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_mf_test_batteries.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OM4", "OM5"]) {
            let mut grp_mf_test_batt_detail = RawGroup::new("MF_TEST_BATT_DETAIL");
            grp_mf_test_batt_detail.push(RawSegment::from_tokens(&segments.expect("OM5")?));
            while segments.peek_matches_any(&["OM4"]) {
                if let Some(s) = segments.optional("OM4") {
                    grp_mf_test_batt_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_mf_test_batteries.push_group(grp_mf_test_batt_detail);
        }
        msg.push_group(grp_mf_test_batteries);
    }
    Ok(msg)
}
pub fn parse_mfn_m11(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M11");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFE", "OM1", "OM2", "OM6", "OMC", "PRT"]) {
        let mut grp_mf_test_calculated = RawGroup::new("MF_TEST_CALCULATED");
        grp_mf_test_calculated.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_test_calculated.push(RawSegment::from_tokens(&segments.expect("OM1")?));
        while segments.peek_matches_any(&["OMC"]) {
            if let Some(s) = segments.optional("OMC") {
                grp_mf_test_calculated.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_mf_test_calculated.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OM2", "OM6"]) {
            let mut grp_mf_test_calc_detail = RawGroup::new("MF_TEST_CALC_DETAIL");
            grp_mf_test_calc_detail.push(RawSegment::from_tokens(&segments.expect("OM6")?));
            grp_mf_test_calc_detail.push(RawSegment::from_tokens(&segments.expect("OM2")?));
            grp_mf_test_calculated.push_group(grp_mf_test_calc_detail);
        }
        msg.push_group(grp_mf_test_calculated);
    }
    Ok(msg)
}
pub fn parse_mfn_m12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFE", "OM1", "OM7", "PRT"]) {
        let mut grp_mf_obs_attributes = RawGroup::new("MF_OBS_ATTRIBUTES");
        grp_mf_obs_attributes.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_obs_attributes.push(RawSegment::from_tokens(&segments.expect("OM1")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_mf_obs_attributes.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OM7", "PRT"]) {
            let mut grp_mf_obs_other_attributes = RawGroup::new("MF_OBS_OTHER_ATTRIBUTES");
            grp_mf_obs_other_attributes.push(RawSegment::from_tokens(&segments.expect("OM7")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_mf_obs_other_attributes.push(RawSegment::from_tokens(&s));
                }
            }
            grp_mf_obs_attributes.push_group(grp_mf_obs_other_attributes);
        }
        msg.push_group(grp_mf_obs_attributes);
    }
    Ok(msg)
}
pub fn parse_mfn_m13(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M13");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MFE")?));
    while segments.peek_matches_any(&["MFE"]) {
        if let Some(s) = segments.optional("MFE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_mfn_m15(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M15");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["IIM", "MFE"]) {
        let mut grp_mf_inv_item = RawGroup::new("MF_INV_ITEM");
        grp_mf_inv_item.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_inv_item.push(RawSegment::from_tokens(&segments.expect("IIM")?));
        msg.push_group(grp_mf_inv_item);
    }
    Ok(msg)
}
pub fn parse_mfn_m16(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M16");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["ILT", "ITM", "IVT", "MFE", "NTE", "PCE", "PKG", "STZ", "VND"]) {
        let mut grp_material_item_record = RawGroup::new("MATERIAL_ITEM_RECORD");
        grp_material_item_record.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_material_item_record.push(RawSegment::from_tokens(&segments.expect("ITM")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_material_item_record.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "STZ"]) {
            let mut grp_sterilization = RawGroup::new("STERILIZATION");
            grp_sterilization.push(RawSegment::from_tokens(&segments.expect("STZ")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_sterilization.push(RawSegment::from_tokens(&s));
                }
            }
            grp_material_item_record.push_group(grp_sterilization);
        }
        while segments.peek_matches_any(&["PCE", "PKG", "VND"]) {
            let mut grp_purchasing_vendor = RawGroup::new("PURCHASING_VENDOR");
            grp_purchasing_vendor.push(RawSegment::from_tokens(&segments.expect("VND")?));
            while segments.peek_matches_any(&["PCE", "PKG"]) {
                let mut grp_packaging = RawGroup::new("PACKAGING");
                grp_packaging.push(RawSegment::from_tokens(&segments.expect("PKG")?));
                while segments.peek_matches_any(&["PCE"]) {
                    if let Some(s) = segments.optional("PCE") {
                        grp_packaging.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_purchasing_vendor.push_group(grp_packaging);
            }
            grp_material_item_record.push_group(grp_purchasing_vendor);
        }
        while segments.peek_matches_any(&["ILT", "IVT", "NTE"]) {
            let mut grp_material_location = RawGroup::new("MATERIAL_LOCATION");
            grp_material_location.push(RawSegment::from_tokens(&segments.expect("IVT")?));
            while segments.peek_matches_any(&["ILT"]) {
                if let Some(s) = segments.optional("ILT") {
                    grp_material_location.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_material_location.push(RawSegment::from_tokens(&s));
                }
            }
            grp_material_item_record.push_group(grp_material_location);
        }
        msg.push_group(grp_material_item_record);
    }
    Ok(msg)
}
pub fn parse_mfn_m17(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M17");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["DMI", "MFE"]) {
        let mut grp_mf_drg = RawGroup::new("MF_DRG");
        grp_mf_drg.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_drg.push(RawSegment::from_tokens(&segments.expect("DMI")?));
        msg.push_group(grp_mf_drg);
    }
    Ok(msg)
}
pub fn parse_mfn_m18(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M18");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["DPS", "MCP", "MFE", "PM1"]) {
        let mut grp_mf_payer = RawGroup::new("MF_PAYER");
        grp_mf_payer.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        while segments.peek_matches_any(&["DPS", "MCP", "PM1"]) {
            let mut grp_payer_mf_entry = RawGroup::new("PAYER_MF_ENTRY");
            grp_payer_mf_entry.push(RawSegment::from_tokens(&segments.expect("PM1")?));
            while segments.peek_matches_any(&["DPS", "MCP"]) {
                let mut grp_payer_mf_coverage = RawGroup::new("PAYER_MF_COVERAGE");
                grp_payer_mf_coverage.push(RawSegment::from_tokens(&segments.expect("MCP")?));
                while segments.peek_matches_any(&["DPS"]) {
                    if let Some(s) = segments.optional("DPS") {
                        grp_payer_mf_coverage.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_payer_mf_entry.push_group(grp_payer_mf_coverage);
            }
            grp_mf_payer.push_group(grp_payer_mf_entry);
        }
        msg.push_group(grp_mf_payer);
    }
    Ok(msg)
}
pub fn parse_mfn_m19(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_M19");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["CTR", "ITM", "MFE", "NTE", "PKG", "VND"]) {
        let mut grp_contract_record = RawGroup::new("CONTRACT_RECORD");
        grp_contract_record.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_contract_record.push(RawSegment::from_tokens(&segments.expect("CTR")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_contract_record.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ITM", "PKG", "VND"]) {
            let mut grp_material_item_record = RawGroup::new("MATERIAL_ITEM_RECORD");
            grp_material_item_record.push(RawSegment::from_tokens(&segments.expect("ITM")?));
            while segments.peek_matches_any(&["PKG", "VND"]) {
                let mut grp_purchasing_vendor = RawGroup::new("PURCHASING_VENDOR");
                grp_purchasing_vendor.push(RawSegment::from_tokens(&segments.expect("VND")?));
                while segments.peek_matches_any(&["PKG"]) {
                    let mut grp_packaging = RawGroup::new("PACKAGING");
                    grp_packaging.push(RawSegment::from_tokens(&segments.expect("PKG")?));
                    grp_purchasing_vendor.push_group(grp_packaging);
                }
                grp_material_item_record.push_group(grp_purchasing_vendor);
            }
            grp_contract_record.push_group(grp_material_item_record);
        }
        msg.push_group(grp_contract_record);
    }
    Ok(msg)
}
pub fn parse_mfn_znn(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("MFN_Znn");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MFI")?));
    while segments.peek_matches_any(&["MFE", "anyHL7Segment"]) {
        let mut grp_mf_site_defined = RawGroup::new("MF_SITE_DEFINED");
        grp_mf_site_defined.push(RawSegment::from_tokens(&segments.expect("MFE")?));
        grp_mf_site_defined.push(RawSegment::from_tokens(&segments.expect("anyHL7Segment")?));
        msg.push_group(grp_mf_site_defined);
    }
    Ok(msg)
}
pub fn parse_nmd_n02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("NMD_N02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NCK", "NSC", "NST", "NTE"]) {
        let mut grp_clock_and_stats_with_notes = RawGroup::new("CLOCK_AND_STATS_WITH_NOTES");
        if segments.peek_matches_any(&["NCK", "NTE"]) {
            let mut grp_clock = RawGroup::new("CLOCK");
            grp_clock.push(RawSegment::from_tokens(&segments.expect("NCK")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_clock.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clock_and_stats_with_notes.push_group(grp_clock);
        }
        if segments.peek_matches_any(&["NST", "NTE"]) {
            let mut grp_app_stats = RawGroup::new("APP_STATS");
            grp_app_stats.push(RawSegment::from_tokens(&segments.expect("NST")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_app_stats.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clock_and_stats_with_notes.push_group(grp_app_stats);
        }
        if segments.peek_matches_any(&["NSC", "NTE"]) {
            let mut grp_app_status = RawGroup::new("APP_STATUS");
            grp_app_status.push(RawSegment::from_tokens(&segments.expect("NSC")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_app_status.push(RawSegment::from_tokens(&s));
                }
            }
            grp_clock_and_stats_with_notes.push_group(grp_app_status);
        }
        msg.push_group(grp_clock_and_stats_with_notes);
    }
    Ok(msg)
}
pub fn parse_omb_o27(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMB_O27");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "BPO", "DG1", "FT1", "NTE", "OBX", "ORC", "PRT", "SPM", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("BPO")?));
        if let Some(s) = segments.optional("SPM") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DG1"]) {
            if let Some(s) = segments.optional("DG1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_omd_o03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMD_O03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NTE", "OBX", "ODS", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_order_diet = RawGroup::new("ORDER_DIET");
        grp_order_diet.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order_diet.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_diet = RawGroup::new("TIMING_DIET");
            grp_timing_diet.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_diet.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order_diet.push_group(grp_timing_diet);
        }
        if segments.peek_matches_any(&["NTE", "OBX", "ODS", "PRT"]) {
            let mut grp_diet = RawGroup::new("DIET");
            grp_diet.push(RawSegment::from_tokens(&segments.expect("ODS")?));
            while segments.peek_matches_any(&["ODS"]) {
                if let Some(s) = segments.optional("ODS") {
                    grp_diet.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_diet.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_diet.push_group(grp_observation);
            }
            grp_order_diet.push_group(grp_diet);
        }
        msg.push_group(grp_order_diet);
    }
    while segments.peek_matches_any(&["NTE", "ODT", "ORC", "PRT", "TQ1", "TQ2"]) {
        let mut grp_order_tray = RawGroup::new("ORDER_TRAY");
        grp_order_tray.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order_tray.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_tray = RawGroup::new("TIMING_TRAY");
            grp_timing_tray.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_tray.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order_tray.push_group(grp_timing_tray);
        }
        grp_order_tray.push(RawSegment::from_tokens(&segments.expect("ODT")?));
        while segments.peek_matches_any(&["ODT"]) {
            if let Some(s) = segments.optional("ODT") {
                grp_order_tray.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order_tray.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order_tray);
    }
    Ok(msg)
}
pub fn parse_omg_o19(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMG_O19");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OH1", "OH2", "OH3", "OH4"]) {
            let mut grp_occupational_data_for_health = RawGroup::new("OCCUPATIONAL_DATA_FOR_HEALTH");
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_occupational_data_for_health);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
            let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
            grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_next_of_kin.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_next_of_kin);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTD", "CTI", "DEV", "DG1", "FT1", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("CTD") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["DG1"]) {
            if let Some(s) = segments.optional("DG1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("REL") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC", "SPM"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC"]) {
                let mut grp_container = RawGroup::new("CONTAINER");
                grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_container.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_container_observation = RawGroup::new("CONTAINER_OBSERVATION");
                    grp_container_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_container_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_container.push_group(grp_container_observation);
                }
                grp_specimen.push_group(grp_container);
            }
            grp_order.push_group(grp_specimen);
        }
        if let Some(s) = segments.optional("SGH") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1", "ARV", "CTD", "DEV", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
            let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
            if segments.peek_matches_any(&["ARV", "PD1", "PID", "PRT"]) {
                let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                if let Some(s) = segments.optional("PD1") {
                    grp_patient_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["ARV"]) {
                    if let Some(s) = segments.optional("ARV") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_prior_result.push_group(grp_patient_prior);
            }
            if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_prior_result.push_group(grp_patient_visit_prior);
            }
            while segments.peek_matches_any(&["AL1"]) {
                if let Some(s) = segments.optional("AL1") {
                    grp_prior_result.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CTD", "DEV", "NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                grp_order_prior.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_prior = RawGroup::new("TIMING_PRIOR");
                    grp_timing_prior.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_timing_prior);
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["DEV", "PRT"]) {
                    let mut grp_order_detail_participation_prior = RawGroup::new("ORDER_DETAIL_PARTICIPATION_PRIOR");
                    grp_order_detail_participation_prior.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                    while segments.peek_matches_any(&["DEV"]) {
                        if let Some(s) = segments.optional("DEV") {
                            grp_order_detail_participation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_order_detail_participation_prior);
                }
                if let Some(s) = segments.optional("CTD") {
                    grp_order_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                    let mut grp_observation_prior = RawGroup::new("OBSERVATION_PRIOR");
                    grp_observation_prior.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_observation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_observation_prior);
                }
                grp_prior_result.push_group(grp_order_prior);
            }
            grp_order.push_group(grp_prior_result);
        }
        if let Some(s) = segments.optional("SGT") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_omi_o23(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMI_O23");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OH1", "OH2", "OH3", "OH4"]) {
            let mut grp_occupational_data_for_health = RawGroup::new("OCCUPATIONAL_DATA_FOR_HEALTH");
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_occupational_data_for_health);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["CTD", "DG1", "IPC", "NTE", "OBR", "OBX", "ORC", "PRT", "REL", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("CTD") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["DG1"]) {
            if let Some(s) = segments.optional("DG1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("REL") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("IPC")?));
        while segments.peek_matches_any(&["IPC"]) {
            if let Some(s) = segments.optional("IPC") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_oml_o21(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OML_O21");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OH1", "OH2", "OH3", "OH4"]) {
            let mut grp_occupational_data_for_health = RawGroup::new("OCCUPATIONAL_DATA_FOR_HEALTH");
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_occupational_data_for_health);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
            let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
            grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_next_of_kin.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_next_of_kin);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTD", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["AL1", "ARV", "CTD", "DEV", "DG1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
            let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
            grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            if let Some(s) = segments.optional("TCD") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("CTD") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["DG1"]) {
                if let Some(s) = segments.optional("DG1") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("REL") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT", "TCD"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("TCD") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_observation_request.push_group(grp_observation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC", "SPM"]) {
                let mut grp_specimen = RawGroup::new("SPECIMEN");
                grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_specimen.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                    grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_specimen_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_specimen_observation);
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC"]) {
                    let mut grp_container = RawGroup::new("CONTAINER");
                    grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_container.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["OBX", "PRT"]) {
                        let mut grp_container_observation = RawGroup::new("CONTAINER_OBSERVATION");
                        grp_container_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_container_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_container.push_group(grp_container_observation);
                    }
                    grp_specimen.push_group(grp_container);
                }
                grp_observation_request.push_group(grp_specimen);
            }
            if let Some(s) = segments.optional("IPC") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("SGH") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["AL1", "ARV", "DEV", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
                let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
                if segments.peek_matches_any(&["ARV", "PD1", "PID", "PRT"]) {
                    let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                    grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                    if let Some(s) = segments.optional("PD1") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_patient_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["ARV"]) {
                        if let Some(s) = segments.optional("ARV") {
                            grp_patient_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_prior_result.push_group(grp_patient_prior);
                }
                if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                    let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                    grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                    if let Some(s) = segments.optional("PV2") {
                        grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_prior_result.push_group(grp_patient_visit_prior);
                }
                while segments.peek_matches_any(&["AL1"]) {
                    if let Some(s) = segments.optional("AL1") {
                        grp_prior_result.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["DEV", "NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                    let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                    grp_order_prior.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_order_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["DEV", "PRT"]) {
                        let mut grp_observation_participation_prior = RawGroup::new("OBSERVATION_PARTICIPATION_PRIOR");
                        grp_observation_participation_prior.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                        while segments.peek_matches_any(&["DEV"]) {
                            if let Some(s) = segments.optional("DEV") {
                                grp_observation_participation_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push_group(grp_observation_participation_prior);
                    }
                    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                        let mut grp_timing_prior = RawGroup::new("TIMING_PRIOR");
                        grp_timing_prior.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                        while segments.peek_matches_any(&["TQ2"]) {
                            if let Some(s) = segments.optional("TQ2") {
                                grp_timing_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push_group(grp_timing_prior);
                    }
                    while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                        let mut grp_observation_prior = RawGroup::new("OBSERVATION_PRIOR");
                        grp_observation_prior.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_observation_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_observation_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push_group(grp_observation_prior);
                    }
                    grp_prior_result.push_group(grp_order_prior);
                }
                grp_observation_request.push_group(grp_prior_result);
            }
            if let Some(s) = segments.optional("SGT") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            grp_order.push_group(grp_observation_request);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_oml_o33(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OML_O33");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OH1", "OH2", "OH3", "OH4"]) {
            let mut grp_occupational_data_for_health = RawGroup::new("OCCUPATIONAL_DATA_FOR_HEALTH");
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_occupational_data_for_health);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
            let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
            grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_next_of_kin.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_next_of_kin);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
        let mut grp_specimen = RawGroup::new("SPECIMEN");
        grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_specimen.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
            grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_specimen_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen.push_group(grp_specimen_observation);
        }
        while segments.peek_matches_any(&["NTE", "SAC"]) {
            let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
            grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_specimen_container.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen.push_group(grp_specimen_container);
        }
        while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SGH", "SGT", "TCD", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["AL1", "ARV", "DEV", "DG1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SGH", "SGT", "TCD", "TQ1", "TQ2"]) {
                let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                if let Some(s) = segments.optional("TCD") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["DG1"]) {
                    if let Some(s) = segments.optional("DG1") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("REL") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT", "TCD"]) {
                    let mut grp_observation = RawGroup::new("OBSERVATION");
                    grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    if let Some(s) = segments.optional("TCD") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_observation_request.push_group(grp_observation);
                }
                if let Some(s) = segments.optional("IPC") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
                if let Some(s) = segments.optional("SGH") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["AL1", "ARV", "DEV", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
                    let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
                    if segments.peek_matches_any(&["ARV", "PD1", "PID", "PRT"]) {
                        let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                        grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                        if let Some(s) = segments.optional("PD1") {
                            grp_patient_prior.push(RawSegment::from_tokens(&s));
                        }
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_patient_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["ARV"]) {
                            if let Some(s) = segments.optional("ARV") {
                                grp_patient_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_prior_result.push_group(grp_patient_prior);
                    }
                    if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                        let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                        grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                        if let Some(s) = segments.optional("PV2") {
                            grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                        }
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_prior_result.push_group(grp_patient_visit_prior);
                    }
                    while segments.peek_matches_any(&["AL1"]) {
                        if let Some(s) = segments.optional("AL1") {
                            grp_prior_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["DEV", "NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                        let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                        grp_order_prior.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_order_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_order_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["DEV", "PRT"]) {
                            let mut grp_observation_participation_prior = RawGroup::new("OBSERVATION_PARTICIPATION_PRIOR");
                            grp_observation_participation_prior.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                            while segments.peek_matches_any(&["DEV"]) {
                                if let Some(s) = segments.optional("DEV") {
                                    grp_observation_participation_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_order_prior.push_group(grp_observation_participation_prior);
                        }
                        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                            let mut grp_timing_prior = RawGroup::new("TIMING_PRIOR");
                            grp_timing_prior.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                            while segments.peek_matches_any(&["TQ2"]) {
                                if let Some(s) = segments.optional("TQ2") {
                                    grp_timing_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_order_prior.push_group(grp_timing_prior);
                        }
                        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                            let mut grp_observation_prior = RawGroup::new("OBSERVATION_PRIOR");
                            grp_observation_prior.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                            while segments.peek_matches_any(&["PRT"]) {
                                if let Some(s) = segments.optional("PRT") {
                                    grp_observation_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            while segments.peek_matches_any(&["NTE"]) {
                                if let Some(s) = segments.optional("NTE") {
                                    grp_observation_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_order_prior.push_group(grp_observation_prior);
                        }
                        grp_prior_result.push_group(grp_order_prior);
                    }
                    grp_observation_request.push_group(grp_prior_result);
                }
                if let Some(s) = segments.optional("SGT") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
                grp_order.push_group(grp_observation_request);
            }
            while segments.peek_matches_any(&["FT1"]) {
                if let Some(s) = segments.optional("FT1") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CTI"]) {
                if let Some(s) = segments.optional("CTI") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("BLG") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
            grp_specimen.push_group(grp_order);
        }
        msg.push_group(grp_specimen);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_oml_o35(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OML_O35");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OH1", "OH2", "OH3", "OH4"]) {
            let mut grp_occupational_data_for_health = RawGroup::new("OCCUPATIONAL_DATA_FOR_HEALTH");
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_occupational_data_for_health);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
            let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
            grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_next_of_kin.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_next_of_kin);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
        let mut grp_specimen = RawGroup::new("SPECIMEN");
        grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_specimen.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
            grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_specimen_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen.push_group(grp_specimen_observation);
        }
        while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "TCD", "TQ1", "TQ2"]) {
            let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
            grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_specimen_container.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SGH", "SGT", "TCD", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing);
                }
                if segments.peek_matches_any(&["AL1", "ARV", "DEV", "DG1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SGH", "SGT", "TCD", "TQ1", "TQ2"]) {
                    let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                    grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    if let Some(s) = segments.optional("TCD") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["DG1"]) {
                        if let Some(s) = segments.optional("DG1") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    if let Some(s) = segments.optional("REL") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["NTE", "OBX", "PRT", "TCD"]) {
                        let mut grp_observation = RawGroup::new("OBSERVATION");
                        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        if let Some(s) = segments.optional("TCD") {
                            grp_observation.push(RawSegment::from_tokens(&s));
                        }
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_observation_request.push_group(grp_observation);
                    }
                    if let Some(s) = segments.optional("IPC") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                    if let Some(s) = segments.optional("SGH") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["AL1", "ARV", "DEV", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
                        let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
                        if segments.peek_matches_any(&["ARV", "PD1", "PID", "PRT"]) {
                            let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                            grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                            if let Some(s) = segments.optional("PD1") {
                                grp_patient_prior.push(RawSegment::from_tokens(&s));
                            }
                            while segments.peek_matches_any(&["PRT"]) {
                                if let Some(s) = segments.optional("PRT") {
                                    grp_patient_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            while segments.peek_matches_any(&["ARV"]) {
                                if let Some(s) = segments.optional("ARV") {
                                    grp_patient_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_prior_result.push_group(grp_patient_prior);
                        }
                        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                            let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                            grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                            if let Some(s) = segments.optional("PV2") {
                                grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                            }
                            while segments.peek_matches_any(&["PRT"]) {
                                if let Some(s) = segments.optional("PRT") {
                                    grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_prior_result.push_group(grp_patient_visit_prior);
                        }
                        while segments.peek_matches_any(&["AL1"]) {
                            if let Some(s) = segments.optional("AL1") {
                                grp_prior_result.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["DEV", "NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                            let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                            grp_order_prior.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                            while segments.peek_matches_any(&["PRT"]) {
                                if let Some(s) = segments.optional("PRT") {
                                    grp_order_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                            while segments.peek_matches_any(&["NTE"]) {
                                if let Some(s) = segments.optional("NTE") {
                                    grp_order_prior.push(RawSegment::from_tokens(&s));
                                }
                            }
                            while segments.peek_matches_any(&["DEV", "PRT"]) {
                                let mut grp_observation_participation = RawGroup::new("OBSERVATION_PARTICIPATION");
                                grp_observation_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                                while segments.peek_matches_any(&["DEV"]) {
                                    if let Some(s) = segments.optional("DEV") {
                                        grp_observation_participation.push(RawSegment::from_tokens(&s));
                                    }
                                }
                                grp_order_prior.push_group(grp_observation_participation);
                            }
                            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                                let mut grp_timing_prior = RawGroup::new("TIMING_PRIOR");
                                grp_timing_prior.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                                while segments.peek_matches_any(&["TQ2"]) {
                                    if let Some(s) = segments.optional("TQ2") {
                                        grp_timing_prior.push(RawSegment::from_tokens(&s));
                                    }
                                }
                                grp_order_prior.push_group(grp_timing_prior);
                            }
                            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                                let mut grp_observation_prior = RawGroup::new("OBSERVATION_PRIOR");
                                grp_observation_prior.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                                while segments.peek_matches_any(&["PRT"]) {
                                    if let Some(s) = segments.optional("PRT") {
                                        grp_observation_prior.push(RawSegment::from_tokens(&s));
                                    }
                                }
                                while segments.peek_matches_any(&["NTE"]) {
                                    if let Some(s) = segments.optional("NTE") {
                                        grp_observation_prior.push(RawSegment::from_tokens(&s));
                                    }
                                }
                                grp_order_prior.push_group(grp_observation_prior);
                            }
                            grp_prior_result.push_group(grp_order_prior);
                        }
                        grp_observation_request.push_group(grp_prior_result);
                    }
                    if let Some(s) = segments.optional("SGT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                    grp_order.push_group(grp_observation_request);
                }
                while segments.peek_matches_any(&["FT1"]) {
                    if let Some(s) = segments.optional("FT1") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["CTI"]) {
                    if let Some(s) = segments.optional("CTI") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("BLG") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
                grp_specimen_container.push_group(grp_order);
            }
            grp_specimen.push_group(grp_specimen_container);
        }
        msg.push_group(grp_specimen);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_oml_o39(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OML_O39");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OH1", "OH2", "OH3", "OH4"]) {
            let mut grp_occupational_data_for_health = RawGroup::new("OCCUPATIONAL_DATA_FOR_HEALTH");
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_occupational_data_for_health.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_occupational_data_for_health);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
            let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
            grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_next_of_kin.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_next_of_kin.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_next_of_kin);
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "CTD", "CTI", "DG1", "FT1", "NTE", "OBR", "OBX", "ORC", "PAC", "PRT", "REL", "SAC", "SHP", "SPM", "TCD", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["CTD", "DG1", "NTE", "OBR", "OBX", "PAC", "PRT", "REL", "SAC", "SHP", "SPM", "TCD"]) {
            let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
            grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            if let Some(s) = segments.optional("TCD") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("CTD") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["DG1"]) {
                if let Some(s) = segments.optional("DG1") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("REL") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT", "TCD"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("TCD") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_observation_request.push_group(grp_observation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PAC", "PRT", "SAC", "SHP", "SPM"]) {
                let mut grp_specimen_shipment = RawGroup::new("SPECIMEN_SHIPMENT");
                grp_specimen_shipment.push(RawSegment::from_tokens(&segments.expect("SHP")?));
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_shipment_observation = RawGroup::new("SHIPMENT_OBSERVATION");
                    grp_shipment_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_shipment_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen_shipment.push_group(grp_shipment_observation);
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PAC", "PRT", "SAC", "SPM"]) {
                    let mut grp_package = RawGroup::new("PACKAGE");
                    grp_package.push(RawSegment::from_tokens(&segments.expect("PAC")?));
                    while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC", "SPM"]) {
                        let mut grp_specimen_in_package = RawGroup::new("SPECIMEN_IN_PACKAGE");
                        grp_specimen_in_package.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_specimen_in_package.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["OBX", "PRT"]) {
                            let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                            grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                            while segments.peek_matches_any(&["PRT"]) {
                                if let Some(s) = segments.optional("PRT") {
                                    grp_specimen_observation.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_specimen_in_package.push_group(grp_specimen_observation);
                        }
                        while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC"]) {
                            let mut grp_specimen_container_in_package = RawGroup::new("SPECIMEN_CONTAINER_IN_PACKAGE");
                            grp_specimen_container_in_package.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                            while segments.peek_matches_any(&["NTE"]) {
                                if let Some(s) = segments.optional("NTE") {
                                    grp_specimen_container_in_package.push(RawSegment::from_tokens(&s));
                                }
                            }
                            while segments.peek_matches_any(&["OBX", "PRT"]) {
                                let mut grp_container_observation = RawGroup::new("CONTAINER_OBSERVATION");
                                grp_container_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                                while segments.peek_matches_any(&["PRT"]) {
                                    if let Some(s) = segments.optional("PRT") {
                                        grp_container_observation.push(RawSegment::from_tokens(&s));
                                    }
                                }
                                grp_specimen_container_in_package.push_group(grp_container_observation);
                            }
                            grp_specimen_in_package.push_group(grp_specimen_container_in_package);
                        }
                        grp_package.push_group(grp_specimen_in_package);
                    }
                    grp_specimen_shipment.push_group(grp_package);
                }
                grp_observation_request.push_group(grp_specimen_shipment);
            }
            grp_order.push_group(grp_observation_request);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_oml_o59(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OML_O59");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AL1", "BLG", "CTD", "CTI", "DEV", "DG1", "FT1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["AL1", "CTD", "DEV", "DG1", "IPC", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "REL", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
            let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
            grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            if let Some(s) = segments.optional("TCD") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("CTD") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["DG1"]) {
                if let Some(s) = segments.optional("DG1") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("REL") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT", "TCD"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("TCD") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_observation_request.push_group(grp_observation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC", "SPM"]) {
                let mut grp_specimen = RawGroup::new("SPECIMEN");
                grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_specimen.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                    grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_specimen_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_specimen_observation);
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC"]) {
                    let mut grp_container = RawGroup::new("CONTAINER");
                    grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_container.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["OBX", "PRT"]) {
                        let mut grp_container_observation = RawGroup::new("CONTAINER_OBSERVATION");
                        grp_container_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_container_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_container.push_group(grp_container_observation);
                    }
                    grp_specimen.push_group(grp_container);
                }
                grp_observation_request.push_group(grp_specimen);
            }
            if let Some(s) = segments.optional("IPC") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("SGH") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["AL1", "DEV", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
                let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
                if segments.peek_matches_any(&["PD1", "PID", "PRT"]) {
                    let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                    grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                    if let Some(s) = segments.optional("PD1") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_patient_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_prior_result.push_group(grp_patient_prior);
                }
                if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                    let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                    grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                    if let Some(s) = segments.optional("PV2") {
                        grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_prior_result.push_group(grp_patient_visit_prior);
                }
                while segments.peek_matches_any(&["AL1"]) {
                    if let Some(s) = segments.optional("AL1") {
                        grp_prior_result.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["DEV", "NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                    let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                    grp_order_prior.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_order_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["DEV", "PRT"]) {
                        let mut grp_observation_participation_prior = RawGroup::new("OBSERVATION_PARTICIPATION_PRIOR");
                        grp_observation_participation_prior.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                        while segments.peek_matches_any(&["DEV"]) {
                            if let Some(s) = segments.optional("DEV") {
                                grp_observation_participation_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push_group(grp_observation_participation_prior);
                    }
                    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                        let mut grp_timing_prior = RawGroup::new("TIMING_PRIOR");
                        grp_timing_prior.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                        while segments.peek_matches_any(&["TQ2"]) {
                            if let Some(s) = segments.optional("TQ2") {
                                grp_timing_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push_group(grp_timing_prior);
                    }
                    while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                        let mut grp_observation_prior = RawGroup::new("OBSERVATION_PRIOR");
                        grp_observation_prior.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_observation_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_observation_prior.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_prior.push_group(grp_observation_prior);
                    }
                    grp_prior_result.push_group(grp_order_prior);
                }
                grp_observation_request.push_group(grp_prior_result);
            }
            if let Some(s) = segments.optional("SGT") {
                grp_observation_request.push(RawSegment::from_tokens(&s));
            }
            grp_order.push_group(grp_observation_request);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_omn_o07(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMN_O07");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "NTE", "OBX", "ORC", "PRT", "RQ1", "RQD", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RQD")?));
        if let Some(s) = segments.optional("RQ1") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_omp_o09(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMP_O09");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if segments.peek_matches_any(&["PD1", "PRT"]) {
            let mut grp_additional_demographics = RawGroup::new("ADDITIONAL_DEMOGRAPHICS");
            grp_additional_demographics.push(RawSegment::from_tokens(&segments.expect("PD1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_additional_demographics.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_additional_demographics);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "CDO", "FT1", "NTE", "OBX", "ORC", "PRT", "RXC", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXO")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
        while segments.peek_matches_any(&["RXR"]) {
            if let Some(s) = segments.optional("RXR") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "RXC"]) {
            let mut grp_component = RawGroup::new("COMPONENT");
            grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_component.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_component);
        }
        while segments.peek_matches_any(&["CDO"]) {
            if let Some(s) = segments.optional("CDO") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_omq_o57(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMQ_O57");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NK1", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTD", "CTI", "DEV", "DG1", "FT1", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2", "TXA"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("TXA")?));
        if let Some(s) = segments.optional("CTD") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["DG1"]) {
            if let Some(s) = segments.optional("DG1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["AL1", "ARV", "CTD", "DEV", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
            let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
            if segments.peek_matches_any(&["ARV", "PD1", "PID", "PRT"]) {
                let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                if let Some(s) = segments.optional("PD1") {
                    grp_patient_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["ARV"]) {
                    if let Some(s) = segments.optional("ARV") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_prior_result.push_group(grp_patient_prior);
            }
            if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_prior_result.push_group(grp_patient_visit_prior);
            }
            while segments.peek_matches_any(&["AL1"]) {
                if let Some(s) = segments.optional("AL1") {
                    grp_prior_result.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CTD", "DEV", "NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                grp_order_prior.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_prior = RawGroup::new("TIMING_PRIOR");
                    grp_timing_prior.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_timing_prior);
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["DEV", "PRT"]) {
                    let mut grp_observation_participation_prior = RawGroup::new("OBSERVATION_PARTICIPATION_PRIOR");
                    grp_observation_participation_prior.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                    while segments.peek_matches_any(&["DEV"]) {
                        if let Some(s) = segments.optional("DEV") {
                            grp_observation_participation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_observation_participation_prior);
                }
                if let Some(s) = segments.optional("CTD") {
                    grp_order_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                    let mut grp_observation_prior = RawGroup::new("OBSERVATION_PRIOR");
                    grp_observation_prior.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_observation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_observation_prior);
                }
                grp_prior_result.push_group(grp_order_prior);
            }
            grp_order.push_group(grp_prior_result);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_oms_o05(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OMS_O05");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "NTE", "OBX", "ORC", "PRT", "RQ1", "RQD", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RQD")?));
        if let Some(s) = segments.optional("RQ1") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_opl_o37(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OPL_O37");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PRT")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["GT1", "NTE"]) {
        let mut grp_guarantor = RawGroup::new("GUARANTOR");
        grp_guarantor.push(RawSegment::from_tokens(&segments.expect("GT1")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_guarantor.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_guarantor);
    }
    while segments.peek_matches_any(&["AL1", "ARV", "BLG", "CTI", "DEV", "DG1", "FT1", "IN1", "IN2", "IN3", "NK1", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "SAC", "SGH", "SGT", "SPM", "TCD", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["AL1", "ARV", "IN1", "IN2", "IN3", "OBX", "PD1", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_observations_on_patient = RawGroup::new("OBSERVATIONS_ON_PATIENT");
                grp_observations_on_patient.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observations_on_patient.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_patient.push_group(grp_observations_on_patient);
            }
            while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
                let mut grp_insurance = RawGroup::new("INSURANCE");
                grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
                if let Some(s) = segments.optional("IN2") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
                if let Some(s) = segments.optional("IN3") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
                grp_patient.push_group(grp_insurance);
            }
            while segments.peek_matches_any(&["AL1"]) {
                if let Some(s) = segments.optional("AL1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["DG1", "OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TCD", "TQ1", "TQ2"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["OBX", "PRT", "SAC"]) {
                let mut grp_container = RawGroup::new("CONTAINER");
                grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_container_observation = RawGroup::new("CONTAINER_OBSERVATION");
                    grp_container_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_container_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_container.push_group(grp_container_observation);
                }
                grp_specimen.push_group(grp_container);
            }
            while segments.peek_matches_any(&["DG1", "OBR", "OBX", "ORC", "PRT", "TCD", "TQ1", "TQ2"]) {
                let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                grp_observation_request.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_observation_request.push_group(grp_timing);
                }
                if let Some(s) = segments.optional("TCD") {
                    grp_observation_request.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["DG1"]) {
                    if let Some(s) = segments.optional("DG1") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_order_related_observation = RawGroup::new("ORDER_RELATED_OBSERVATION");
                    grp_order_related_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_related_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_observation_request.push_group(grp_order_related_observation);
                }
                grp_specimen.push_group(grp_observation_request);
            }
            grp_order.push_group(grp_specimen);
        }
        if let Some(s) = segments.optional("SGH") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        if segments.peek_matches_any(&["AL1", "ARV", "DEV", "NK1", "OBR", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "TQ1", "TQ2"]) {
            let mut grp_prior_result = RawGroup::new("PRIOR_RESULT");
            grp_prior_result.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["NK1"]) {
                if let Some(s) = segments.optional("NK1") {
                    grp_prior_result.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["ARV", "PD1", "PID", "PRT"]) {
                let mut grp_patient_prior = RawGroup::new("PATIENT_PRIOR");
                grp_patient_prior.push(RawSegment::from_tokens(&segments.expect("PID")?));
                if let Some(s) = segments.optional("PD1") {
                    grp_patient_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["ARV"]) {
                    if let Some(s) = segments.optional("ARV") {
                        grp_patient_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_prior_result.push_group(grp_patient_prior);
            }
            if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                let mut grp_patient_visit_prior = RawGroup::new("PATIENT_VISIT_PRIOR");
                grp_patient_visit_prior.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_visit_prior.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_prior_result.push_group(grp_patient_visit_prior);
            }
            if let Some(s) = segments.optional("AL1") {
                grp_prior_result.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["DEV", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order_prior = RawGroup::new("ORDER_PRIOR");
                grp_order_prior.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                if let Some(s) = segments.optional("ORC") {
                    grp_order_prior.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["DEV", "PRT"]) {
                    let mut grp_observation_participation_prior = RawGroup::new("OBSERVATION_PARTICIPATION_PRIOR");
                    grp_observation_participation_prior.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                    while segments.peek_matches_any(&["DEV"]) {
                        if let Some(s) = segments.optional("DEV") {
                            grp_observation_participation_prior.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_observation_participation_prior);
                }
                if segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_timing);
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_observation_result_group = RawGroup::new("OBSERVATION_RESULT_GROUP");
                    grp_observation_result_group.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_result_group.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_prior.push_group(grp_observation_result_group);
                }
                grp_prior_result.push_group(grp_order_prior);
            }
            grp_order.push_group(grp_prior_result);
        }
        if let Some(s) = segments.optional("SGT") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_opr_o38(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OPR_O38");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "NK1", "OBR", "OBX", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        while segments.peek_matches_any(&["ARV", "NK1", "OBR", "OBX", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("NK1")?));
            while segments.peek_matches_any(&["NK1"]) {
                if let Some(s) = segments.optional("NK1") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["ARV", "PID", "PRT"]) {
                let mut grp_patient = RawGroup::new("PATIENT");
                grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["ARV"]) {
                    if let Some(s) = segments.optional("ARV") {
                        grp_patient.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_patient);
            }
            while segments.peek_matches_any(&["OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
                let mut grp_specimen = RawGroup::new("SPECIMEN");
                grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                    grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_specimen_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_specimen_observation);
                }
                while segments.peek_matches_any(&["SAC"]) {
                    if let Some(s) = segments.optional("SAC") {
                        grp_specimen.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBR", "ORC", "PRT"]) {
                    let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                    grp_observation_request.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_observation_request);
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_timing);
                }
                grp_order.push_group(grp_specimen);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_opu_r25(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OPU_R25");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("NTE") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PV1")?));
    if let Some(s) = segments.optional("PV2") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
        let mut grp_patient_visit_observation = RawGroup::new("PATIENT_VISIT_OBSERVATION");
        grp_patient_visit_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient_visit_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient_visit_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient_visit_observation);
    }
    while segments.peek_matches_any(&["ARV", "INV", "NK1", "NTE", "OBR", "OBX", "OH1", "OH2", "OH3", "OH4", "ORC", "PD1", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_accession_detail = RawGroup::new("ACCESSION_DETAIL");
        grp_accession_detail.push(RawSegment::from_tokens(&segments.expect("NK1")?));
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_accession_detail.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["ARV", "NTE", "OBX", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
                grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_patient_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_patient.push_group(grp_patient_observation);
            }
            grp_accession_detail.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["INV", "SAC"]) {
                let mut grp_container = RawGroup::new("CONTAINER");
                grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                if let Some(s) = segments.optional("INV") {
                    grp_container.push(RawSegment::from_tokens(&s));
                }
                grp_specimen.push_group(grp_container);
            }
            while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["ORC", "PRT"]) {
                    let mut grp_common_order = RawGroup::new("COMMON_ORDER");
                    grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_common_order.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_common_order);
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
                    grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_qty.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing_qty);
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                    let mut grp_result = RawGroup::new("RESULT");
                    grp_result.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_result);
                }
                grp_specimen.push_group(grp_order);
            }
            grp_accession_detail.push_group(grp_specimen);
        }
        msg.push_group(grp_accession_detail);
    }
    Ok(msg)
}
pub fn parse_ora_r33(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORA_R33");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ORC", "PRT"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_ora_r41(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORA_R41");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_orb_o28(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORB_O28");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "BPO", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "BPO", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["BPO", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing);
                }
                if let Some(s) = segments.optional("BPO") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
                grp_patient.push_group(grp_order);
            }
            grp_response.push_group(grp_patient);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_ord_o04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORD_O04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "NTE", "ODS", "ODT", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ODS", "ORC", "PRT", "TQ1", "TQ2"]) {
            let mut grp_order_diet = RawGroup::new("ORDER_DIET");
            grp_order_diet.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_diet.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_diet = RawGroup::new("TIMING_DIET");
                grp_timing_diet.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_diet.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_diet.push_group(grp_timing_diet);
            }
            while segments.peek_matches_any(&["ODS"]) {
                if let Some(s) = segments.optional("ODS") {
                    grp_order_diet.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order_diet.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order_diet);
        }
        while segments.peek_matches_any(&["NTE", "ODT", "ORC", "PRT", "TQ1", "TQ2"]) {
            let mut grp_order_tray = RawGroup::new("ORDER_TRAY");
            grp_order_tray.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_tray.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_tray = RawGroup::new("TIMING_TRAY");
                grp_timing_tray.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_tray.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_tray.push_group(grp_timing_tray);
            }
            while segments.peek_matches_any(&["ODT"]) {
                if let Some(s) = segments.optional("ODT") {
                    grp_order_tray.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order_tray.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order_tray);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_org_o20(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORG_O20");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "CTI", "NTE", "OBR", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["CTI", "NTE", "OBR", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "OBR", "PRT"]) {
                let mut grp_observation_group = RawGroup::new("OBSERVATION_GROUP");
                grp_observation_group.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_group.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation_group.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_observation_group);
            }
            while segments.peek_matches_any(&["CTI"]) {
                if let Some(s) = segments.optional("CTI") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["SAC", "SPM"]) {
                let mut grp_specimen = RawGroup::new("SPECIMEN");
                grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                while segments.peek_matches_any(&["SAC"]) {
                    if let Some(s) = segments.optional("SAC") {
                        grp_specimen.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_specimen);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_ori_o24(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORI_O24");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "IPC", "NTE", "OBR", "ORC", "PID", "PRT", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["IPC", "NTE", "OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("IPC")?));
            while segments.peek_matches_any(&["IPC"]) {
                if let Some(s) = segments.optional("IPC") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "OBR", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        grp_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBR", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["OBR", "PRT", "SAC", "SPM"]) {
                let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["SAC", "SPM"]) {
                    let mut grp_specimen = RawGroup::new("SPECIMEN");
                    grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                    while segments.peek_matches_any(&["SAC"]) {
                        if let Some(s) = segments.optional("SAC") {
                            grp_specimen.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_observation_request.push_group(grp_specimen);
                }
                grp_order.push_group(grp_observation_request);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o34(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O34");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "OBR", "OBX", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        grp_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["SAC"]) {
                if let Some(s) = segments.optional("SAC") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing);
                }
                if segments.peek_matches_any(&["OBR", "PRT"]) {
                    let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                    grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_observation_request);
                }
                grp_specimen.push_group(grp_order);
            }
            grp_response.push_group(grp_specimen);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o36(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O36");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "NTE", "OBR", "OBX", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        grp_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBR", "ORC", "PRT", "SAC", "TQ1", "TQ2"]) {
                let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
                grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                while segments.peek_matches_any(&["OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
                    let mut grp_order = RawGroup::new("ORDER");
                    grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                        let mut grp_timing = RawGroup::new("TIMING");
                        grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                        while segments.peek_matches_any(&["TQ2"]) {
                            if let Some(s) = segments.optional("TQ2") {
                                grp_timing.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order.push_group(grp_timing);
                    }
                    if segments.peek_matches_any(&["OBR", "PRT"]) {
                        let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                        grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_observation_request.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order.push_group(grp_observation_request);
                    }
                    grp_specimen_container.push_group(grp_order);
                }
                grp_specimen.push_group(grp_specimen_container);
            }
            grp_response.push_group(grp_specimen);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o40(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O40");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "OBR", "ORC", "PAC", "PID", "PRT", "SAC", "SHP", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "OBR", "ORC", "PAC", "PID", "PRT", "SAC", "SHP", "SPM", "TQ1", "TQ2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBR", "ORC", "PAC", "PRT", "SAC", "SHP", "SPM", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing);
                }
                if segments.peek_matches_any(&["OBR", "PAC", "PRT", "SAC", "SHP", "SPM"]) {
                    let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                    grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["PAC", "SAC", "SHP", "SPM"]) {
                        let mut grp_specimen_shipment = RawGroup::new("SPECIMEN_SHIPMENT");
                        grp_specimen_shipment.push(RawSegment::from_tokens(&segments.expect("SHP")?));
                        while segments.peek_matches_any(&["PAC", "SAC", "SPM"]) {
                            let mut grp_package = RawGroup::new("PACKAGE");
                            grp_package.push(RawSegment::from_tokens(&segments.expect("PAC")?));
                            while segments.peek_matches_any(&["SAC", "SPM"]) {
                                let mut grp_specimen_in_package = RawGroup::new("SPECIMEN_IN_PACKAGE");
                                grp_specimen_in_package.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                                while segments.peek_matches_any(&["SAC"]) {
                                    let mut grp_specimen_container_in_package = RawGroup::new("SPECIMEN_CONTAINER_IN_PACKAGE");
                                    grp_specimen_container_in_package.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                                    grp_specimen_in_package.push_group(grp_specimen_container_in_package);
                                }
                                grp_package.push_group(grp_specimen_in_package);
                            }
                            grp_specimen_shipment.push_group(grp_package);
                        }
                        grp_observation_request.push_group(grp_specimen_shipment);
                    }
                    grp_order.push_group(grp_observation_request);
                }
                grp_patient.push_group(grp_order);
            }
            grp_response.push_group(grp_patient);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o53(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O53");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["OBR", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["OBR", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["OBR", "PRT", "SAC", "SPM"]) {
                let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["SAC", "SPM"]) {
                    let mut grp_specimen = RawGroup::new("SPECIMEN");
                    grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                    while segments.peek_matches_any(&["SAC"]) {
                        if let Some(s) = segments.optional("SAC") {
                            grp_specimen.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_observation_request.push_group(grp_specimen);
                }
                grp_order.push_group(grp_observation_request);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o54(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O54");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["OBR", "OBX", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["SAC"]) {
                if let Some(s) = segments.optional("SAC") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing = RawGroup::new("TIMING");
                    grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing);
                }
                if segments.peek_matches_any(&["OBR", "PRT"]) {
                    let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                    grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation_request.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_observation_request);
                }
                grp_specimen.push_group(grp_order);
            }
            grp_response.push_group(grp_specimen);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o55(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O55");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PID", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SPM", "TQ1", "TQ2"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBR", "ORC", "PRT", "SAC", "TQ1", "TQ2"]) {
                let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
                grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                while segments.peek_matches_any(&["OBR", "ORC", "PRT", "TQ1", "TQ2"]) {
                    let mut grp_order = RawGroup::new("ORDER");
                    grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                        let mut grp_timing = RawGroup::new("TIMING");
                        grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                        while segments.peek_matches_any(&["TQ2"]) {
                            if let Some(s) = segments.optional("TQ2") {
                                grp_timing.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order.push_group(grp_timing);
                    }
                    if segments.peek_matches_any(&["OBR", "PRT"]) {
                        let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                        grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_observation_request.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order.push_group(grp_observation_request);
                    }
                    grp_specimen_container.push_group(grp_order);
                }
                grp_specimen.push_group(grp_specimen_container);
            }
            grp_response.push_group(grp_specimen);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orl_o56(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORL_O56");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["OBR", "ORC", "PAC", "PID", "PRT", "SAC", "SHP", "SPM", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["OBR", "ORC", "PAC", "PRT", "SAC", "SHP", "SPM", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["OBR", "PAC", "PRT", "SAC", "SHP", "SPM"]) {
                let mut grp_observation_request = RawGroup::new("OBSERVATION_REQUEST");
                grp_observation_request.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation_request.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PAC", "SAC", "SHP", "SPM"]) {
                    let mut grp_specimen_shipment = RawGroup::new("SPECIMEN_SHIPMENT");
                    grp_specimen_shipment.push(RawSegment::from_tokens(&segments.expect("SHP")?));
                    while segments.peek_matches_any(&["PAC", "SAC", "SPM"]) {
                        let mut grp_package = RawGroup::new("PACKAGE");
                        grp_package.push(RawSegment::from_tokens(&segments.expect("PAC")?));
                        while segments.peek_matches_any(&["SAC", "SPM"]) {
                            let mut grp_specimen_in_package = RawGroup::new("SPECIMEN_IN_PACKAGE");
                            grp_specimen_in_package.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                            while segments.peek_matches_any(&["SAC"]) {
                                let mut grp_specimen_container_in_package = RawGroup::new("SPECIMEN_CONTAINER_IN_PACKAGE");
                                grp_specimen_container_in_package.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                                grp_specimen_in_package.push_group(grp_specimen_container_in_package);
                            }
                            grp_package.push_group(grp_specimen_in_package);
                        }
                        grp_specimen_shipment.push_group(grp_package);
                    }
                    grp_observation_request.push_group(grp_specimen_shipment);
                }
                grp_order.push_group(grp_observation_request);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orn_o08(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORN_O08");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "NTE", "ORC", "PID", "PRT", "RQ1", "RQD", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT", "RQ1", "RQD", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("RQD")?));
            if let Some(s) = segments.optional("RQ1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_orp_o10(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORP_O10");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "ORC", "PID", "PRT", "RXC", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT", "RXC", "RXO", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_component = RawGroup::new("COMPONENT");
                    grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_component.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail.push_group(grp_component);
                }
                grp_order.push_group(grp_order_detail);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_ors_o06(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORS_O06");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "NTE", "ORC", "PID", "PRT", "RQ1", "RQD", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT", "RQ1", "RQD", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("RQD")?));
            if let Some(s) = segments.optional("RQ1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_oru_r01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORU_R01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV", "CTD", "CTI", "DEV", "FT1", "IN1", "IN2", "IN3", "NK1", "NTE", "OBR", "OBX", "OH1", "OH2", "OH3", "OH4", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "SPM", "TQ1", "TQ2", "TXA"]) {
        let mut grp_patient_result = RawGroup::new("PATIENT_RESULT");
        if segments.peek_matches_any(&["ARV", "IN1", "IN2", "IN3", "NK1", "NTE", "OBX", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH1"]) {
                if let Some(s) = segments.optional("OH1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OH2"]) {
                if let Some(s) = segments.optional("OH2") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("OH3") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["OH4"]) {
                if let Some(s) = segments.optional("OH4") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NK1", "OH2", "OH3"]) {
                let mut grp_next_of_kin = RawGroup::new("NEXT_OF_KIN");
                grp_next_of_kin.push(RawSegment::from_tokens(&segments.expect("NK1")?));
                while segments.peek_matches_any(&["OH2"]) {
                    if let Some(s) = segments.optional("OH2") {
                        grp_next_of_kin.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("OH3") {
                    grp_next_of_kin.push(RawSegment::from_tokens(&s));
                }
                grp_patient.push_group(grp_next_of_kin);
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
                grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_patient.push_group(grp_patient_observation);
            }
            if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
                let mut grp_visit = RawGroup::new("VISIT");
                grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_visit.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_patient.push_group(grp_visit);
            }
            while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
                let mut grp_insurance = RawGroup::new("INSURANCE");
                grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
                if let Some(s) = segments.optional("IN2") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
                if let Some(s) = segments.optional("IN3") {
                    grp_insurance.push(RawSegment::from_tokens(&s));
                }
                grp_patient.push_group(grp_insurance);
            }
            grp_patient_result.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["CTD", "CTI", "DEV", "FT1", "NTE", "OBR", "OBX", "ORC", "PRT", "SPM", "TQ1", "TQ2", "TXA"]) {
            let mut grp_order_observation = RawGroup::new("ORDER_OBSERVATION");
            if segments.peek_matches_any(&["OBX", "ORC", "PRT", "TXA"]) {
                let mut grp_common_order = RawGroup::new("COMMON_ORDER");
                grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_common_order.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["OBX", "PRT", "TXA"]) {
                    let mut grp_order_document = RawGroup::new("ORDER_DOCUMENT");
                    grp_order_document.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_document.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_document.push(RawSegment::from_tokens(&segments.expect("TXA")?));
                    grp_common_order.push_group(grp_order_document);
                }
                grp_order_observation.push_group(grp_common_order);
            }
            grp_order_observation.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["DEV", "PRT"]) {
                let mut grp_observation_participation = RawGroup::new("OBSERVATION_PARTICIPATION");
                grp_observation_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                while segments.peek_matches_any(&["DEV"]) {
                    if let Some(s) = segments.optional("DEV") {
                        grp_observation_participation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_observation.push_group(grp_observation_participation);
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
                grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_qty.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_observation.push_group(grp_timing_qty);
            }
            if let Some(s) = segments.optional("CTD") {
                grp_order_observation.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_observation.push_group(grp_observation);
            }
            while segments.peek_matches_any(&["FT1"]) {
                if let Some(s) = segments.optional("FT1") {
                    grp_order_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CTI"]) {
                if let Some(s) = segments.optional("CTI") {
                    grp_order_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["OBX", "PRT", "SPM"]) {
                let mut grp_specimen = RawGroup::new("SPECIMEN");
                grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                    grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_specimen_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_specimen_observation);
                }
                grp_order_observation.push_group(grp_specimen);
            }
            grp_patient_result.push_group(grp_order_observation);
        }
        while segments.peek_matches_any(&["DEV", "OBX"]) {
            let mut grp_device = RawGroup::new("DEVICE");
            grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
            while segments.peek_matches_any(&["OBX"]) {
                if let Some(s) = segments.optional("OBX") {
                    grp_device.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient_result.push_group(grp_device);
        }
        msg.push_group(grp_patient_result);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_oru_r30(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORU_R30");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH1"]) {
        if let Some(s) = segments.optional("OH1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OH2"]) {
        if let Some(s) = segments.optional("OH2") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("OH3") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["OH4"]) {
        if let Some(s) = segments.optional("OH4") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["OBX", "PRT"]) {
        let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
        grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient_observation);
    }
    if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_visit);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("ORC")?));
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("OBR")?));
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
        let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
        grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
        while segments.peek_matches_any(&["TQ2"]) {
            if let Some(s) = segments.optional("TQ2") {
                grp_timing_qty.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_timing_qty);
    }
    while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_observation);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    Ok(msg)
}
pub fn parse_orx_o58(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("ORX_O58");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "CTI", "NTE", "ORC", "PID", "PRT", "TXA"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["ARV", "NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["CTI", "ORC", "PRT", "TXA"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("TXA")?));
            while segments.peek_matches_any(&["CTI"]) {
                if let Some(s) = segments.optional("CTI") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_osm_r26(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OSM_R26");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["ARV", "NK1", "OBX", "PAC", "PID", "PRT", "PV1", "SAC", "SHP", "SPM"]) {
        let mut grp_shipment = RawGroup::new("SHIPMENT");
        grp_shipment.push(RawSegment::from_tokens(&segments.expect("SHP")?));
        grp_shipment.push(RawSegment::from_tokens(&segments.expect("PRT")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_shipment.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_shipping_observation = RawGroup::new("SHIPPING_OBSERVATION");
            grp_shipping_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_shipping_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_shipment.push_group(grp_shipping_observation);
        }
        while segments.peek_matches_any(&["ARV", "NK1", "OBX", "PAC", "PID", "PRT", "PV1", "SAC", "SPM"]) {
            let mut grp_package = RawGroup::new("PACKAGE");
            grp_package.push(RawSegment::from_tokens(&segments.expect("PAC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_package.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV", "NK1", "OBX", "PID", "PRT", "PV1", "SAC", "SPM"]) {
                let mut grp_specimen = RawGroup::new("SPECIMEN");
                grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                    grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_specimen_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_specimen_observation);
                }
                while segments.peek_matches_any(&["OBX", "PRT", "SAC"]) {
                    let mut grp_container = RawGroup::new("CONTAINER");
                    grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                    while segments.peek_matches_any(&["OBX", "PRT"]) {
                        let mut grp_container_observation = RawGroup::new("CONTAINER_OBSERVATION");
                        grp_container_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_container_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_container.push_group(grp_container_observation);
                    }
                    grp_specimen.push_group(grp_container);
                }
                if segments.peek_matches_any(&["ARV", "NK1", "OBX", "PID", "PRT"]) {
                    let mut grp_subject_person_or_animal_identification = RawGroup::new("SUBJECT_PERSON_OR_ANIMAL_IDENTIFICATION");
                    grp_subject_person_or_animal_identification.push(RawSegment::from_tokens(&segments.expect("PID")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_subject_person_or_animal_identification.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["ARV"]) {
                        if let Some(s) = segments.optional("ARV") {
                            grp_subject_person_or_animal_identification.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["OBX", "PRT"]) {
                        let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
                        grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_patient_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_subject_person_or_animal_identification.push_group(grp_patient_observation);
                    }
                    while segments.peek_matches_any(&["NK1"]) {
                        if let Some(s) = segments.optional("NK1") {
                            grp_subject_person_or_animal_identification.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_subject_person_or_animal_identification);
                }
                if segments.peek_matches_any(&["NK1", "OBX", "PID", "PRT", "PV1"]) {
                    let mut grp_subject_population_or_location_identification = RawGroup::new("SUBJECT_POPULATION_OR_LOCATION_IDENTIFICATION");
                    grp_subject_population_or_location_identification.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_subject_population_or_location_identification.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["OBX", "PRT"]) {
                        let mut grp_patient_visit_observation = RawGroup::new("PATIENT_VISIT_OBSERVATION");
                        grp_patient_visit_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_patient_visit_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_subject_population_or_location_identification.push_group(grp_patient_visit_observation);
                    }
                    if let Some(s) = segments.optional("PID") {
                        grp_subject_population_or_location_identification.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_subject_population_or_location_identification.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NK1"]) {
                        if let Some(s) = segments.optional("NK1") {
                            grp_subject_population_or_location_identification.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_specimen.push_group(grp_subject_population_or_location_identification);
                }
                grp_package.push_group(grp_specimen);
            }
            grp_shipment.push_group(grp_package);
        }
        msg.push_group(grp_shipment);
    }
    Ok(msg)
}
pub fn parse_osu_o51(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OSU_O51");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("PID") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ORC", "PRT"]) {
        let mut grp_order_status = RawGroup::new("ORDER_STATUS");
        grp_order_status.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order_status.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order_status);
    }
    Ok(msg)
}
pub fn parse_osu_o52(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OSU_O52");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["PID", "PRT"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ORC", "PRT"]) {
        let mut grp_order_status = RawGroup::new("ORDER_STATUS");
        grp_order_status.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order_status.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order_status);
    }
    Ok(msg)
}
pub fn parse_oul_r22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OUL_R22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("NTE") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
            grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_observation);
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_visit = RawGroup::new("VISIT");
            grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CTI", "INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SID", "SPM", "TCD", "TQ1", "TQ2", "TXA"]) {
        let mut grp_specimen = RawGroup::new("SPECIMEN");
        grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
            grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_specimen_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen.push_group(grp_specimen_observation);
        }
        while segments.peek_matches_any(&["INV", "SAC"]) {
            let mut grp_container = RawGroup::new("CONTAINER");
            grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
            if let Some(s) = segments.optional("INV") {
                grp_container.push(RawSegment::from_tokens(&s));
            }
            grp_specimen.push_group(grp_container);
        }
        while segments.peek_matches_any(&["CTI", "INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SID", "TCD", "TQ1", "TQ2", "TXA"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["OBX", "ORC", "PRT", "TXA"]) {
                let mut grp_common_order = RawGroup::new("COMMON_ORDER");
                grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_common_order.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["OBX", "PRT", "TXA"]) {
                    let mut grp_order_document = RawGroup::new("ORDER_DOCUMENT");
                    grp_order_document.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_document.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_document.push(RawSegment::from_tokens(&segments.expect("TXA")?));
                    grp_common_order.push_group(grp_order_document);
                }
                grp_order.push_group(grp_common_order);
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
                grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_qty.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing_qty);
            }
            while segments.peek_matches_any(&["INV", "NTE", "OBX", "PRT", "SID", "TCD"]) {
                let mut grp_result = RawGroup::new("RESULT");
                grp_result.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_result.push(RawSegment::from_tokens(&s));
                    }
                }
                if let Some(s) = segments.optional("TCD") {
                    grp_result.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["SID"]) {
                    if let Some(s) = segments.optional("SID") {
                        grp_result.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["INV"]) {
                    if let Some(s) = segments.optional("INV") {
                        grp_result.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_result.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_result);
            }
            while segments.peek_matches_any(&["CTI"]) {
                if let Some(s) = segments.optional("CTI") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen.push_group(grp_order);
        }
        msg.push_group(grp_specimen);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_oul_r23(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OUL_R23");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("NTE") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["ARV", "NTE", "OBX", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OH1"]) {
            if let Some(s) = segments.optional("OH1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["OH4"]) {
            if let Some(s) = segments.optional("OH4") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
            grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_observation);
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_visit = RawGroup::new("VISIT");
            grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CTI", "INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SID", "SPM", "TCD", "TQ1", "TQ2", "TXA"]) {
        let mut grp_specimen = RawGroup::new("SPECIMEN");
        grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
            grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_specimen_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen.push_group(grp_specimen_observation);
        }
        while segments.peek_matches_any(&["CTI", "INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SID", "TCD", "TQ1", "TQ2", "TXA"]) {
            let mut grp_container = RawGroup::new("CONTAINER");
            grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
            if let Some(s) = segments.optional("INV") {
                grp_container.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["CTI", "INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SID", "TCD", "TQ1", "TQ2", "TXA"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["OBX", "ORC", "PRT", "TXA"]) {
                    let mut grp_common_order = RawGroup::new("COMMON_ORDER");
                    grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_common_order.push(RawSegment::from_tokens(&s));
                        }
                    }
                    if segments.peek_matches_any(&["OBX", "PRT", "TXA"]) {
                        let mut grp_order_document = RawGroup::new("ORDER_DOCUMENT");
                        grp_order_document.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_order_document.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_document.push(RawSegment::from_tokens(&segments.expect("TXA")?));
                        grp_common_order.push_group(grp_order_document);
                    }
                    grp_order.push_group(grp_common_order);
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
                    grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_qty.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_timing_qty);
                }
                while segments.peek_matches_any(&["INV", "NTE", "OBX", "PRT", "SID", "TCD"]) {
                    let mut grp_result = RawGroup::new("RESULT");
                    grp_result.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    if let Some(s) = segments.optional("TCD") {
                        grp_result.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["SID"]) {
                        if let Some(s) = segments.optional("SID") {
                            grp_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["INV"]) {
                        if let Some(s) = segments.optional("INV") {
                            grp_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_result.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order.push_group(grp_result);
                }
                while segments.peek_matches_any(&["CTI"]) {
                    if let Some(s) = segments.optional("CTI") {
                        grp_order.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_container.push_group(grp_order);
            }
            grp_specimen.push_group(grp_container);
        }
        msg.push_group(grp_specimen);
    }
    while segments.peek_matches_any(&["DEV", "OBX"]) {
        let mut grp_device = RawGroup::new("DEVICE");
        grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_device.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_device);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_oul_r24(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("OUL_R24");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("NTE") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["ARV", "NTE", "OBX", "OH1", "OH2", "OH3", "OH4", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OH1"]) {
            if let Some(s) = segments.optional("OH1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OH2"]) {
            if let Some(s) = segments.optional("OH2") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("OH3") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["OH4"]) {
            if let Some(s) = segments.optional("OH4") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_patient_observation = RawGroup::new("PATIENT_OBSERVATION");
            grp_patient_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_observation);
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_visit = RawGroup::new("VISIT");
            grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CTI", "DEV", "INV", "NTE", "OBR", "OBX", "ORC", "PRT", "SAC", "SID", "SPM", "TCD", "TQ1", "TQ2", "TXA"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["OBX", "ORC", "PRT", "TXA"]) {
            let mut grp_common_order = RawGroup::new("COMMON_ORDER");
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["OBX", "PRT", "TXA"]) {
                let mut grp_order_document = RawGroup::new("ORDER_DOCUMENT");
                grp_order_document.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order_document.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_document.push(RawSegment::from_tokens(&segments.expect("TXA")?));
                grp_common_order.push_group(grp_order_document);
            }
            grp_order.push_group(grp_common_order);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
            grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_qty.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing_qty);
        }
        while segments.peek_matches_any(&["INV", "OBX", "PRT", "SAC", "SPM"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX", "PRT"]) {
                let mut grp_specimen_observation = RawGroup::new("SPECIMEN_OBSERVATION");
                grp_specimen_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_specimen_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_specimen.push_group(grp_specimen_observation);
            }
            while segments.peek_matches_any(&["INV", "SAC"]) {
                let mut grp_container = RawGroup::new("CONTAINER");
                grp_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
                if let Some(s) = segments.optional("INV") {
                    grp_container.push(RawSegment::from_tokens(&s));
                }
                grp_specimen.push_group(grp_container);
            }
            grp_order.push_group(grp_specimen);
        }
        while segments.peek_matches_any(&["INV", "NTE", "OBX", "PRT", "SID", "TCD"]) {
            let mut grp_result = RawGroup::new("RESULT");
            grp_result.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_result.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("TCD") {
                grp_result.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["SID"]) {
                if let Some(s) = segments.optional("SID") {
                    grp_result.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["INV"]) {
                if let Some(s) = segments.optional("INV") {
                    grp_result.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_result.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_result);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DEV", "OBX"]) {
            let mut grp_device = RawGroup::new("DEVICE");
            grp_device.push(RawSegment::from_tokens(&segments.expect("DEV")?));
            while segments.peek_matches_any(&["OBX"]) {
                if let Some(s) = segments.optional("OBX") {
                    grp_device.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_device);
        }
        msg.push_group(grp_order);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_pex_p07(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PEX_P07");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_visit.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_visit);
    }
    while segments.peek_matches_any(&["CSP", "CSR", "NK1", "NTE", "OBX", "PCR", "PEO", "PES", "PRB", "PRT", "RXA", "RXE", "RXR", "TQ1", "TQ2"]) {
        let mut grp_experience = RawGroup::new("EXPERIENCE");
        grp_experience.push(RawSegment::from_tokens(&segments.expect("PES")?));
        while segments.peek_matches_any(&["CSP", "CSR", "NK1", "NTE", "OBX", "PCR", "PEO", "PRB", "PRT", "RXA", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_pex_observation = RawGroup::new("PEX_OBSERVATION");
            grp_pex_observation.push(RawSegment::from_tokens(&segments.expect("PEO")?));
            while segments.peek_matches_any(&["CSP", "CSR", "NK1", "NTE", "OBX", "PCR", "PRB", "PRT", "RXA", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_pex_cause = RawGroup::new("PEX_CAUSE");
                grp_pex_cause.push(RawSegment::from_tokens(&segments.expect("PCR")?));
                if segments.peek_matches_any(&["PRT", "RXE", "RXR", "TQ1", "TQ2"]) {
                    let mut grp_rx_order = RawGroup::new("RX_ORDER");
                    grp_rx_order.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_rx_order.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                        let mut grp_timing_qty = RawGroup::new("TIMING_QTY");
                        grp_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                        while segments.peek_matches_any(&["TQ2"]) {
                            if let Some(s) = segments.optional("TQ2") {
                                grp_timing_qty.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_rx_order.push_group(grp_timing_qty);
                    }
                    while segments.peek_matches_any(&["RXR"]) {
                        if let Some(s) = segments.optional("RXR") {
                            grp_rx_order.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_pex_cause.push_group(grp_rx_order);
                }
                while segments.peek_matches_any(&["PRT", "RXA", "RXR"]) {
                    let mut grp_rx_administration = RawGroup::new("RX_ADMINISTRATION");
                    grp_rx_administration.push(RawSegment::from_tokens(&segments.expect("RXA")?));
                    if let Some(s) = segments.optional("RXR") {
                        grp_rx_administration.push(RawSegment::from_tokens(&s));
                    }
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_rx_administration.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_pex_cause.push_group(grp_rx_administration);
                }
                while segments.peek_matches_any(&["PRB"]) {
                    if let Some(s) = segments.optional("PRB") {
                        grp_pex_cause.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["OBX", "PRT"]) {
                    let mut grp_observation = RawGroup::new("OBSERVATION");
                    grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_pex_cause.push_group(grp_observation);
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_pex_cause.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["NK1", "OBX", "PRB", "PRT", "RXA", "RXE", "RXR", "TQ1", "TQ2"]) {
                    let mut grp_associated_person = RawGroup::new("ASSOCIATED_PERSON");
                    grp_associated_person.push(RawSegment::from_tokens(&segments.expect("NK1")?));
                    if segments.peek_matches_any(&["PRT", "RXE", "RXR", "TQ1", "TQ2"]) {
                        let mut grp_associated_rx_order = RawGroup::new("ASSOCIATED_RX_ORDER");
                        grp_associated_rx_order.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_associated_rx_order.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                            let mut grp_nk1_timing_qty = RawGroup::new("NK1_TIMING_QTY");
                            grp_nk1_timing_qty.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                            while segments.peek_matches_any(&["TQ2"]) {
                                if let Some(s) = segments.optional("TQ2") {
                                    grp_nk1_timing_qty.push(RawSegment::from_tokens(&s));
                                }
                            }
                            grp_associated_rx_order.push_group(grp_nk1_timing_qty);
                        }
                        while segments.peek_matches_any(&["RXR"]) {
                            if let Some(s) = segments.optional("RXR") {
                                grp_associated_rx_order.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_associated_person.push_group(grp_associated_rx_order);
                    }
                    while segments.peek_matches_any(&["PRT", "RXA", "RXR"]) {
                        let mut grp_associated_rx_admin = RawGroup::new("ASSOCIATED_RX_ADMIN");
                        grp_associated_rx_admin.push(RawSegment::from_tokens(&segments.expect("RXA")?));
                        if let Some(s) = segments.optional("RXR") {
                            grp_associated_rx_admin.push(RawSegment::from_tokens(&s));
                        }
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_associated_rx_admin.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_associated_person.push_group(grp_associated_rx_admin);
                    }
                    while segments.peek_matches_any(&["PRB"]) {
                        if let Some(s) = segments.optional("PRB") {
                            grp_associated_person.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["OBX", "PRT"]) {
                        let mut grp_associated_observation = RawGroup::new("ASSOCIATED_OBSERVATION");
                        grp_associated_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_associated_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_associated_person.push_group(grp_associated_observation);
                    }
                    grp_pex_cause.push_group(grp_associated_person);
                }
                while segments.peek_matches_any(&["CSP", "CSR"]) {
                    let mut grp_study = RawGroup::new("STUDY");
                    grp_study.push(RawSegment::from_tokens(&segments.expect("CSR")?));
                    while segments.peek_matches_any(&["CSP"]) {
                        if let Some(s) = segments.optional("CSP") {
                            grp_study.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_pex_cause.push_group(grp_study);
                }
                grp_pex_observation.push_group(grp_pex_cause);
            }
            grp_experience.push_group(grp_pex_observation);
        }
        msg.push_group(grp_experience);
    }
    Ok(msg)
}
pub fn parse_pgl_pc6(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PGL_PC6");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["GOL", "NTE", "OBX", "ORC", "PRB", "PRT", "PTH", "ROL", "VAR"]) {
        let mut grp_goal = RawGroup::new("GOAL");
        grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_goal.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
            let mut grp_goal_participation = RawGroup::new("GOAL_PARTICIPATION");
            grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
            grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_goal_participation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_goal_participation);
        }
        while segments.peek_matches_any(&["PTH", "VAR"]) {
            let mut grp_pathway = RawGroup::new("PATHWAY");
            grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_pathway);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_goal.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRB", "PRT", "ROL", "VAR"]) {
            let mut grp_problem = RawGroup::new("PROBLEM");
            grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_problem.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_problem.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
                let mut grp_problem_participation = RawGroup::new("PROBLEM_PARTICIPATION");
                grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
                grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_problem_participation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_problem.push_group(grp_problem_participation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
                grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_problem_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_problem_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_problem.push_group(grp_problem_observation);
            }
            grp_goal.push_group(grp_problem);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "ORC", "PRT", "VAR"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            if segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");

                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                    let mut grp_order_observation = RawGroup::new("ORDER_OBSERVATION");
                    grp_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_order_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["VAR"]) {
                        if let Some(s) = segments.optional("VAR") {
                            grp_order_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail.push_group(grp_order_observation);
                }
                grp_order.push_group(grp_order_detail);
            }
            grp_goal.push_group(grp_order);
        }
        msg.push_group(grp_goal);
    }
    Ok(msg)
}
pub fn parse_pmu_b01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PMU_B01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("STF")?));
    while segments.peek_matches_any(&["PRA"]) {
        if let Some(s) = segments.optional("PRA") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ORG"]) {
        if let Some(s) = segments.optional("ORG") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AFF"]) {
        if let Some(s) = segments.optional("AFF") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["LAN"]) {
        if let Some(s) = segments.optional("LAN") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["EDU"]) {
        if let Some(s) = segments.optional("EDU") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["CER"]) {
        if let Some(s) = segments.optional("CER") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ROL"]) {
        if let Some(s) = segments.optional("ROL") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_pmu_b03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PMU_B03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("STF")?));
    Ok(msg)
}
pub fn parse_pmu_b04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PMU_B04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("STF")?));
    while segments.peek_matches_any(&["PRA"]) {
        if let Some(s) = segments.optional("PRA") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ORG"]) {
        if let Some(s) = segments.optional("ORG") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_pmu_b07(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PMU_B07");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("STF")?));
    if let Some(s) = segments.optional("PRA") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["CER", "PRT", "ROL"]) {
        let mut grp_certificate = RawGroup::new("CERTIFICATE");
        grp_certificate.push(RawSegment::from_tokens(&segments.expect("CER")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_certificate.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_certificate.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_certificate);
    }
    Ok(msg)
}
pub fn parse_pmu_b08(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PMU_B08");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EVN")?));
    msg.push(RawSegment::from_tokens(&segments.expect("STF")?));
    if let Some(s) = segments.optional("PRA") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["CER"]) {
        if let Some(s) = segments.optional("CER") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_ppg_pcg(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PPG_PCG");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["GOL", "NTE", "OBX", "ORC", "PRB", "PRT", "PTH", "ROL", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
            let mut grp_pathway_participation = RawGroup::new("PATHWAY_PARTICIPATION");
            grp_pathway_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
            grp_pathway_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_pathway_participation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_participation);
        }
        while segments.peek_matches_any(&["GOL", "NTE", "OBX", "ORC", "PRB", "PRT", "ROL", "VAR"]) {
            let mut grp_goal = RawGroup::new("GOAL");
            grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_goal.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_goal.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
                let mut grp_goal_participation = RawGroup::new("GOAL_PARTICIPATION");
                grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
                grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_goal_participation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_goal.push_group(grp_goal_participation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
                grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_goal_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_goal_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_goal.push_group(grp_goal_observation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRB", "PRT", "ROL", "VAR"]) {
                let mut grp_problem = RawGroup::new("PROBLEM");
                grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_problem.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_problem.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
                    let mut grp_problem_participation = RawGroup::new("PROBLEM_PARTICIPATION");
                    grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
                    grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                    while segments.peek_matches_any(&["VAR"]) {
                        if let Some(s) = segments.optional("VAR") {
                            grp_problem_participation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_problem.push_group(grp_problem_participation);
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                    let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
                    grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_problem_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_problem_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_problem.push_group(grp_problem_observation);
                }
                grp_goal.push_group(grp_problem);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "ORC", "PRT", "VAR"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                if segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                    let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");

                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_order_detail.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["VAR"]) {
                        if let Some(s) = segments.optional("VAR") {
                            grp_order_detail.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                        let mut grp_order_observation = RawGroup::new("ORDER_OBSERVATION");
                        grp_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_order_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_order_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["VAR"]) {
                            if let Some(s) = segments.optional("VAR") {
                                grp_order_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_detail.push_group(grp_order_observation);
                    }
                    grp_order.push_group(grp_order_detail);
                }
                grp_goal.push_group(grp_order);
            }
            grp_pathway.push_group(grp_goal);
        }
        msg.push_group(grp_pathway);
    }
    Ok(msg)
}
pub fn parse_ppp_pcb(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PPP_PCB");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["GOL", "NTE", "OBX", "ORC", "PRB", "PRT", "PTH", "ROL", "VAR"]) {
        let mut grp_pathway = RawGroup::new("PATHWAY");
        grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_pathway.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
            let mut grp_pathway_participation = RawGroup::new("PATHWAY_PARTICIPATION");
            grp_pathway_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
            grp_pathway_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_pathway_participation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_pathway.push_group(grp_pathway_participation);
        }
        while segments.peek_matches_any(&["GOL", "NTE", "OBX", "ORC", "PRB", "PRT", "ROL", "VAR"]) {
            let mut grp_problem = RawGroup::new("PROBLEM");
            grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_problem.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_problem.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
                let mut grp_problem_participation = RawGroup::new("PROBLEM_PARTICIPATION");
                grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
                grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_problem_participation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_problem.push_group(grp_problem_participation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
                grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_problem_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_problem_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_problem.push_group(grp_problem_observation);
            }
            while segments.peek_matches_any(&["GOL", "NTE", "OBX", "PRT", "ROL", "VAR"]) {
                let mut grp_goal = RawGroup::new("GOAL");
                grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_goal.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_goal.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
                    let mut grp_goal_participation = RawGroup::new("GOAL_PARTICIPATION");
                    grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
                    grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                    while segments.peek_matches_any(&["VAR"]) {
                        if let Some(s) = segments.optional("VAR") {
                            grp_goal_participation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_goal.push_group(grp_goal_participation);
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                    let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
                    grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_goal_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_goal_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_goal.push_group(grp_goal_observation);
                }
                grp_problem.push_group(grp_goal);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "ORC", "PRT", "VAR"]) {
                let mut grp_order = RawGroup::new("ORDER");
                grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
                if segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                    let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");

                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_order_detail.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["VAR"]) {
                        if let Some(s) = segments.optional("VAR") {
                            grp_order_detail.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                        let mut grp_order_observation = RawGroup::new("ORDER_OBSERVATION");
                        grp_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                        while segments.peek_matches_any(&["PRT"]) {
                            if let Some(s) = segments.optional("PRT") {
                                grp_order_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["NTE"]) {
                            if let Some(s) = segments.optional("NTE") {
                                grp_order_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        while segments.peek_matches_any(&["VAR"]) {
                            if let Some(s) = segments.optional("VAR") {
                                grp_order_observation.push(RawSegment::from_tokens(&s));
                            }
                        }
                        grp_order_detail.push_group(grp_order_observation);
                    }
                    grp_order.push_group(grp_order_detail);
                }
                grp_problem.push_group(grp_order);
            }
            grp_pathway.push_group(grp_problem);
        }
        msg.push_group(grp_pathway);
    }
    Ok(msg)
}
pub fn parse_ppr_pc1(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("PPR_PC1");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["GOL", "NTE", "OBX", "ORC", "PRB", "PRT", "PTH", "ROL", "VAR"]) {
        let mut grp_problem = RawGroup::new("PROBLEM");
        grp_problem.push(RawSegment::from_tokens(&segments.expect("PRB")?));
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["VAR"]) {
            if let Some(s) = segments.optional("VAR") {
                grp_problem.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
            let mut grp_problem_participation = RawGroup::new("PROBLEM_PARTICIPATION");
            grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
            grp_problem_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_problem_participation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_problem_participation);
        }
        while segments.peek_matches_any(&["PTH", "VAR"]) {
            let mut grp_pathway = RawGroup::new("PATHWAY");
            grp_pathway.push(RawSegment::from_tokens(&segments.expect("PTH")?));
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_pathway.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_pathway);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_problem_observation = RawGroup::new("PROBLEM_OBSERVATION");
            grp_problem_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_problem_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_problem_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_problem.push_group(grp_problem_observation);
        }
        while segments.peek_matches_any(&["GOL", "NTE", "OBX", "PRT", "ROL", "VAR"]) {
            let mut grp_goal = RawGroup::new("GOAL");
            grp_goal.push(RawSegment::from_tokens(&segments.expect("GOL")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_goal.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["VAR"]) {
                if let Some(s) = segments.optional("VAR") {
                    grp_goal.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT", "ROL", "VAR"]) {
                let mut grp_goal_participation = RawGroup::new("GOAL_PARTICIPATION");
                grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("ROL")?));
                grp_goal_participation.push(RawSegment::from_tokens(&segments.expect("PRT")?));
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_goal_participation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_goal.push_group(grp_goal_participation);
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_goal_observation = RawGroup::new("GOAL_OBSERVATION");
                grp_goal_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_goal_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_goal_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_goal.push_group(grp_goal_observation);
            }
            grp_problem.push_group(grp_goal);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "ORC", "PRT", "VAR"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            if segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");

                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["VAR"]) {
                    if let Some(s) = segments.optional("VAR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "OBX", "PRT", "VAR"]) {
                    let mut grp_order_observation = RawGroup::new("ORDER_OBSERVATION");
                    grp_order_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_order_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_order_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["VAR"]) {
                        if let Some(s) = segments.optional("VAR") {
                            grp_order_observation.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail.push_group(grp_order_observation);
                }
                grp_order.push_group(grp_order_detail);
            }
            grp_problem.push_group(grp_order);
        }
        msg.push_group(grp_problem);
    }
    Ok(msg)
}
pub fn parse_qbp_e03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_E03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_qbp_e22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_E22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_qbp_o33(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_O33");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    Ok(msg)
}
pub fn parse_qbp_o34(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_O34");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    Ok(msg)
}
pub fn parse_qbp_q11(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_Q11");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["anyHL7Segment"]) {
        let mut grp_qbp = RawGroup::new("QBP");
        if let Some(s) = segments.optional("anyHL7Segment") {
            grp_qbp.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_qbp);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_qbp_q13(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_Q13");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if let Some(s) = segments.optional("PID") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("RDF") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("RDF") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_qbp_q15(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_Q15");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if let Some(s) = segments.optional("anyHL7Segment") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_qbp_q21(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_Q21");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_qbp_qnn(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_Qnn");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if let Some(s) = segments.optional("RDF") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_qbp_z73(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QBP_Z73");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    Ok(msg)
}
pub fn parse_qcn_j01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QCN_J01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QID")?));
    Ok(msg)
}
pub fn parse_qsb_q16(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QSB_Q16");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_qvr_q17(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("QVR_Q17");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["anyHL7Segment"]) {
        let mut grp_qbp = RawGroup::new("QBP");
        if let Some(s) = segments.optional("anyHL7Segment") {
            grp_qbp.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_qbp);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_ras_o17(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RAS_O17");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PD1")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["CDO", "CTI", "NTE", "OBX", "ORC", "PRT", "RXA", "RXC", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["NTE", "RXC", "RXR"]) {
                let mut grp_order_detail_supplement = RawGroup::new("ORDER_DETAIL_SUPPLEMENT");
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("NTE")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_components = RawGroup::new("COMPONENTS");
                    grp_components.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_components.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail_supplement.push_group(grp_components);
                }
                grp_order_detail.push_group(grp_order_detail_supplement);
            }
            grp_order.push_group(grp_order_detail);
        }
        if segments.peek_matches_any(&["CDO", "NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_encoding = RawGroup::new("ENCODING");
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_encoding.push_group(grp_timing_encoded);
            }
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CDO"]) {
                if let Some(s) = segments.optional("CDO") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_encoding);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT", "RXA", "RXR"]) {
            let mut grp_administration = RawGroup::new("ADMINISTRATION");
            grp_administration.push(RawSegment::from_tokens(&segments.expect("RXA")?));
            while segments.peek_matches_any(&["RXA"]) {
                if let Some(s) = segments.optional("RXA") {
                    grp_administration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_administration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_administration.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_administration.push_group(grp_observation);
            }
            grp_order.push_group(grp_administration);
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_rcv_o59(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RCV_O59");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["FT1", "NTE", "OBX", "ORC", "PRT", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["NTE", "RXC", "RXO", "RXR"]) {
            let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            if segments.peek_matches_any(&["NTE", "RXC", "RXR"]) {
                let mut grp_order_detail_supplement = RawGroup::new("ORDER_DETAIL_SUPPLEMENT");
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("NTE")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_component = RawGroup::new("COMPONENT");
                    grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_component.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail_supplement.push_group(grp_component);
                }
                grp_order_detail.push_group(grp_order_detail_supplement);
            }
            grp_order.push_group(grp_order_detail);
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_encoding = RawGroup::new("ENCODING");
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_encoding.push_group(grp_timing_encoded);
            }
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_encoding);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXD")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
        while segments.peek_matches_any(&["RXR"]) {
            if let Some(s) = segments.optional("RXR") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["RXC"]) {
            if let Some(s) = segments.optional("RXC") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_rde_o11(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RDE_O11");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "CDO", "CTI", "FT1", "NTE", "OBX", "ORC", "PRT", "RXC", "RXE", "RXO", "RXR", "RXV", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "RXC"]) {
                let mut grp_component = RawGroup::new("COMPONENT");
                grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_component.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail.push_group(grp_component);
            }
            grp_order.push_group(grp_order_detail);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXE")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
            grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_encoded.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing_encoded);
        }
        while segments.peek_matches_any(&["NTE", "PRT", "RXV", "TQ1", "TQ2"]) {
            let mut grp_pharmacy_treatment_infusion_order = RawGroup::new("PHARMACY_TREATMENT_INFUSION_ORDER");
            grp_pharmacy_treatment_infusion_order.push(RawSegment::from_tokens(&segments.expect("RXV")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_pharmacy_treatment_infusion_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_pharmacy_treatment_infusion_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_pharmacy_treatment_infusion_order.push_group(grp_timing_encoded);
            }
            grp_order.push_group(grp_pharmacy_treatment_infusion_order);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
        while segments.peek_matches_any(&["RXR"]) {
            if let Some(s) = segments.optional("RXR") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["RXC"]) {
            if let Some(s) = segments.optional("RXC") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CDO"]) {
            if let Some(s) = segments.optional("CDO") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_rde_o49(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RDE_O49");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "GT1", "IN1", "IN2", "IN3", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_patient.push_group(grp_insurance);
        }
        if let Some(s) = segments.optional("GT1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["BLG", "CTI", "FT1", "NTE", "OBX", "ORC", "PRT", "RXC", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "RXC"]) {
                let mut grp_component = RawGroup::new("COMPONENT");
                grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_component.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail.push_group(grp_component);
            }
            grp_order.push_group(grp_order_detail);
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXE")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
            grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing_encoded.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing_encoded);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
        while segments.peek_matches_any(&["RXR"]) {
            if let Some(s) = segments.optional("RXR") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["RXC"]) {
            if let Some(s) = segments.optional("RXC") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("BLG") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["CTI"]) {
            if let Some(s) = segments.optional("CTI") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_rdr_rdr(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RDR_RDR");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("SFT") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE", "ORC", "PID", "QRD", "QRF", "RXC", "RXD", "RXE", "RXR", "TQ1", "TQ2"]) {
        let mut grp_definition = RawGroup::new("DEFINITION");
        grp_definition.push(RawSegment::from_tokens(&segments.expect("QRD")?));
        if let Some(s) = segments.optional("QRF") {
            grp_definition.push(RawSegment::from_tokens(&s));
        }
        if segments.peek_matches_any(&["NTE", "PID"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_definition.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["ORC", "RXC", "RXD", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_encoding = RawGroup::new("ENCODING");
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_encoding.push_group(grp_timing_encoded);
                }
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_encoding);
            }
            while segments.peek_matches_any(&["RXC", "RXD", "RXR"]) {
                let mut grp_dispense = RawGroup::new("DISPENSE");
                grp_dispense.push(RawSegment::from_tokens(&segments.expect("RXD")?));
                grp_dispense.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_dispense);
            }
            grp_definition.push_group(grp_order);
        }
        msg.push_group(grp_definition);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rds_o13(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RDS_O13");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PD1")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["CDO", "FT1", "NTE", "OBX", "ORC", "PRT", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["NTE", "RXC", "RXR"]) {
                let mut grp_order_detail_supplement = RawGroup::new("ORDER_DETAIL_SUPPLEMENT");
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("NTE")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_component = RawGroup::new("COMPONENT");
                    grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_component.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail_supplement.push_group(grp_component);
                }
                grp_order_detail.push_group(grp_order_detail_supplement);
            }
            grp_order.push_group(grp_order_detail);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_encoding = RawGroup::new("ENCODING");
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_encoding.push_group(grp_timing_encoded);
            }
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_encoding);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXD")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
        while segments.peek_matches_any(&["RXR"]) {
            if let Some(s) = segments.optional("RXR") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["RXC"]) {
            if let Some(s) = segments.optional("RXC") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CDO"]) {
            if let Some(s) = segments.optional("CDO") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["FT1"]) {
            if let Some(s) = segments.optional("FT1") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_rdy_k15(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RDY_K15");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    while segments.peek_matches_any(&["DSP"]) {
        if let Some(s) = segments.optional("DSP") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rdy_z80(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RDY_Z80");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    while segments.peek_matches_any(&["DSP"]) {
        if let Some(s) = segments.optional("DSP") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_ref_i12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("REF_I12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("RF1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AUT", "CTD"]) {
        let mut grp_authorization_contact2 = RawGroup::new("AUTHORIZATION_CONTACT2");
        grp_authorization_contact2.push(RawSegment::from_tokens(&segments.expect("AUT")?));
        if let Some(s) = segments.optional("CTD") {
            grp_authorization_contact2.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_authorization_contact2);
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider_contact = RawGroup::new("PROVIDER_CONTACT");
        grp_provider_contact.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider_contact.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider_contact);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DRG"]) {
        if let Some(s) = segments.optional("DRG") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "CTD", "PR1"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        if segments.peek_matches_any(&["AUT", "CTD"]) {
            let mut grp_authorization_contact2 = RawGroup::new("AUTHORIZATION_CONTACT2");
            grp_authorization_contact2.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            if let Some(s) = segments.optional("CTD") {
                grp_authorization_contact2.push(RawSegment::from_tokens(&s));
            }
            grp_procedure.push_group(grp_authorization_contact2);
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_results_notes = RawGroup::new("RESULTS_NOTES");
            grp_results_notes.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_results_notes.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_results_notes.push(RawSegment::from_tokens(&s));
                }
            }
            grp_observation.push_group(grp_results_notes);
        }
        msg.push_group(grp_observation);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rgv_o15(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RGV_O15");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
            let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
            grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            if let Some(s) = segments.optional("PV2") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_patient_visit);
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["CDO", "NTE", "OBX", "ORC", "PRT", "RXC", "RXE", "RXG", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
            let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
            grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order_detail.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["NTE", "RXC", "RXR"]) {
                let mut grp_order_detail_supplement = RawGroup::new("ORDER_DETAIL_SUPPLEMENT");
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("NTE")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail_supplement.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail_supplement.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_components = RawGroup::new("COMPONENTS");
                    grp_components.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_components.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail_supplement.push_group(grp_components);
                }
                grp_order_detail.push_group(grp_order_detail_supplement);
            }
            grp_order.push_group(grp_order_detail);
        }
        if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_encoding = RawGroup::new("ENCODING");
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_encoding.push_group(grp_timing_encoded);
            }
            grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_encoding.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_encoding);
        }
        while segments.peek_matches_any(&["CDO", "NTE", "OBX", "PRT", "RXC", "RXG", "RXR", "TQ1", "TQ2"]) {
            let mut grp_give = RawGroup::new("GIVE");
            grp_give.push(RawSegment::from_tokens(&segments.expect("RXG")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_give.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing_give = RawGroup::new("TIMING_GIVE");
                grp_timing_give.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing_give.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_give.push_group(grp_timing_give);
            }
            grp_give.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_give.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_give.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CDO"]) {
                if let Some(s) = segments.optional("CDO") {
                    grp_give.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_give.push_group(grp_observation);
            }
            grp_order.push_group(grp_give);
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}
pub fn parse_rpa_i08(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RPA_I08");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("RF1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AUT", "CTD"]) {
        let mut grp_authorization = RawGroup::new("AUTHORIZATION");
        grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
        if let Some(s) = segments.optional("CTD") {
            grp_authorization.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_authorization);
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DRG"]) {
        if let Some(s) = segments.optional("DRG") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "CTD", "PR1"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        if segments.peek_matches_any(&["AUT", "CTD"]) {
            let mut grp_authorization = RawGroup::new("AUTHORIZATION");
            grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            if let Some(s) = segments.optional("CTD") {
                grp_authorization.push(RawSegment::from_tokens(&s));
            }
            grp_procedure.push_group(grp_authorization);
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_results = RawGroup::new("RESULTS");
            grp_results.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_results.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_results.push(RawSegment::from_tokens(&s));
                }
            }
            grp_observation.push_group(grp_results);
        }
        msg.push_group(grp_observation);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_visit);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rpi_i01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RPI_I01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["GT1", "IN1", "IN2", "IN3"]) {
        let mut grp_guarantor_insurance = RawGroup::new("GUARANTOR_INSURANCE");
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_guarantor_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_guarantor_insurance.push_group(grp_insurance);
        }
        msg.push_group(grp_guarantor_insurance);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rpi_i04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RPI_I04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["GT1", "IN1", "IN2", "IN3"]) {
        let mut grp_guarantor_insurance = RawGroup::new("GUARANTOR_INSURANCE");
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_guarantor_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_guarantor_insurance.push_group(grp_insurance);
        }
        msg.push_group(grp_guarantor_insurance);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rpl_i02(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RPL_I02");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DSP"]) {
        if let Some(s) = segments.optional("DSP") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rpr_i03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RPR_I03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    while segments.peek_matches_any(&["PID"]) {
        if let Some(s) = segments.optional("PID") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rqa_i08(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RQA_I08");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("RF1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AUT", "CTD"]) {
        let mut grp_authorization = RawGroup::new("AUTHORIZATION");
        grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
        if let Some(s) = segments.optional("CTD") {
            grp_authorization.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_authorization);
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["GT1", "IN1", "IN2", "IN3"]) {
        let mut grp_guarantor_insurance = RawGroup::new("GUARANTOR_INSURANCE");
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_guarantor_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_guarantor_insurance.push_group(grp_insurance);
        }
        msg.push_group(grp_guarantor_insurance);
    }
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DRG"]) {
        if let Some(s) = segments.optional("DRG") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "CTD", "PR1"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        if segments.peek_matches_any(&["AUT", "CTD"]) {
            let mut grp_authorization = RawGroup::new("AUTHORIZATION");
            grp_authorization.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            if let Some(s) = segments.optional("CTD") {
                grp_authorization.push(RawSegment::from_tokens(&s));
            }
            grp_procedure.push_group(grp_authorization);
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_results = RawGroup::new("RESULTS");
            grp_results.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_results.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_results.push(RawSegment::from_tokens(&s));
                }
            }
            grp_observation.push_group(grp_results);
        }
        msg.push_group(grp_observation);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_visit = RawGroup::new("VISIT");
        grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_visit);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rqi_i01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RQI_I01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["GT1", "IN1", "IN2", "IN3"]) {
        let mut grp_guarantor_insurance = RawGroup::new("GUARANTOR_INSURANCE");
        while segments.peek_matches_any(&["GT1"]) {
            if let Some(s) = segments.optional("GT1") {
                grp_guarantor_insurance.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
            let mut grp_insurance = RawGroup::new("INSURANCE");
            grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
            if let Some(s) = segments.optional("IN2") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("IN3") {
                grp_insurance.push(RawSegment::from_tokens(&s));
            }
            grp_guarantor_insurance.push_group(grp_insurance);
        }
        msg.push_group(grp_guarantor_insurance);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rqp_i04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RQP_I04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider = RawGroup::new("PROVIDER");
        grp_provider.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rra_o18(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RRA_O18");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "ORC", "PID", "PRT", "RXA", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["ORC", "PRT", "RXA", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["PRT", "RXA", "RXR"]) {
                let mut grp_administration = RawGroup::new("ADMINISTRATION");
                while segments.peek_matches_any(&["PRT", "RXA"]) {
                    let mut grp_treatment = RawGroup::new("TREATMENT");
                    grp_treatment.push(RawSegment::from_tokens(&segments.expect("RXA")?));
                    while segments.peek_matches_any(&["PRT"]) {
                        if let Some(s) = segments.optional("PRT") {
                            grp_treatment.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_administration.push_group(grp_treatment);
                }
                grp_administration.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                grp_order.push_group(grp_administration);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_rrd_o14(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RRD_O14");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "ORC", "PID", "PRT", "RXC", "RXD", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT", "RXC", "RXD", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXD", "RXR"]) {
                let mut grp_dispense = RawGroup::new("DISPENSE");
                grp_dispense.push(RawSegment::from_tokens(&segments.expect("RXD")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_dispense.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_dispense);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_rre_o12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RRE_O12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "ORC", "PID", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_encoding = RawGroup::new("ENCODING");
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_encoding.push_group(grp_timing_encoded);
                }
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_encoding);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_rre_o50(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RRE_O50");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "ORC", "PID", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "ORC", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_encoding = RawGroup::new("ENCODING");
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_encoding.push_group(grp_timing_encoded);
                }
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_encoding);
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_rrg_o16(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RRG_O16");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["NTE", "ORC", "PID", "PRT", "RXC", "RXG", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["NTE", "PID", "PRT"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["ORC", "PRT", "RXC", "RXG", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["PRT", "RXC", "RXG", "RXR", "TQ1", "TQ2"]) {
                let mut grp_give = RawGroup::new("GIVE");
                grp_give.push(RawSegment::from_tokens(&segments.expect("RXG")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_give.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_give = RawGroup::new("TIMING_GIVE");
                    grp_timing_give.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_give.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_give.push_group(grp_timing_give);
                }
                grp_give.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_give.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_give.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_give);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    Ok(msg)
}
pub fn parse_rri_i12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RRI_I12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("MSA") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("RF1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if segments.peek_matches_any(&["AUT", "CTD"]) {
        let mut grp_authorization_contact2 = RawGroup::new("AUTHORIZATION_CONTACT2");
        grp_authorization_contact2.push(RawSegment::from_tokens(&segments.expect("AUT")?));
        if let Some(s) = segments.optional("CTD") {
            grp_authorization_contact2.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_authorization_contact2);
    }
    while segments.peek_matches_any(&["CTD", "PRD"]) {
        let mut grp_provider_contact = RawGroup::new("PROVIDER_CONTACT");
        grp_provider_contact.push(RawSegment::from_tokens(&segments.expect("PRD")?));
        while segments.peek_matches_any(&["CTD"]) {
            if let Some(s) = segments.optional("CTD") {
                grp_provider_contact.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_provider_contact);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("ACC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["DG1"]) {
        if let Some(s) = segments.optional("DG1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DRG"]) {
        if let Some(s) = segments.optional("DRG") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AL1"]) {
        if let Some(s) = segments.optional("AL1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["AUT", "CTD", "PR1"]) {
        let mut grp_procedure = RawGroup::new("PROCEDURE");
        grp_procedure.push(RawSegment::from_tokens(&segments.expect("PR1")?));
        if segments.peek_matches_any(&["AUT", "CTD"]) {
            let mut grp_authorization_contact2 = RawGroup::new("AUTHORIZATION_CONTACT2");
            grp_authorization_contact2.push(RawSegment::from_tokens(&segments.expect("AUT")?));
            if let Some(s) = segments.optional("CTD") {
                grp_authorization_contact2.push(RawSegment::from_tokens(&s));
            }
            grp_procedure.push_group(grp_authorization_contact2);
        }
        msg.push_group(grp_procedure);
    }
    while segments.peek_matches_any(&["NTE", "OBR", "OBX", "PRT"]) {
        let mut grp_observation = RawGroup::new("OBSERVATION");
        grp_observation.push(RawSegment::from_tokens(&segments.expect("OBR")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_results_notes = RawGroup::new("RESULTS_NOTES");
            grp_results_notes.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_results_notes.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_results_notes.push(RawSegment::from_tokens(&s));
                }
            }
            grp_observation.push_group(grp_results_notes);
        }
        msg.push_group(grp_observation);
    }
    if segments.peek_matches_any(&["PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_rsp_e03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_E03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_rsp_e22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_E22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["UAC"]) {
        if let Some(s) = segments.optional("UAC") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }

    Ok(msg)
}
pub fn parse_rsp_k11(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K11");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["anyHL7Segment"]) {
        let mut grp_segment_pattern = RawGroup::new("SEGMENT_PATTERN");
        grp_segment_pattern.push(RawSegment::from_tokens(&segments.expect("anyHL7Segment")?));
        msg.push_group(grp_segment_pattern);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_k21(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K21");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["ARV", "NK1", "PD1", "PID", "QRI"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        grp_query_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_query_response.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_query_response.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_query_response.push(RawSegment::from_tokens(&s));
            }
        }
        grp_query_response.push(RawSegment::from_tokens(&segments.expect("QRI")?));
        msg.push_group(grp_query_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_k22(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K22");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    while segments.peek_matches_any(&["NK1", "PD1", "PID", "QRI"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        grp_query_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_query_response.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_query_response.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("QRI") {
            grp_query_response.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_query_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_k23(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K23");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["PID"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        grp_query_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        msg.push_group(grp_query_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_k25(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K25");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    while segments.peek_matches_any(&["AFF", "CER", "EDU", "LAN", "NK1", "ORG", "PRA", "PRT", "ROL", "STF"]) {
        let mut grp_staff = RawGroup::new("STAFF");
        grp_staff.push(RawSegment::from_tokens(&segments.expect("STF")?));
        while segments.peek_matches_any(&["PRA"]) {
            if let Some(s) = segments.optional("PRA") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ORG"]) {
            if let Some(s) = segments.optional("ORG") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AFF"]) {
            if let Some(s) = segments.optional("AFF") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["LAN"]) {
            if let Some(s) = segments.optional("LAN") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["EDU"]) {
            if let Some(s) = segments.optional("EDU") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["CER"]) {
            if let Some(s) = segments.optional("CER") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ROL"]) {
            if let Some(s) = segments.optional("ROL") {
                grp_staff.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_staff);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_k31(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K31");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    while segments.peek_matches_any(&["AL1", "ARV", "CDO", "NTE", "OBX", "ORC", "PD1", "PID", "PRT", "PV1", "PV2", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_response = RawGroup::new("RESPONSE");
        if segments.peek_matches_any(&["AL1", "ARV", "NTE", "PD1", "PID", "PRT", "PV1", "PV2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["ARV"]) {
                if let Some(s) = segments.optional("ARV") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["AL1"]) {
                if let Some(s) = segments.optional("AL1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
                let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
                grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_patient_visit.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_patient_visit.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["ARV"]) {
                    if let Some(s) = segments.optional("ARV") {
                        grp_patient_visit.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_patient.push_group(grp_patient_visit);
            }
            grp_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["CDO", "NTE", "OBX", "ORC", "PRT", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
            let mut grp_order = RawGroup::new("ORDER");
            grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXO", "RXR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_components = RawGroup::new("COMPONENTS");
                    grp_components.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_components.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail.push_group(grp_components);
                }
                grp_order.push_group(grp_order_detail);
            }
            if segments.peek_matches_any(&["NTE", "PRT", "RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_encoding = RawGroup::new("ENCODING");
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_encoding.push_group(grp_timing_encoded);
                }
                grp_encoding.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_encoding.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_encoding);
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("RXD")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["CDO"]) {
                if let Some(s) = segments.optional("CDO") {
                    grp_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
                while segments.peek_matches_any(&["PRT"]) {
                    if let Some(s) = segments.optional("PRT") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order.push_group(grp_observation);
            }
            grp_response.push_group(grp_order);
        }
        msg.push_group(grp_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_k32(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_K32");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    while segments.peek_matches_any(&["NK1", "PD1", "PID", "PV1", "PV2", "QRI"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        grp_query_response.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_query_response.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NK1"]) {
            if let Some(s) = segments.optional("NK1") {
                grp_query_response.push(RawSegment::from_tokens(&s));
            }
        }
        grp_query_response.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_query_response.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("QRI") {
            grp_query_response.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_query_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_o33(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_O33");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["ARV", "PID", "PRT"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donor);
    }
    Ok(msg)
}
pub fn parse_rsp_o34(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_O34");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["AL1", "ARV", "NTE", "OBX", "PD1", "PID", "PRT", "PV1"]) {
        let mut grp_donor = RawGroup::new("DONOR");
        grp_donor.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_donor.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["AL1"]) {
            if let Some(s) = segments.optional("AL1") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_donor.push(RawSegment::from_tokens(&s));
            }
        }
        if segments.peek_matches_any(&["NTE", "PRT", "PV1"]) {
            let mut grp_donor_registration = RawGroup::new("DONOR_REGISTRATION");
            grp_donor_registration.push(RawSegment::from_tokens(&segments.expect("PV1")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_donor_registration.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donor.push_group(grp_donor_registration);
        }
        msg.push_group(grp_donor);
    }
    if segments.peek_matches_any(&["DON", "NTE", "OBX", "PRT"]) {
        let mut grp_donation = RawGroup::new("DONATION");
        grp_donation.push(RawSegment::from_tokens(&segments.expect("DON")?));
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_donor_observations = RawGroup::new("DONOR_OBSERVATIONS");
            grp_donor_observations.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_donor_observations.push(RawSegment::from_tokens(&s));
                }
            }
            grp_donation.push_group(grp_donor_observations);
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_donation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_donation);
    }
    Ok(msg)
}
pub fn parse_rsp_z82(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_Z82");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    while segments.peek_matches_any(&["AL1", "NTE", "OBX", "ORC", "PD1", "PID", "PV1", "PV2", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        if segments.peek_matches_any(&["AL1", "NTE", "PD1", "PID", "PV1", "PV2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["AL1", "PV1", "PV2"]) {
                let mut grp_visit = RawGroup::new("VISIT");
                grp_visit.push(RawSegment::from_tokens(&segments.expect("AL1")?));
                while segments.peek_matches_any(&["AL1"]) {
                    if let Some(s) = segments.optional("AL1") {
                        grp_visit.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
                grp_patient.push_group(grp_visit);
            }
            grp_query_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "ORC", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
            let mut grp_common_order = RawGroup::new("COMMON_ORDER");
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "RXC", "RXO", "RXR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_treatment = RawGroup::new("TREATMENT");
                    grp_treatment.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["RXC"]) {
                        if let Some(s) = segments.optional("RXC") {
                            grp_treatment.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_treatment.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail.push_group(grp_treatment);
                }
                grp_common_order.push_group(grp_order_detail);
            }
            if segments.peek_matches_any(&["RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_encoded_order = RawGroup::new("ENCODED_ORDER");
                grp_encoded_order.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_encoded_order.push_group(grp_timing_encoded);
                }
                grp_encoded_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_encoded_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_encoded_order.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_encoded_order);
            }
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("RXD")?));
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                if let Some(s) = segments.optional("OBX") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_observation);
            }
            grp_query_response.push_group(grp_common_order);
        }
        msg.push_group(grp_query_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_z84(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_Z84");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["RDF", "RDT"]) {
        let mut grp_row_definition = RawGroup::new("ROW_DEFINITION");
        grp_row_definition.push(RawSegment::from_tokens(&segments.expect("RDF")?));
        while segments.peek_matches_any(&["RDT"]) {
            if let Some(s) = segments.optional("RDT") {
                grp_row_definition.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_row_definition);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_z86(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_Z86");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    while segments.peek_matches_any(&["AL1", "NTE", "OBX", "ORC", "PD1", "PID", "RXA", "RXC", "RXD", "RXE", "RXG", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        if segments.peek_matches_any(&["AL1", "NTE", "PD1", "PID"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["AL1"]) {
                if let Some(s) = segments.optional("AL1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_query_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "ORC", "RXA", "RXC", "RXD", "RXE", "RXG", "RXO", "RXR", "TQ1", "TQ2"]) {
            let mut grp_common_order = RawGroup::new("COMMON_ORDER");
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["RXC", "RXO", "RXR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_order_detail);
            }
            if segments.peek_matches_any(&["RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_encoded_order = RawGroup::new("ENCODED_ORDER");
                grp_encoded_order.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_encoded_order.push_group(grp_timing_encoded);
                }
                grp_encoded_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_encoded_order.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_encoded_order.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_encoded_order);
            }
            if segments.peek_matches_any(&["RXC", "RXD", "RXR"]) {
                let mut grp_dispense = RawGroup::new("DISPENSE");
                grp_dispense.push(RawSegment::from_tokens(&segments.expect("RXD")?));
                grp_dispense.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_dispense.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_dispense);
            }
            if segments.peek_matches_any(&["RXC", "RXG", "RXR"]) {
                let mut grp_give = RawGroup::new("GIVE");
                grp_give.push(RawSegment::from_tokens(&segments.expect("RXG")?));
                grp_give.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_give.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_give.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_give);
            }
            if segments.peek_matches_any(&["RXA", "RXC", "RXR"]) {
                let mut grp_administration = RawGroup::new("ADMINISTRATION");
                grp_administration.push(RawSegment::from_tokens(&segments.expect("RXA")?));
                grp_administration.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_administration.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_administration.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_administration);
            }
            while segments.peek_matches_any(&["NTE", "OBX"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                if let Some(s) = segments.optional("OBX") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_observation);
            }
            grp_query_response.push_group(grp_common_order);
        }
        msg.push_group(grp_query_response);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rsp_z88(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_Z88");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    while segments.peek_matches_any(&["AL1", "NTE", "OBX", "ORC", "PD1", "PID", "PV1", "PV2", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        if segments.peek_matches_any(&["AL1", "NTE", "PD1", "PID", "PV1", "PV2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["AL1", "PV1", "PV2"]) {
                let mut grp_allergy = RawGroup::new("ALLERGY");
                grp_allergy.push(RawSegment::from_tokens(&segments.expect("AL1")?));
                while segments.peek_matches_any(&["AL1"]) {
                    if let Some(s) = segments.optional("AL1") {
                        grp_allergy.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["PV1", "PV2"]) {
                    let mut grp_visit = RawGroup::new("VISIT");
                    grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                    if let Some(s) = segments.optional("PV2") {
                        grp_visit.push(RawSegment::from_tokens(&s));
                    }
                    grp_allergy.push_group(grp_visit);
                }
                grp_patient.push_group(grp_allergy);
            }
            grp_query_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["NTE", "OBX", "ORC", "RXC", "RXD", "RXE", "RXO", "RXR", "TQ1", "TQ2"]) {
            let mut grp_common_order = RawGroup::new("COMMON_ORDER");
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_timing);
            }
            if segments.peek_matches_any(&["NTE", "RXC", "RXO", "RXR"]) {
                let mut grp_order_detail = RawGroup::new("ORDER_DETAIL");
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXO")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_order_detail.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_detail.push(RawSegment::from_tokens(&s));
                    }
                }
                if segments.peek_matches_any(&["NTE", "RXC"]) {
                    let mut grp_component = RawGroup::new("COMPONENT");
                    grp_component.push(RawSegment::from_tokens(&segments.expect("RXC")?));
                    while segments.peek_matches_any(&["RXC"]) {
                        if let Some(s) = segments.optional("RXC") {
                            grp_component.push(RawSegment::from_tokens(&s));
                        }
                    }
                    while segments.peek_matches_any(&["NTE"]) {
                        if let Some(s) = segments.optional("NTE") {
                            grp_component.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_detail.push_group(grp_component);
                }
                grp_common_order.push_group(grp_order_detail);
            }
            if segments.peek_matches_any(&["RXC", "RXE", "RXR", "TQ1", "TQ2"]) {
                let mut grp_order_encoded = RawGroup::new("ORDER_ENCODED");
                grp_order_encoded.push(RawSegment::from_tokens(&segments.expect("RXE")?));
                while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                    let mut grp_timing_encoded = RawGroup::new("TIMING_ENCODED");
                    grp_timing_encoded.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                    while segments.peek_matches_any(&["TQ2"]) {
                        if let Some(s) = segments.optional("TQ2") {
                            grp_timing_encoded.push(RawSegment::from_tokens(&s));
                        }
                    }
                    grp_order_encoded.push_group(grp_timing_encoded);
                }
                grp_order_encoded.push(RawSegment::from_tokens(&segments.expect("RXR")?));
                while segments.peek_matches_any(&["RXR"]) {
                    if let Some(s) = segments.optional("RXR") {
                        grp_order_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                while segments.peek_matches_any(&["RXC"]) {
                    if let Some(s) = segments.optional("RXC") {
                        grp_order_encoded.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_order_encoded);
            }
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("RXD")?));
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("RXR")?));
            while segments.peek_matches_any(&["RXR"]) {
                if let Some(s) = segments.optional("RXR") {
                    grp_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["RXC"]) {
                if let Some(s) = segments.optional("RXC") {
                    grp_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE", "OBX"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                if let Some(s) = segments.optional("OBX") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_observation);
            }
            grp_query_response.push_group(grp_common_order);
        }
        msg.push_group(grp_query_response);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("DSC")?));
    Ok(msg)
}
pub fn parse_rsp_z90(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_Z90");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("RCP")?));
    while segments.peek_matches_any(&["CTD", "NK1", "NTE", "OBR", "OBX", "ORC", "PD1", "PID", "PV1", "PV2", "SPM", "TQ1", "TQ2"]) {
        let mut grp_query_response = RawGroup::new("QUERY_RESPONSE");
        if segments.peek_matches_any(&["NK1", "NTE", "PD1", "PID", "PV1", "PV2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            if let Some(s) = segments.optional("PD1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NK1"]) {
                if let Some(s) = segments.optional("NK1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if segments.peek_matches_any(&["PV1", "PV2"]) {
                let mut grp_visit = RawGroup::new("VISIT");
                grp_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
                if let Some(s) = segments.optional("PV2") {
                    grp_visit.push(RawSegment::from_tokens(&s));
                }
                grp_patient.push_group(grp_visit);
            }
            grp_query_response.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["CTD", "NTE", "OBR", "OBX", "ORC", "TQ1", "TQ2"]) {
            let mut grp_common_order = RawGroup::new("COMMON_ORDER");
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
            while segments.peek_matches_any(&["TQ1", "TQ2"]) {
                let mut grp_timing = RawGroup::new("TIMING");
                grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
                while segments.peek_matches_any(&["TQ2"]) {
                    if let Some(s) = segments.optional("TQ2") {
                        grp_timing.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_timing);
            }
            grp_common_order.push(RawSegment::from_tokens(&segments.expect("OBR")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_common_order.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("CTD") {
                grp_common_order.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE", "OBX"]) {
                let mut grp_observation = RawGroup::new("OBSERVATION");
                if let Some(s) = segments.optional("OBX") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_observation.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_common_order.push_group(grp_observation);
            }
            grp_query_response.push_group(grp_common_order);
        }
        while segments.peek_matches_any(&["OBX", "SPM"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX"]) {
                if let Some(s) = segments.optional("OBX") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            grp_query_response.push_group(grp_specimen);
        }
        msg.push_group(grp_query_response);
    }
    msg.push(RawSegment::from_tokens(&segments.expect("DSC")?));
    Ok(msg)
}
pub fn parse_rsp_znn(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RSP_Znn");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if let Some(s) = segments.optional("anyHL7Segment") {
        msg.push(RawSegment::from_tokens(&s));
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rtb_k13(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RTB_K13");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["RDF", "RDT"]) {
        let mut grp_row_definition = RawGroup::new("ROW_DEFINITION");
        grp_row_definition.push(RawSegment::from_tokens(&segments.expect("RDF")?));
        while segments.peek_matches_any(&["RDT"]) {
            if let Some(s) = segments.optional("RDT") {
                grp_row_definition.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_row_definition);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rtb_knn(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RTB_Knn");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    if let Some(s) = segments.optional("ERR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    msg.push(RawSegment::from_tokens(&segments.expect("anyHL7Segment")?));
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_rtb_z74(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("RTB_Z74");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("QAK")?));
    msg.push(RawSegment::from_tokens(&segments.expect("QPD")?));
    if segments.peek_matches_any(&["RDF", "RDT"]) {
        let mut grp_row_definition = RawGroup::new("ROW_DEFINITION");
        grp_row_definition.push(RawSegment::from_tokens(&segments.expect("RDF")?));
        while segments.peek_matches_any(&["RDT"]) {
            if let Some(s) = segments.optional("RDT") {
                grp_row_definition.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_row_definition);
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_sdr_s31(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SDR_S31");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }

    Ok(msg)
}
pub fn parse_sdr_s32(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SDR_S32");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }

    Ok(msg)
}
pub fn parse_siu_s12(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SIU_S12");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("SCH")?));
    while segments.peek_matches_any(&["TQ1"]) {
        if let Some(s) = segments.optional("TQ1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1", "OBX", "PD1", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        if let Some(s) = segments.optional("PD1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("PV1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("PV2") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DG1"]) {
            if let Some(s) = segments.optional("DG1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AIG", "AIL", "AIP", "AIS", "NTE", "RGS"]) {
        let mut grp_resources = RawGroup::new("RESOURCES");
        grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
        while segments.peek_matches_any(&["AIS", "NTE"]) {
            let mut grp_service = RawGroup::new("SERVICE");
            grp_service.push(RawSegment::from_tokens(&segments.expect("AIS")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_service.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_service);
        }
        while segments.peek_matches_any(&["AIG", "NTE"]) {
            let mut grp_general_resource = RawGroup::new("GENERAL_RESOURCE");
            grp_general_resource.push(RawSegment::from_tokens(&segments.expect("AIG")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_general_resource.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_general_resource);
        }
        while segments.peek_matches_any(&["AIL", "NTE"]) {
            let mut grp_location_resource = RawGroup::new("LOCATION_RESOURCE");
            grp_location_resource.push(RawSegment::from_tokens(&segments.expect("AIL")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_location_resource.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_location_resource);
        }
        while segments.peek_matches_any(&["AIP", "NTE"]) {
            let mut grp_personnel_resource = RawGroup::new("PERSONNEL_RESOURCE");
            grp_personnel_resource.push(RawSegment::from_tokens(&segments.expect("AIP")?));
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_personnel_resource.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_personnel_resource);
        }
        msg.push_group(grp_resources);
    }
    Ok(msg)
}
pub fn parse_slr_s28(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SLR_S28");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("SLT")?));
    while segments.peek_matches_any(&["SLT"]) {
        if let Some(s) = segments.optional("SLT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_srm_s01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SRM_S01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("ARQ")?));
    if let Some(s) = segments.optional("APR") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["NTE"]) {
        if let Some(s) = segments.optional("NTE") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["DG1", "OBX", "PID", "PRT", "PV1", "PV2"]) {
        let mut grp_patient = RawGroup::new("PATIENT");
        grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("PV1") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("PV2") {
            grp_patient.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_patient.push_group(grp_observation);
        }
        while segments.peek_matches_any(&["DG1"]) {
            if let Some(s) = segments.optional("DG1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient);
    }
    while segments.peek_matches_any(&["AIG", "AIL", "AIP", "AIS", "APR", "NTE", "RGS"]) {
        let mut grp_resources = RawGroup::new("RESOURCES");
        grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
        while segments.peek_matches_any(&["AIS", "APR", "NTE"]) {
            let mut grp_service = RawGroup::new("SERVICE");
            grp_service.push(RawSegment::from_tokens(&segments.expect("AIS")?));
            if let Some(s) = segments.optional("APR") {
                grp_service.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_service.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_service);
        }
        while segments.peek_matches_any(&["AIG", "APR", "NTE"]) {
            let mut grp_general_resource = RawGroup::new("GENERAL_RESOURCE");
            grp_general_resource.push(RawSegment::from_tokens(&segments.expect("AIG")?));
            if let Some(s) = segments.optional("APR") {
                grp_general_resource.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_general_resource.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_general_resource);
        }
        while segments.peek_matches_any(&["AIL", "APR", "NTE"]) {
            let mut grp_location_resource = RawGroup::new("LOCATION_RESOURCE");
            grp_location_resource.push(RawSegment::from_tokens(&segments.expect("AIL")?));
            if let Some(s) = segments.optional("APR") {
                grp_location_resource.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_location_resource.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_location_resource);
        }
        while segments.peek_matches_any(&["AIP", "APR", "NTE"]) {
            let mut grp_personnel_resource = RawGroup::new("PERSONNEL_RESOURCE");
            grp_personnel_resource.push(RawSegment::from_tokens(&segments.expect("AIP")?));
            if let Some(s) = segments.optional("APR") {
                grp_personnel_resource.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_personnel_resource.push(RawSegment::from_tokens(&s));
                }
            }
            grp_resources.push_group(grp_personnel_resource);
        }
        msg.push_group(grp_resources);
    }
    Ok(msg)
}
pub fn parse_srr_s01(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SRR_S01");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    msg.push(RawSegment::from_tokens(&segments.expect("MSA")?));
    while segments.peek_matches_any(&["ERR"]) {
        if let Some(s) = segments.optional("ERR") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["AIG", "AIL", "AIP", "AIS", "DG1", "NTE", "PID", "PRT", "PV1", "PV2", "RGS", "SCH", "TQ1"]) {
        let mut grp_schedule = RawGroup::new("SCHEDULE");
        grp_schedule.push(RawSegment::from_tokens(&segments.expect("SCH")?));
        while segments.peek_matches_any(&["TQ1"]) {
            if let Some(s) = segments.optional("TQ1") {
                grp_schedule.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_schedule.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["DG1", "PID", "PRT", "PV1", "PV2"]) {
            let mut grp_patient = RawGroup::new("PATIENT");
            grp_patient.push(RawSegment::from_tokens(&segments.expect("PID")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            if let Some(s) = segments.optional("PV1") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            if let Some(s) = segments.optional("PV2") {
                grp_patient.push(RawSegment::from_tokens(&s));
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["DG1"]) {
                if let Some(s) = segments.optional("DG1") {
                    grp_patient.push(RawSegment::from_tokens(&s));
                }
            }
            grp_schedule.push_group(grp_patient);
        }
        while segments.peek_matches_any(&["AIG", "AIL", "AIP", "AIS", "NTE", "RGS"]) {
            let mut grp_resources = RawGroup::new("RESOURCES");
            grp_resources.push(RawSegment::from_tokens(&segments.expect("RGS")?));
            while segments.peek_matches_any(&["AIS", "NTE"]) {
                let mut grp_service = RawGroup::new("SERVICE");
                grp_service.push(RawSegment::from_tokens(&segments.expect("AIS")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_service.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_resources.push_group(grp_service);
            }
            while segments.peek_matches_any(&["AIG", "NTE"]) {
                let mut grp_general_resource = RawGroup::new("GENERAL_RESOURCE");
                grp_general_resource.push(RawSegment::from_tokens(&segments.expect("AIG")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_general_resource.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_resources.push_group(grp_general_resource);
            }
            while segments.peek_matches_any(&["AIL", "NTE"]) {
                let mut grp_location_resource = RawGroup::new("LOCATION_RESOURCE");
                grp_location_resource.push(RawSegment::from_tokens(&segments.expect("AIL")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_location_resource.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_resources.push_group(grp_location_resource);
            }
            while segments.peek_matches_any(&["AIP", "NTE"]) {
                let mut grp_personnel_resource = RawGroup::new("PERSONNEL_RESOURCE");
                grp_personnel_resource.push(RawSegment::from_tokens(&segments.expect("AIP")?));
                while segments.peek_matches_any(&["NTE"]) {
                    if let Some(s) = segments.optional("NTE") {
                        grp_personnel_resource.push(RawSegment::from_tokens(&s));
                    }
                }
                grp_resources.push_group(grp_personnel_resource);
            }
            grp_schedule.push_group(grp_resources);
        }
        msg.push_group(grp_schedule);
    }
    Ok(msg)
}
pub fn parse_ssr_u04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SSR_U04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["SAC", "SPM"]) {
        let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
        grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
        while segments.peek_matches_any(&["SPM"]) {
            if let Some(s) = segments.optional("SPM") {
                grp_specimen_container.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_specimen_container);
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_ssu_u03(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("SSU_U03");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["NTE", "OBX", "PRT", "SAC", "SPM"]) {
        let mut grp_specimen_container = RawGroup::new("SPECIMEN_CONTAINER");
        grp_specimen_container.push(RawSegment::from_tokens(&segments.expect("SAC")?));
        while segments.peek_matches_any(&["OBX"]) {
            if let Some(s) = segments.optional("OBX") {
                grp_specimen_container.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_specimen_container.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_specimen_container.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["OBX", "PRT", "SPM"]) {
            let mut grp_specimen = RawGroup::new("SPECIMEN");
            grp_specimen.push(RawSegment::from_tokens(&segments.expect("SPM")?));
            while segments.peek_matches_any(&["OBX"]) {
                if let Some(s) = segments.optional("OBX") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_specimen.push(RawSegment::from_tokens(&s));
                }
            }
            grp_specimen_container.push_group(grp_specimen);
        }
        msg.push_group(grp_specimen_container);
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_stc_s33(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("STC_S33");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("SCP")?));
    while segments.peek_matches_any(&["SCP"]) {
        if let Some(s) = segments.optional("SCP") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    Ok(msg)
}
pub fn parse_tcu_u10(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("TCU_U10");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("EQU")?));
    while segments.peek_matches_any(&["SPM", "TCC"]) {
        let mut grp_test_configuration = RawGroup::new("TEST_CONFIGURATION");
        if let Some(s) = segments.optional("SPM") {
            grp_test_configuration.push(RawSegment::from_tokens(&s));
        }
        grp_test_configuration.push(RawSegment::from_tokens(&segments.expect("TCC")?));
        while segments.peek_matches_any(&["TCC"]) {
            if let Some(s) = segments.optional("TCC") {
                grp_test_configuration.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_test_configuration);
    }
    if let Some(s) = segments.optional("ROL") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_udm_q05(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("UDM_Q05");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("URD")?));
    if let Some(s) = segments.optional("URS") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("DSP")?));
    while segments.peek_matches_any(&["DSP"]) {
        if let Some(s) = segments.optional("DSP") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("DSC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    Ok(msg)
}
pub fn parse_vxu_v04(
    segments: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    let mut msg = RawMessage::new("VXU_V04");
        msg.push(RawSegment::from_tokens(&segments.expect("MSH")?));
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["SFT"]) {
        if let Some(s) = segments.optional("SFT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if let Some(s) = segments.optional("UAC") {
        msg.push(RawSegment::from_tokens(&s));
    }
    msg.push(RawSegment::from_tokens(&segments.expect("PID")?));
    if let Some(s) = segments.optional("PD1") {
        msg.push(RawSegment::from_tokens(&s));
    }
    while segments.peek_matches_any(&["PRT"]) {
        if let Some(s) = segments.optional("PRT") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["NK1"]) {
        if let Some(s) = segments.optional("NK1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["ARV"]) {
        if let Some(s) = segments.optional("ARV") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    if segments.peek_matches_any(&["ARV", "PRT", "PV1", "PV2"]) {
        let mut grp_patient_visit = RawGroup::new("PATIENT_VISIT");
        grp_patient_visit.push(RawSegment::from_tokens(&segments.expect("PV1")?));
        if let Some(s) = segments.optional("PV2") {
            grp_patient_visit.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["ARV"]) {
            if let Some(s) = segments.optional("ARV") {
                grp_patient_visit.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_patient_visit);
    }
    while segments.peek_matches_any(&["GT1"]) {
        if let Some(s) = segments.optional("GT1") {
            msg.push(RawSegment::from_tokens(&s));
        }
    }
    while segments.peek_matches_any(&["IN1", "IN2", "IN3"]) {
        let mut grp_insurance = RawGroup::new("INSURANCE");
        grp_insurance.push(RawSegment::from_tokens(&segments.expect("IN1")?));
        if let Some(s) = segments.optional("IN2") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        if let Some(s) = segments.optional("IN3") {
            grp_insurance.push(RawSegment::from_tokens(&s));
        }
        msg.push_group(grp_insurance);
    }
    while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
        let mut grp_person_observation = RawGroup::new("PERSON_OBSERVATION");
        grp_person_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_person_observation.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["NTE"]) {
            if let Some(s) = segments.optional("NTE") {
                grp_person_observation.push(RawSegment::from_tokens(&s));
            }
        }
        msg.push_group(grp_person_observation);
    }
    while segments.peek_matches_any(&["NTE", "OBX", "ORC", "PRT", "RXA", "RXR", "TQ1", "TQ2"]) {
        let mut grp_order = RawGroup::new("ORDER");
        grp_order.push(RawSegment::from_tokens(&segments.expect("ORC")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        while segments.peek_matches_any(&["TQ1", "TQ2"]) {
            let mut grp_timing = RawGroup::new("TIMING");
            grp_timing.push(RawSegment::from_tokens(&segments.expect("TQ1")?));
            while segments.peek_matches_any(&["TQ2"]) {
                if let Some(s) = segments.optional("TQ2") {
                    grp_timing.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_timing);
        }
        grp_order.push(RawSegment::from_tokens(&segments.expect("RXA")?));
        while segments.peek_matches_any(&["PRT"]) {
            if let Some(s) = segments.optional("PRT") {
                grp_order.push(RawSegment::from_tokens(&s));
            }
        }
        if let Some(s) = segments.optional("RXR") {
            grp_order.push(RawSegment::from_tokens(&s));
        }
        while segments.peek_matches_any(&["NTE", "OBX", "PRT"]) {
            let mut grp_observation = RawGroup::new("OBSERVATION");
            grp_observation.push(RawSegment::from_tokens(&segments.expect("OBX")?));
            while segments.peek_matches_any(&["PRT"]) {
                if let Some(s) = segments.optional("PRT") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            while segments.peek_matches_any(&["NTE"]) {
                if let Some(s) = segments.optional("NTE") {
                    grp_observation.push(RawSegment::from_tokens(&s));
                }
            }
            grp_order.push_group(grp_observation);
        }
        msg.push_group(grp_order);
    }
    Ok(msg)
}

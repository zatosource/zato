// Generated - do not edit
use crate::{RawFields, RawFieldsExt, RawSegment};

pub fn parse_abs(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ABS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_acc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ACC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
        ],
    }
}
pub fn parse_add(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ADD".to_string(),
        fields: vec![
raw.get_field(1),
        ],
    }
}
pub fn parse_adj(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ADJ".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
        ],
    }
}
pub fn parse_aff(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AFF".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_aig(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AIG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_ail(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AIL".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_aip(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AIP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_ais(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AIS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_repeating_field(12),
        ],
    }
}
pub fn parse_al1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AL1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
        ],
    }
}
pub fn parse_apr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "APR".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
        ],
    }
}
pub fn parse_arq(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ARQ".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
raw.get_field(18),
raw.get_repeating_field(19),
raw.get_repeating_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_repeating_field(25),
raw.get_field(26),
        ],
    }
}
pub fn parse_arv(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ARV".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
        ],
    }
}
pub fn parse_aut(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "AUT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_repeating_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
        ],
    }
}
pub fn parse_bhs(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BHS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
        ],
    }
}
pub fn parse_blc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BLC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_blg(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BLG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_bpo(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BPO".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_bpx(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BPX".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_repeating_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
        ],
    }
}
pub fn parse_bts(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BTS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
        ],
    }
}
pub fn parse_btx(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BTX".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
        ],
    }
}
pub fn parse_bui(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "BUI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
        ],
    }
}
pub fn parse_cdm(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CDM".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_repeating_field(12),
raw.get_field(13),
        ],
    }
}
pub fn parse_cdo(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CDO".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_cer(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CER".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_repeating_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
        ],
    }
}
pub fn parse_cm0(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CM0".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
        ],
    }
}
pub fn parse_cm1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CM1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_cm2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CM2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_cns(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CNS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_con(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CON".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_repeating_field(25),
        ],
    }
}
pub fn parse_csp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CSP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_csr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CSR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
        ],
    }
}
pub fn parse_css(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CSS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_ctd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CTD".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
        ],
    }
}
pub fn parse_cti(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CTI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_ctr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "CTR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
        ],
    }
}
pub fn parse_db1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DB1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
        ],
    }
}
pub fn parse_dev(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DEV".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
        ],
    }
}
pub fn parse_dg1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DG1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(3),
raw.get_field(5),
raw.get_field(6),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
        ],
    }
}
pub fn parse_dmi(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DMI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_don(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DON".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_repeating_field(31),
raw.get_field(32),
raw.get_repeating_field(33),
raw.get_field(34),
        ],
    }
}
pub fn parse_dps(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DPS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_drg(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DRG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
        ],
    }
}
pub fn parse_dsc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DSC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_dsp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DSP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_dst(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "DST".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
        ],
    }
}
pub fn parse_ecd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ECD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_repeating_field(5),
        ],
    }
}
pub fn parse_ecr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ECR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
        ],
    }
}
pub fn parse_edu(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "EDU".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
        ],
    }
}
pub fn parse_eqp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "EQP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_equ(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "EQU".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_err(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ERR".to_string(),
        fields: vec![
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_repeating_field(12),
        ],
    }
}
pub fn parse_evn(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "EVN".to_string(),
        fields: vec![
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_fac(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "FAC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_fhs(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "FHS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
        ],
    }
}
pub fn parse_ft1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "FT1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_repeating_field(19),
raw.get_repeating_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_field(25),
raw.get_repeating_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_repeating_field(31),
raw.get_repeating_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_repeating_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_field(40),
raw.get_field(41),
raw.get_field(42),
raw.get_field(43),
raw.get_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_field(49),
raw.get_field(50),
raw.get_field(51),
raw.get_field(52),
raw.get_field(53),
raw.get_field(54),
raw.get_field(55),
raw.get_field(56),
        ],
    }
}
pub fn parse_fts(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "FTS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_gol(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "GOL".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(16),
raw.get_repeating_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_repeating_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
        ],
    }
}
pub fn parse_gp1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "GP1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_gp2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "GP2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_gt1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "GT1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
raw.get_repeating_field(18),
raw.get_repeating_field(19),
raw.get_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_repeating_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_repeating_field(34),
raw.get_repeating_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_field(40),
raw.get_field(41),
raw.get_repeating_field(42),
raw.get_field(43),
raw.get_repeating_field(44),
raw.get_repeating_field(45),
raw.get_repeating_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_field(49),
raw.get_field(50),
raw.get_repeating_field(51),
raw.get_field(52),
raw.get_field(53),
raw.get_field(54),
raw.get_repeating_field(55),
raw.get_field(56),
raw.get_field(57),
        ],
    }
}
pub fn parse_hxx(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "Hxx".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_iam(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IAM".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
        ],
    }
}
pub fn parse_iar(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IAR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_iim(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IIM".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
        ],
    }
}
pub fn parse_ilt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ILT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
        ],
    }
}
pub fn parse_in1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IN1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_repeating_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_repeating_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(39),
raw.get_field(42),
raw.get_field(43),
raw.get_repeating_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_repeating_field(49),
raw.get_field(50),
raw.get_field(51),
raw.get_field(52),
raw.get_field(53),
raw.get_repeating_field(54),
raw.get_field(55),
        ],
    }
}
pub fn parse_in2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IN2".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_repeating_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_repeating_field(25),
raw.get_repeating_field(26),
raw.get_field(27),
raw.get_repeating_field(28),
raw.get_repeating_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_repeating_field(32),
raw.get_repeating_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_repeating_field(40),
raw.get_field(41),
raw.get_repeating_field(42),
raw.get_repeating_field(43),
raw.get_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_repeating_field(49),
raw.get_repeating_field(50),
raw.get_field(51),
raw.get_repeating_field(52),
raw.get_repeating_field(53),
raw.get_repeating_field(54),
raw.get_field(55),
raw.get_repeating_field(56),
raw.get_field(57),
raw.get_repeating_field(58),
raw.get_field(59),
raw.get_field(60),
raw.get_field(61),
raw.get_field(62),
raw.get_repeating_field(63),
raw.get_repeating_field(64),
raw.get_field(65),
raw.get_field(66),
raw.get_field(67),
raw.get_field(68),
raw.get_repeating_field(69),
raw.get_repeating_field(70),
raw.get_repeating_field(71),
raw.get_field(72),
raw.get_field(73),
        ],
    }
}
pub fn parse_in3(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IN3".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_repeating_field(19),
raw.get_repeating_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_repeating_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
        ],
    }
}
pub fn parse_inv(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "INV".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
        ],
    }
}
pub fn parse_ipc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IPC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
        ],
    }
}
pub fn parse_ipr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IPR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
        ],
    }
}
pub fn parse_isd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ISD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_itm(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ITM".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_repeating_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
        ],
    }
}
pub fn parse_ivc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IVC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
        ],
    }
}
pub fn parse_ivt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "IVT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_repeating_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
        ],
    }
}
pub fn parse_lan(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "LAN".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_lcc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "LCC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
        ],
    }
}
pub fn parse_lch(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "LCH".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_ldp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "LDP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_loc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "LOC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
        ],
    }
}
pub fn parse_lrl(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "LRL".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_mcp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MCP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_mfa(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MFA".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
        ],
    }
}
pub fn parse_mfe(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MFE".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_mfi(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MFI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_mrg(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MRG".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_field(3),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
        ],
    }
}
pub fn parse_msa(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MSA".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(4),
raw.get_field(7),
raw.get_field(8),
        ],
    }
}
pub fn parse_msh(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "MSH".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_repeating_field(27),
raw.get_repeating_field(28),
        ],
    }
}
pub fn parse_nck(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NCK".to_string(),
        fields: vec![
raw.get_field(1),
        ],
    }
}
pub fn parse_nds(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NDS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_nk1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NK1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_repeating_field(17),
raw.get_repeating_field(18),
raw.get_repeating_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_repeating_field(26),
raw.get_field(27),
raw.get_repeating_field(28),
raw.get_repeating_field(29),
raw.get_repeating_field(30),
raw.get_repeating_field(32),
raw.get_repeating_field(33),
raw.get_field(34),
raw.get_repeating_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_field(40),
raw.get_field(41),
        ],
    }
}
pub fn parse_npu(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NPU".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_nsc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NSC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
        ],
    }
}
pub fn parse_nst(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NST".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
        ],
    }
}
pub fn parse_nte(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "NTE".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
        ],
    }
}
pub fn parse_obr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OBR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(29),
raw.get_field(30),
raw.get_repeating_field(31),
raw.get_field(36),
raw.get_field(37),
raw.get_repeating_field(38),
raw.get_repeating_field(39),
raw.get_field(40),
raw.get_field(41),
raw.get_field(42),
raw.get_repeating_field(43),
raw.get_field(44),
raw.get_repeating_field(45),
raw.get_repeating_field(46),
raw.get_repeating_field(47),
raw.get_field(48),
raw.get_field(49),
raw.get_field(51),
raw.get_field(52),
raw.get_repeating_field(53),
raw.get_repeating_field(54),
raw.get_field(55),
        ],
    }
}
pub fn parse_obx(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OBX".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_repeating_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_repeating_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_repeating_field(32),
raw.get_repeating_field(33),
        ],
    }
}
pub fn parse_ods(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ODS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_odt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ODT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_oh1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OH1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_oh2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OH2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
        ],
    }
}
pub fn parse_oh3(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OH3".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
        ],
    }
}
pub fn parse_oh4(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OH4".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_om1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_repeating_field(25),
raw.get_field(26),
raw.get_repeating_field(27),
raw.get_repeating_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_repeating_field(31),
raw.get_field(32),
raw.get_repeating_field(33),
raw.get_repeating_field(34),
raw.get_repeating_field(35),
raw.get_repeating_field(36),
raw.get_repeating_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_repeating_field(40),
raw.get_field(41),
raw.get_field(42),
raw.get_field(43),
raw.get_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_field(49),
raw.get_field(50),
raw.get_repeating_field(51),
raw.get_repeating_field(52),
raw.get_repeating_field(53),
raw.get_field(54),
raw.get_repeating_field(55),
raw.get_field(56),
raw.get_field(57),
raw.get_repeating_field(58),
raw.get_repeating_field(59),
        ],
    }
}
pub fn parse_om2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
        ],
    }
}
pub fn parse_om3(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM3".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_om4(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM4".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
        ],
    }
}
pub fn parse_om5(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM5".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_om6(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM6".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_om7(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OM7".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
        ],
    }
}
pub fn parse_omc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OMC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
        ],
    }
}
pub fn parse_orc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ORC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(20),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(32),
raw.get_repeating_field(33),
raw.get_repeating_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
        ],
    }
}
pub fn parse_org(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ORG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
        ],
    }
}
pub fn parse_ovr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "OVR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_pac(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PAC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
        ],
    }
}
pub fn parse_pce(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PCE".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_pcr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PCR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
        ],
    }
}
pub fn parse_pd1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PD1".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
        ],
    }
}
pub fn parse_pda(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PDA".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
        ],
    }
}
pub fn parse_pdc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PDC".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
        ],
    }
}
pub fn parse_peo(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PEO".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_repeating_field(14),
raw.get_repeating_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
raw.get_repeating_field(18),
raw.get_repeating_field(19),
raw.get_repeating_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
        ],
    }
}
pub fn parse_pes(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PES".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
        ],
    }
}
pub fn parse_pid(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PID".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(3),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(10),
raw.get_repeating_field(11),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_repeating_field(21),
raw.get_repeating_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_repeating_field(26),
raw.get_field(27),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_repeating_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_repeating_field(39),
raw.get_repeating_field(40),
        ],
    }
}
pub fn parse_pkg(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PKG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
        ],
    }
}
pub fn parse_pm1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PM1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
        ],
    }
}
pub fn parse_pmt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PMT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_pr1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PR1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(3),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(9),
raw.get_field(10),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_repeating_field(23),
raw.get_field(24),
raw.get_field(25),
        ],
    }
}
pub fn parse_pra(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PRA".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_prb(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PRB".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
        ],
    }
}
pub fn parse_prc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PRC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
        ],
    }
}
pub fn parse_prd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PRD".to_string(),
        fields: vec![
raw.get_repeating_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_repeating_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_prt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PRT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
        ],
    }
}
pub fn parse_psg(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PSG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_psh(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PSH".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_psl(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PSL".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_field(40),
raw.get_field(41),
raw.get_field(42),
raw.get_field(43),
raw.get_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
        ],
    }
}
pub fn parse_pss(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PSS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_pth(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PTH".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_pv1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PV1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_repeating_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_repeating_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_repeating_field(25),
raw.get_repeating_field(26),
raw.get_repeating_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_field(41),
raw.get_field(42),
raw.get_field(43),
raw.get_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_field(49),
raw.get_repeating_field(50),
raw.get_field(51),
raw.get_field(53),
raw.get_field(54),
        ],
    }
}
pub fn parse_pv2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PV2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_repeating_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_repeating_field(39),
raw.get_field(40),
raw.get_repeating_field(41),
raw.get_field(42),
raw.get_field(43),
raw.get_field(44),
raw.get_repeating_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_repeating_field(49),
raw.get_field(50),
        ],
    }
}
pub fn parse_pye(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "PYE".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_qak(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "QAK".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_qid(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "QID".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_qpd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "QPD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_qrd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "QRD".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_qrf(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "QRF".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_qri(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "QRI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_rcp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RCP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
        ],
    }
}
pub fn parse_rdf(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RDF".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
        ],
    }
}
pub fn parse_rdt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RDT".to_string(),
        fields: vec![
raw.get_field(1),
        ],
    }
}
pub fn parse_rel(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "REL".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
        ],
    }
}
pub fn parse_rf1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RF1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_repeating_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
        ],
    }
}
pub fn parse_rfi(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RFI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_rgs(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RGS".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_rmi(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RMI".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
        ],
    }
}
pub fn parse_rol(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ROL".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_rq1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RQ1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_rqd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RQD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
        ],
    }
}
pub fn parse_rxa(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXA".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_repeating_field(16),
raw.get_repeating_field(17),
raw.get_repeating_field(18),
raw.get_repeating_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_repeating_field(29),
        ],
    }
}
pub fn parse_rxc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
        ],
    }
}
pub fn parse_rxd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_repeating_field(19),
raw.get_repeating_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_repeating_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_repeating_field(34),
raw.get_repeating_field(35),
        ],
    }
}
pub fn parse_rxe(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXE".to_string(),
        fields: vec![
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_repeating_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_repeating_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_repeating_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_field(40),
raw.get_field(41),
raw.get_field(42),
raw.get_field(43),
raw.get_field(44),
raw.get_repeating_field(45),
        ],
    }
}
pub fn parse_rxg(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXG".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_field(12),
raw.get_repeating_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_repeating_field(19),
raw.get_repeating_field(20),
raw.get_repeating_field(21),
raw.get_repeating_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(29),
raw.get_field(30),
raw.get_repeating_field(31),
raw.get_field(32),
raw.get_field(33),
        ],
    }
}
pub fn parse_rxo(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXO".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_repeating_field(7),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_repeating_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_repeating_field(36),
        ],
    }
}
pub fn parse_rxr(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_rxv(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "RXV".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
        ],
    }
}
pub fn parse_sac(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SAC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_repeating_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_field(39),
raw.get_repeating_field(40),
raw.get_repeating_field(41),
raw.get_field(42),
raw.get_repeating_field(43),
raw.get_repeating_field(44),
raw.get_field(45),
raw.get_field(46),
raw.get_field(47),
raw.get_field(48),
raw.get_field(49),
        ],
    }
}
pub fn parse_scd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SCD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_repeating_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_field(36),
raw.get_field(37),
        ],
    }
}
pub fn parse_sch(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SCH".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(10),
raw.get_repeating_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_repeating_field(18),
raw.get_field(19),
raw.get_repeating_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_repeating_field(26),
raw.get_repeating_field(27),
raw.get_field(28),
        ],
    }
}
pub fn parse_scp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SCP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
        ],
    }
}
pub fn parse_sdd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SDD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
        ],
    }
}
pub fn parse_sft(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SFT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
        ],
    }
}
pub fn parse_sgh(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SGH".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_sgt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SGT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_shp(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SHP".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_repeating_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
        ],
    }
}
pub fn parse_sid(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SID".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_slt(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SLT".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
        ],
    }
}
pub fn parse_spm(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "SPM".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_repeating_field(15),
raw.get_repeating_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_repeating_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_repeating_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_repeating_field(30),
raw.get_repeating_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
        ],
    }
}
pub fn parse_stf(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "STF".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_repeating_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_repeating_field(11),
raw.get_repeating_field(12),
raw.get_repeating_field(13),
raw.get_repeating_field(14),
raw.get_repeating_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_field(22),
raw.get_field(23),
raw.get_field(24),
raw.get_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
raw.get_field(29),
raw.get_repeating_field(30),
raw.get_field(31),
raw.get_field(32),
raw.get_field(33),
raw.get_field(34),
raw.get_field(35),
raw.get_repeating_field(36),
raw.get_field(37),
raw.get_field(38),
raw.get_repeating_field(39),
raw.get_field(40),
raw.get_field(41),
        ],
    }
}
pub fn parse_stz(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "STZ".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
        ],
    }
}
pub fn parse_tcc(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "TCC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
        ],
    }
}
pub fn parse_tcd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "TCD".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
        ],
    }
}
pub fn parse_tq1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "TQ1".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
        ],
    }
}
pub fn parse_tq2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "TQ2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_repeating_field(3),
raw.get_repeating_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
        ],
    }
}
pub fn parse_txa(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "TXA".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_repeating_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_repeating_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_repeating_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_repeating_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
raw.get_field(18),
raw.get_field(19),
raw.get_field(20),
raw.get_field(21),
raw.get_repeating_field(22),
raw.get_repeating_field(23),
raw.get_repeating_field(24),
raw.get_repeating_field(25),
raw.get_field(26),
raw.get_field(27),
raw.get_field(28),
        ],
    }
}
pub fn parse_uac(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "UAC".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_ub1(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "UB1".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_ub2(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "UB2".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_field(9),
raw.get_field(10),
raw.get_field(11),
raw.get_field(12),
raw.get_field(13),
raw.get_field(14),
raw.get_field(15),
raw.get_field(16),
raw.get_field(17),
        ],
    }
}
pub fn parse_urd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "URD".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_urs(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "URS".to_string(),
        fields: vec![
        ],
    }
}
pub fn parse_var(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "VAR".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_repeating_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
        ],
    }
}
pub fn parse_vnd(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "VND".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
raw.get_field(3),
raw.get_field(4),
raw.get_field(5),
raw.get_repeating_field(6),
raw.get_field(7),
raw.get_field(8),
raw.get_repeating_field(9),
raw.get_repeating_field(10),
raw.get_field(11),
        ],
    }
}
pub fn parse_zl7(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "ZL7".to_string(),
        fields: vec![
raw.get_field(1),
raw.get_field(2),
        ],
    }
}
pub fn parse_zxx(raw: &RawFields) -> RawSegment {
    RawSegment {
        segment_id: "Zxx".to_string(),
        fields: vec![
        ],
    }
}

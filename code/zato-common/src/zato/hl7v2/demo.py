from __future__ import annotations

from zato.hl7v2.parser import parse_message

def main() -> None:
    raw_message = (
        "MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|"
        "20240315120000||ADT^A01^ADT_A01|MSG00001|P|2.9\r"
        "EVN|A01|20240315120000\r"
        "PID|1||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r"
        "PV1|1|I|ICU^101^A\r"
    )

    msg = parse_message(raw_message)

    print("Structure ID:", msg._structure_id)

if __name__ == "__main__":
    main()

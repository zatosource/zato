#!/usr/bin/env bash

#
# Downloads the fixtures the HL7-to-FHIR conversion tests are proven against.
#
# The fixtures are committed to the repository, this script only documents where they come from
# and lets them be refreshed when upstream publishes new versions.
#
# * fixtures/v2mappings       - ConceptMaps from the HL7 v2-to-FHIR Implementation Guide (STU 1)
# * fixtures/test_conversions - the IG's agreed message-to-Bundle test conversion pairs
# * fixtures/messages/samples - sample HL7 v2 messages from the Microsoft FHIR-Converter project (MIT)
#

set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

#
# The v2-to-FHIR IG package with all the ConceptMaps
#

echo "Downloading the v2-to-FHIR IG package"
curl -sL -o "$work_dir/package.tgz" http://hl7.org/fhir/uv/v2mappings/STU1/package.tgz
tar xzf "$work_dir/package.tgz" -C "$work_dir"

mkdir -p "$here/fixtures/v2mappings"
cp "$work_dir"/package/ConceptMap-*.json "$here/fixtures/v2mappings/"
cp "$work_dir"/package/CodeSystem-*.json "$here/fixtures/v2mappings/"

#
# The IG repository with the test conversion pairs
#

echo "Cloning the v2-to-fhir repository"
git clone --quiet --depth 1 https://github.com/HL7/v2-to-fhir.git "$work_dir/v2-to-fhir"

mkdir -p "$here/fixtures/test_conversions"
cp "$work_dir"/v2-to-fhir/samples/fhir-bundles/FHIR_bundle.hl7_ADT_A01.json "$here/fixtures/test_conversions/"
cp "$work_dir"/v2-to-fhir/samples/fhir-bundles/FHIR_bundle.hl7_MDM_T02.json "$here/fixtures/test_conversions/"
cp "$work_dir"/v2-to-fhir/samples/messages/Message.hl7_MDM_T02.txt "$here/fixtures/test_conversions/"

echo "Extracting test conversion messages"
python3 - "$work_dir/v2-to-fhir/input/pagecontent/test_conversions.md" "$here/fixtures/test_conversions" <<'EOF'
import re
import sys

source_path = sys.argv[1]
out_dir = sys.argv[2]

text = open(source_path).read()

# Each '#### NAME' heading is followed by one <table><tr> ... </tr></table> block with the message
pattern = re.compile(r'#### (\w+).*?<tr>\n(.*?)\n</tr>', re.S)

for name, body in pattern.findall(text):
    segments = []
    for line in body.split('\n'):
        line = line.strip()
        if line.startswith('<br>'):
            line = line[4:]
        if line:
            segments.append(line.strip())
    message = '\r'.join(segments) + '\r'
    with open(f'{out_dir}/{name}.hl7', 'w') as f:
        f.write(message)
EOF

#
# The Microsoft FHIR-Converter sample messages
#

echo "Cloning the Microsoft FHIR-Converter sample data"
git clone --quiet --depth 1 --filter=blob:none --sparse https://github.com/microsoft/FHIR-Converter.git "$work_dir/fhir-converter"
git -C "$work_dir/fhir-converter" sparse-checkout set data/SampleData/Hl7v2

mkdir -p "$here/fixtures/messages/samples"
cp "$work_dir"/fhir-converter/data/SampleData/Hl7v2/*.hl7 "$here/fixtures/messages/samples/"

echo "Done"

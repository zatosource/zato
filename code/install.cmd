
virtualenv --always-copy .
call .\Scripts\activate.bat
.\Scripts\pip install -r .\requirements.txt
.\Scripts\pip install -e .\zato-common
.\Scripts\pip install -e .\zato-agent
.\Scripts\pip install -e .\zato-broker
.\Scripts\pip install -e .\zato-cli
.\Scripts\pip install -e .\zato-client
.\Scripts\pip install -e .\zato-cy
.\Scripts\pip install -e .\zato-distlock
.\Scripts\pip install -e .\zato-hl7
.\Scripts\pip install -e .\zato-lib
.\Scripts\pip install -e .\zato-scheduler
.\Scripts\pip install -e .\zato-server
.\Scripts\pip install -e .\zato-web-admin
.\Scripts\pip install -e .\zato-zmq
.\Scripts\pip install -e .\zato-sso
.\Scripts\pip install -e .\zato-testing
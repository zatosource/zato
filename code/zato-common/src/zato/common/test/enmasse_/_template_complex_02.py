# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_02 = """

security:

  - name: enmasse.basic_auth.1
    type: basic_auth
    username: enmasse.1
    password: Zato_Enmasse_Env.BasicAuth1

  - name: enmasse.basic_auth.2
    type: basic_auth
    username: enmasse.2
    password: Zato_Enmasse_Env.BasicAuth2

  - name: enmasse.basic_auth.3
    type: basic_auth
    username: enmasse.3
    password: Zato_Enmasse_Env.BasicAuth3

  - name: enmasse.basic_auth.4
    type: basic_auth
    username: enmasse.4
    password: Zato_Enmasse_Env.BasicAuth4

  - name: enmasse.basic_auth.5
    type: basic_auth
    username: enmasse.5
    password: Zato_Enmasse_Env.BasicAuth5

  - name: enmasse.basic_auth.6
    type: basic_auth
    username: enmasse.6
    password: Zato_Enmasse_Env.BasicAuth6

  - name: enmasse.basic_auth.7
    type: basic_auth
    username: enmasse.7
    password: Zato_Enmasse_Env.BasicAuth7

  - name: enmasse.basic_auth.8
    type: basic_auth
    username: enmasse.8
    password: Zato_Enmasse_Env.BasicAuth8

  - name: enmasse.basic_auth.9
    type: basic_auth
    username: enmasse.9
    password: Zato_Enmasse_Env.BasicAuth9

  - name: enmasse.basic_auth.10
    type: basic_auth
    username: enmasse.10
    password: Zato_Enmasse_Env.BasicAuth10

  - name: enmasse.basic_auth.11
    type: basic_auth
    username: enmasse.11
    password: Zato_Enmasse_Env.BasicAuth11

  - name: enmasse.basic_auth.12
    type: basic_auth
    username: enmasse.12
    password: Zato_Enmasse_Env.BasicAuth12

  - name: enmasse.basic_auth.13
    type: basic_auth
    username: enmasse.13
    password: Zato_Enmasse_Env.BasicAuth13

  - name: enmasse.basic_auth.14
    type: basic_auth
    username: enmasse.14
    password: Zato_Enmasse_Env.BasicAuth14

  - name: enmasse.basic_auth.15
    type: basic_auth
    username: enmasse.15
    password: Zato_Enmasse_Env.BasicAuth15

  - name: enmasse.basic_auth.16
    type: basic_auth
    username: enmasse.16
    password: Zato_Enmasse_Env.BasicAuth16

  - name: enmasse.basic_auth.17
    type: basic_auth
    username: enmasse.17
    password: Zato_Enmasse_Env.BasicAuth17

  - name: enmasse.basic_auth.18
    type: basic_auth
    username: enmasse.18
    password: Zato_Enmasse_Env.BasicAuth18

  - name: enmasse.basic_auth.19
    type: basic_auth
    username: enmasse.19
    password: Zato_Enmasse_Env.BasicAuth19

  - name: enmasse.basic_auth.20
    type: basic_auth
    username: enmasse.20
    password: Zato_Enmasse_Env.BasicAuth20

  - name: enmasse.basic_auth.21
    type: basic_auth
    username: enmasse.21
    password: Zato_Enmasse_Env.BasicAuth21

  - name: enmasse.basic_auth.22
    type: basic_auth
    username: enmasse.22
    password: Zato_Enmasse_Env.BasicAuth22

  - name: enmasse.basic_auth.23
    type: basic_auth
    username: enmasse.23
    password: Zato_Enmasse_Env.BasicAuth23

  - name: enmasse.basic_auth.24
    type: basic_auth
    username: enmasse.24
    password: Zato_Enmasse_Env.BasicAuth24

  - name: enmasse.basic_auth.25
    type: basic_auth
    username: enmasse.25
    password: Zato_Enmasse_Env.BasicAuth25

  - name: enmasse.basic_auth.26
    type: basic_auth
    username: enmasse.26
    password: Zato_Enmasse_Env.BasicAuth26

  - name: enmasse.basic_auth.27
    type: basic_auth
    username: enmasse.27
    password: Zato_Enmasse_Env.BasicAuth27

  - name: enmasse.basic_auth.28
    type: basic_auth
    username: enmasse.28
    password: Zato_Enmasse_Env.BasicAuth28

  - name: enmasse.basic_auth.29
    type: basic_auth
    username: enmasse.29
    password: Zato_Enmasse_Env.BasicAuth29

  - name: enmasse.basic_auth.30
    type: basic_auth
    username: enmasse.30
    password: Zato_Enmasse_Env.BasicAuth30

  - name: enmasse.basic_auth.31
    type: basic_auth
    username: enmasse.31
    password: Zato_Enmasse_Env.BasicAuth31

  - name: enmasse.basic_auth.32
    type: basic_auth
    username: enmasse.32
    password: Zato_Enmasse_Env.BasicAuth32

  - name: enmasse.basic_auth.33
    type: basic_auth
    username: enmasse.33
    password: Zato_Enmasse_Env.BasicAuth33

  - name: enmasse.basic_auth.34
    type: basic_auth
    username: enmasse.34
    password: Zato_Enmasse_Env.BasicAuth34

  - name: enmasse.basic_auth.35
    type: basic_auth
    username: enmasse.35
    password: Zato_Enmasse_Env.BasicAuth35

  - name: enmasse.basic_auth.36
    type: basic_auth
    username: enmasse.36
    password: Zato_Enmasse_Env.BasicAuth36

  - name: enmasse.basic_auth.37
    type: basic_auth
    username: enmasse.37
    password: Zato_Enmasse_Env.BasicAuth37

  - name: enmasse.basic_auth.38
    type: basic_auth
    username: enmasse.38
    password: Zato_Enmasse_Env.BasicAuth38

  - name: enmasse.basic_auth.39
    type: basic_auth
    username: enmasse.39
    password: Zato_Enmasse_Env.BasicAuth39

  - name: enmasse.basic_auth.40
    type: basic_auth
    username: enmasse.40
    password: Zato_Enmasse_Env.BasicAuth40


  - name: enmasse.bearer_token.1
    username: enmasse.1
    password: Zato_Enmasse_Env.EnmasseBearerToken1
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.2
    username: enmasse.2
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.3
    username: enmasse.3
    password: Zato_Enmasse_Env.EnmasseBearerToken3
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.4
    username: enmasse.4
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.5
    username: enmasse.5
    password: Zato_Enmasse_Env.EnmasseBearerToken5
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.6
    username: enmasse.6
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.7
    username: enmasse.7
    password: Zato_Enmasse_Env.EnmasseBearerToken7
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.8
    username: enmasse.8
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.9
    username: enmasse.9
    password: Zato_Enmasse_Env.EnmasseBearerToken9
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.10
    username: enmasse.10
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.11
    username: enmasse.11
    password: Zato_Enmasse_Env.EnmasseBearerToken11
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.12
    username: enmasse.12
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.13
    username: enmasse.13
    password: Zato_Enmasse_Env.EnmasseBearerToken13
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.14
    username: enmasse.14
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.15
    username: enmasse.15
    password: Zato_Enmasse_Env.EnmasseBearerToken15
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.16
    username: enmasse.16
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.17
    username: enmasse.17
    password: Zato_Enmasse_Env.EnmasseBearerToken17
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.18
    username: enmasse.18
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.19
    username: enmasse.19
    password: Zato_Enmasse_Env.EnmasseBearerToken19
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.20
    username: enmasse.20
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.21
    username: enmasse.21
    password: Zato_Enmasse_Env.EnmasseBearerToken21
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.22
    username: enmasse.22
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.23
    username: enmasse.23
    password: Zato_Enmasse_Env.EnmasseBearerToken23
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.24
    username: enmasse.24
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.25
    username: enmasse.25
    password: Zato_Enmasse_Env.EnmasseBearerToken25
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.26
    username: enmasse.26
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.27
    username: enmasse.27
    password: Zato_Enmasse_Env.EnmasseBearerToken27
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.28
    username: enmasse.28
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.29
    username: enmasse.29
    password: Zato_Enmasse_Env.EnmasseBearerToken29
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.30
    username: enmasse.30
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.31
    username: enmasse.31
    password: Zato_Enmasse_Env.EnmasseBearerToken31
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.32
    username: enmasse.32
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.33
    username: enmasse.33
    password: Zato_Enmasse_Env.EnmasseBearerToken33
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.34
    username: enmasse.34
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.35
    username: enmasse.35
    password: Zato_Enmasse_Env.EnmasseBearerToken35
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.36
    username: enmasse.36
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.37
    username: enmasse.37
    password: Zato_Enmasse_Env.EnmasseBearerToken37
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.38
    username: enmasse.38
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.bearer_token.39
    username: enmasse.39
    password: Zato_Enmasse_Env.EnmasseBearerToken39
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.40
    username: enmasse.40
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com


  - name: enmasse.ntlm.1
    username: enmasse\\user1
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.2
    username: enmasse\\user2
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.3
    username: enmasse\\user3
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.4
    username: enmasse\\user4
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.5
    username: enmasse\\user5
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.6
    username: enmasse\\user6
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.7
    username: enmasse\\user7
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.8
    username: enmasse\\user8
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.9
    username: enmasse\\user9
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.10
    username: enmasse\\user10
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.11
    username: enmasse\\user11
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.12
    username: enmasse\\user12
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.13
    username: enmasse\\user13
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.14
    username: enmasse\\user14
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.15
    username: enmasse\\user15
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.16
    username: enmasse\\user16
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.17
    username: enmasse\\user17
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.18
    username: enmasse\\user18
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.19
    username: enmasse\\user19
    password: abcdef123456
    type: ntlm

  - name: enmasse.ntlm.20
    username: enmasse\\user20
    password: abcdef123456
    type: ntlm


  - name: enmasse.apikey.1
    type: apikey
    username: enmasse.1
    password: Zato_Enmasse_Env.EnmasseApiKey1

  - name: enmasse.apikey.2
    type: apikey
    username: enmasse.2
    password: Zato_Enmasse_Env.EnmasseApiKey2

  - name: enmasse.apikey.3
    type: apikey
    username: enmasse.3
    password: Zato_Enmasse_Env.EnmasseApiKey3

  - name: enmasse.apikey.4
    type: apikey
    username: enmasse.4
    password: Zato_Enmasse_Env.EnmasseApiKey4

  - name: enmasse.apikey.5
    type: apikey
    username: enmasse.5
    password: Zato_Enmasse_Env.EnmasseApiKey5

  - name: enmasse.apikey.6
    type: apikey
    username: enmasse.6
    password: Zato_Enmasse_Env.EnmasseApiKey6

  - name: enmasse.apikey.7
    type: apikey
    username: enmasse.7
    password: Zato_Enmasse_Env.EnmasseApiKey7

  - name: enmasse.apikey.8
    type: apikey
    username: enmasse.8
    password: Zato_Enmasse_Env.EnmasseApiKey8

  - name: enmasse.apikey.9
    type: apikey
    username: enmasse.9
    password: Zato_Enmasse_Env.EnmasseApiKey9

  - name: enmasse.apikey.10
    type: apikey
    username: enmasse.10
    password: Zato_Enmasse_Env.EnmasseApiKey10

  - name: enmasse.apikey.11
    type: apikey
    username: enmasse.11
    password: Zato_Enmasse_Env.EnmasseApiKey11

  - name: enmasse.apikey.12
    type: apikey
    username: enmasse.12
    password: Zato_Enmasse_Env.EnmasseApiKey12

  - name: enmasse.apikey.13
    type: apikey
    username: enmasse.13
    password: Zato_Enmasse_Env.EnmasseApiKey13

  - name: enmasse.apikey.14
    type: apikey
    username: enmasse.14
    password: Zato_Enmasse_Env.EnmasseApiKey14

  - name: enmasse.apikey.15
    type: apikey
    username: enmasse.15
    password: Zato_Enmasse_Env.EnmasseApiKey15

  - name: enmasse.apikey.16
    type: apikey
    username: enmasse.16
    password: Zato_Enmasse_Env.EnmasseApiKey16

  - name: enmasse.apikey.17
    type: apikey
    username: enmasse.17
    password: Zato_Enmasse_Env.EnmasseApiKey17

  - name: enmasse.apikey.18
    type: apikey
    username: enmasse.18
    password: Zato_Enmasse_Env.EnmasseApiKey18

  - name: enmasse.apikey.19
    type: apikey
    username: enmasse.19
    password: Zato_Enmasse_Env.EnmasseApiKey19

  - name: enmasse.apikey.20
    type: apikey
    username: enmasse.20
    password: Zato_Enmasse_Env.EnmasseApiKey20

  - name: enmasse.apikey.21
    type: apikey
    username: enmasse.21
    password: Zato_Enmasse_Env.EnmasseApiKey21

  - name: enmasse.apikey.22
    type: apikey
    username: enmasse.22
    password: Zato_Enmasse_Env.EnmasseApiKey22

  - name: enmasse.apikey.23
    type: apikey
    username: enmasse.23
    password: Zato_Enmasse_Env.EnmasseApiKey23

  - name: enmasse.apikey.24
    type: apikey
    username: enmasse.24
    password: Zato_Enmasse_Env.EnmasseApiKey24

  - name: enmasse.apikey.25
    type: apikey
    username: enmasse.25
    password: Zato_Enmasse_Env.EnmasseApiKey25

  - name: enmasse.apikey.26
    type: apikey
    username: enmasse.26
    password: Zato_Enmasse_Env.EnmasseApiKey26

  - name: enmasse.apikey.27
    type: apikey
    username: enmasse.27
    password: Zato_Enmasse_Env.EnmasseApiKey27

  - name: enmasse.apikey.28
    type: apikey
    username: enmasse.28
    password: Zato_Enmasse_Env.EnmasseApiKey28

  - name: enmasse.apikey.29
    type: apikey
    username: enmasse.29
    password: Zato_Enmasse_Env.EnmasseApiKey29

  - name: enmasse.apikey.30
    type: apikey
    username: enmasse.30
    password: Zato_Enmasse_Env.EnmasseApiKey30

  - name: enmasse.apikey.31
    type: apikey
    username: enmasse.31
    password: Zato_Enmasse_Env.EnmasseApiKey31

  - name: enmasse.apikey.32
    type: apikey
    username: enmasse.32
    password: Zato_Enmasse_Env.EnmasseApiKey32

  - name: enmasse.apikey.33
    type: apikey
    username: enmasse.33
    password: Zato_Enmasse_Env.EnmasseApiKey33

  - name: enmasse.apikey.34
    type: apikey
    username: enmasse.34
    password: Zato_Enmasse_Env.EnmasseApiKey34

  - name: enmasse.apikey.35
    type: apikey
    username: enmasse.35
    password: Zato_Enmasse_Env.EnmasseApiKey35

  - name: enmasse.apikey.36
    type: apikey
    username: enmasse.36
    password: Zato_Enmasse_Env.EnmasseApiKey36

  - name: enmasse.apikey.37
    type: apikey
    username: enmasse.37
    password: Zato_Enmasse_Env.EnmasseApiKey37

  - name: enmasse.apikey.38
    type: apikey
    username: enmasse.38
    password: Zato_Enmasse_Env.EnmasseApiKey38

  - name: enmasse.apikey.39
    type: apikey
    username: enmasse.39
    password: Zato_Enmasse_Env.EnmasseApiKey39

  - name: enmasse.apikey.40
    type: apikey
    username: enmasse.40
    password: Zato_Enmasse_Env.EnmasseApiKey40


groups:
  - name: enmasse.group.1
    members:
      - enmasse.basic_auth.1
      - enmasse.basic_auth.2
      - enmasse.apikey.1

  - name: enmasse.group.2
    members:
      - enmasse.apikey.1
      - enmasse.apikey.2
      - enmasse.basic_auth.1

  - name: enmasse.group.3
    members:
      - enmasse.basic_auth.3
      - enmasse.basic_auth.4
      - enmasse.apikey.3

  - name: enmasse.group.4
    members:
      - enmasse.apikey.3
      - enmasse.apikey.4
      - enmasse.basic_auth.3

  - name: enmasse.group.5
    members:
      - enmasse.basic_auth.5
      - enmasse.basic_auth.6
      - enmasse.apikey.5

  - name: enmasse.group.6
    members:
      - enmasse.apikey.5
      - enmasse.apikey.6
      - enmasse.basic_auth.5

  - name: enmasse.group.7
    members:
      - enmasse.basic_auth.7
      - enmasse.basic_auth.8
      - enmasse.apikey.7

  - name: enmasse.group.8
    members:
      - enmasse.apikey.7
      - enmasse.apikey.8
      - enmasse.basic_auth.7

  - name: enmasse.group.9
    members:
      - enmasse.basic_auth.9
      - enmasse.basic_auth.10
      - enmasse.apikey.9

  - name: enmasse.group.10
    members:
      - enmasse.apikey.9
      - enmasse.apikey.10
      - enmasse.basic_auth.9

  - name: enmasse.group.11
    members:
      - enmasse.basic_auth.11
      - enmasse.basic_auth.12
      - enmasse.apikey.11

  - name: enmasse.group.12
    members:
      - enmasse.apikey.11
      - enmasse.apikey.12
      - enmasse.basic_auth.11

  - name: enmasse.group.13
    members:
      - enmasse.basic_auth.13
      - enmasse.basic_auth.14
      - enmasse.apikey.13

  - name: enmasse.group.14
    members:
      - enmasse.apikey.13
      - enmasse.apikey.14
      - enmasse.basic_auth.13

  - name: enmasse.group.15
    members:
      - enmasse.basic_auth.15
      - enmasse.basic_auth.16
      - enmasse.apikey.15

  - name: enmasse.group.16
    members:
      - enmasse.apikey.15
      - enmasse.apikey.16
      - enmasse.basic_auth.15

  - name: enmasse.group.17
    members:
      - enmasse.basic_auth.17
      - enmasse.basic_auth.18
      - enmasse.apikey.17

  - name: enmasse.group.18
    members:
      - enmasse.apikey.17
      - enmasse.apikey.18
      - enmasse.basic_auth.17

  - name: enmasse.group.19
    members:
      - enmasse.basic_auth.19
      - enmasse.basic_auth.20
      - enmasse.apikey.19

  - name: enmasse.group.20
    members:
      - enmasse.apikey.19
      - enmasse.apikey.20
      - enmasse.basic_auth.19

  - name: enmasse.group.21
    members:
      - enmasse.basic_auth.21
      - enmasse.basic_auth.22
      - enmasse.apikey.21

  - name: enmasse.group.22
    members:
      - enmasse.apikey.21
      - enmasse.apikey.22
      - enmasse.basic_auth.21

  - name: enmasse.group.23
    members:
      - enmasse.basic_auth.23
      - enmasse.basic_auth.24
      - enmasse.apikey.23

  - name: enmasse.group.24
    members:
      - enmasse.apikey.23
      - enmasse.apikey.24
      - enmasse.basic_auth.23

  - name: enmasse.group.25
    members:
      - enmasse.basic_auth.25
      - enmasse.basic_auth.26
      - enmasse.apikey.25

  - name: enmasse.group.26
    members:
      - enmasse.apikey.25
      - enmasse.apikey.26
      - enmasse.basic_auth.25

  - name: enmasse.group.27
    members:
      - enmasse.basic_auth.27
      - enmasse.basic_auth.28
      - enmasse.apikey.27

  - name: enmasse.group.28
    members:
      - enmasse.apikey.27
      - enmasse.apikey.28
      - enmasse.basic_auth.27

  - name: enmasse.group.29
    members:
      - enmasse.basic_auth.29
      - enmasse.basic_auth.30
      - enmasse.apikey.29

  - name: enmasse.group.30
    members:
      - enmasse.apikey.29
      - enmasse.apikey.30
      - enmasse.basic_auth.29

  - name: enmasse.group.31
    members:
      - enmasse.basic_auth.31
      - enmasse.basic_auth.32
      - enmasse.apikey.31

  - name: enmasse.group.32
    members:
      - enmasse.apikey.31
      - enmasse.apikey.32
      - enmasse.basic_auth.31

  - name: enmasse.group.33
    members:
      - enmasse.basic_auth.33
      - enmasse.basic_auth.34
      - enmasse.apikey.33

  - name: enmasse.group.34
    members:
      - enmasse.apikey.33
      - enmasse.apikey.34
      - enmasse.basic_auth.33

  - name: enmasse.group.35
    members:
      - enmasse.basic_auth.35
      - enmasse.basic_auth.36
      - enmasse.apikey.35

  - name: enmasse.group.36
    members:
      - enmasse.apikey.35
      - enmasse.apikey.36
      - enmasse.basic_auth.35

  - name: enmasse.group.37
    members:
      - enmasse.basic_auth.37
      - enmasse.basic_auth.38
      - enmasse.apikey.37

  - name: enmasse.group.38
    members:
      - enmasse.apikey.37
      - enmasse.apikey.38
      - enmasse.basic_auth.37

  - name: enmasse.group.39
    members:
      - enmasse.basic_auth.39
      - enmasse.basic_auth.40
      - enmasse.apikey.39

  - name: enmasse.group.40
    members:
      - enmasse.apikey.39
      - enmasse.apikey.40
      - enmasse.basic_auth.39


channel_rest:
  - name: enmasse.channel.rest.1
    service: demo.ping
    url_path: /enmasse.rest.1

  - name: enmasse.channel.rest.2
    service: demo.ping
    url_path: /enmasse.rest.2
    data_format: json

  - name: enmasse.channel.rest.3
    service: demo.ping
    url_path: /enmasse.rest.3
    security: enmasse.basic_auth.4
    data_format: json

  - name: enmasse.channel.rest.4
    service: demo.ping
    url_path: /enmasse.rest.4
    data_format: json
    groups:
      - enmasse.group.5
      - enmasse.group.6

  - name: enmasse.channel.rest.5
    service: demo.ping
    url_path: /enmasse.rest.5

  - name: enmasse.channel.rest.6
    service: demo.ping
    url_path: /enmasse.rest.6
    data_format: json

  - name: enmasse.channel.rest.7
    service: demo.ping
    url_path: /enmasse.rest.7
    security: enmasse.basic_auth.8
    data_format: json

  - name: enmasse.channel.rest.8
    service: demo.ping
    url_path: /enmasse.rest.8
    data_format: json
    groups:
      - enmasse.group.9
      - enmasse.group.10

  - name: enmasse.channel.rest.9
    service: demo.ping
    url_path: /enmasse.rest.9

  - name: enmasse.channel.rest.10
    service: demo.ping
    url_path: /enmasse.rest.10
    data_format: json

  - name: enmasse.channel.rest.11
    service: demo.ping
    url_path: /enmasse.rest.11
    security: enmasse.basic_auth.12
    data_format: json

  - name: enmasse.channel.rest.12
    service: demo.ping
    url_path: /enmasse.rest.12
    data_format: json
    groups:
      - enmasse.group.13
      - enmasse.group.14

  - name: enmasse.channel.rest.13
    service: demo.ping
    url_path: /enmasse.rest.13

  - name: enmasse.channel.rest.14
    service: demo.ping
    url_path: /enmasse.rest.14
    data_format: json

  - name: enmasse.channel.rest.15
    service: demo.ping
    url_path: /enmasse.rest.15
    security: enmasse.basic_auth.16
    data_format: json

  - name: enmasse.channel.rest.16
    service: demo.ping
    url_path: /enmasse.rest.16
    data_format: json
    groups:
      - enmasse.group.17
      - enmasse.group.18

  - name: enmasse.channel.rest.17
    service: demo.ping
    url_path: /enmasse.rest.17

  - name: enmasse.channel.rest.18
    service: demo.ping
    url_path: /enmasse.rest.18
    data_format: json

  - name: enmasse.channel.rest.19
    service: demo.ping
    url_path: /enmasse.rest.19
    security: enmasse.basic_auth.20
    data_format: json

  - name: enmasse.channel.rest.20
    service: demo.ping
    url_path: /enmasse.rest.20
    data_format: json
    groups:
      - enmasse.group.21
      - enmasse.group.22

  - name: enmasse.channel.rest.21
    service: demo.ping
    url_path: /enmasse.rest.21

  - name: enmasse.channel.rest.22
    service: demo.ping
    url_path: /enmasse.rest.22
    data_format: json

  - name: enmasse.channel.rest.23
    service: demo.ping
    url_path: /enmasse.rest.23
    security: enmasse.basic_auth.24
    data_format: json

  - name: enmasse.channel.rest.24
    service: demo.ping
    url_path: /enmasse.rest.24
    data_format: json
    groups:
      - enmasse.group.25
      - enmasse.group.26

  - name: enmasse.channel.rest.25
    service: demo.ping
    url_path: /enmasse.rest.25

  - name: enmasse.channel.rest.26
    service: demo.ping
    url_path: /enmasse.rest.26
    data_format: json

  - name: enmasse.channel.rest.27
    service: demo.ping
    url_path: /enmasse.rest.27
    security: enmasse.basic_auth.28
    data_format: json

  - name: enmasse.channel.rest.28
    service: demo.ping
    url_path: /enmasse.rest.28
    data_format: json
    groups:
      - enmasse.group.29
      - enmasse.group.30

  - name: enmasse.channel.rest.29
    service: demo.ping
    url_path: /enmasse.rest.29

  - name: enmasse.channel.rest.30
    service: demo.ping
    url_path: /enmasse.rest.30
    data_format: json

  - name: enmasse.channel.rest.31
    service: demo.ping
    url_path: /enmasse.rest.31
    security: enmasse.basic_auth.32
    data_format: json

  - name: enmasse.channel.rest.32
    service: demo.ping
    url_path: /enmasse.rest.32
    data_format: json
    groups:
      - enmasse.group.33
      - enmasse.group.34

  - name: enmasse.channel.rest.33
    service: demo.ping
    url_path: /enmasse.rest.33

  - name: enmasse.channel.rest.34
    service: demo.ping
    url_path: /enmasse.rest.34
    data_format: json

  - name: enmasse.channel.rest.35
    service: demo.ping
    url_path: /enmasse.rest.35
    security: enmasse.basic_auth.36
    data_format: json

  - name: enmasse.channel.rest.36
    service: demo.ping
    url_path: /enmasse.rest.36
    data_format: json
    groups:
      - enmasse.group.37
      - enmasse.group.38

  - name: enmasse.channel.rest.37
    service: demo.ping
    url_path: /enmasse.rest.37

  - name: enmasse.channel.rest.38
    service: demo.ping
    url_path: /enmasse.rest.38
    data_format: json

  - name: enmasse.channel.rest.39
    service: demo.ping
    url_path: /enmasse.rest.39
    security: enmasse.basic_auth.40
    data_format: json

  - name: enmasse.channel.rest.40
    service: demo.ping
    url_path: /enmasse.rest.40
    data_format: json
    groups:
      - enmasse.group.1
      - enmasse.group.2

  - name: enmasse.channel.rest.41
    service: demo.ping
    url_path: /enmasse.rest.41

  - name: enmasse.channel.rest.42
    service: demo.ping
    url_path: /enmasse.rest.42
    data_format: json

  - name: enmasse.channel.rest.43
    service: demo.ping
    url_path: /enmasse.rest.43
    security: enmasse.basic_auth.4
    data_format: json

  - name: enmasse.channel.rest.44
    service: demo.ping
    url_path: /enmasse.rest.44
    data_format: json
    groups:
      - enmasse.group.5
      - enmasse.group.6

  - name: enmasse.channel.rest.45
    service: demo.ping
    url_path: /enmasse.rest.45

  - name: enmasse.channel.rest.46
    service: demo.ping
    url_path: /enmasse.rest.46
    data_format: json

  - name: enmasse.channel.rest.47
    service: demo.ping
    url_path: /enmasse.rest.47
    security: enmasse.basic_auth.8
    data_format: json

  - name: enmasse.channel.rest.48
    service: demo.ping
    url_path: /enmasse.rest.48
    data_format: json
    groups:
      - enmasse.group.9
      - enmasse.group.10

  - name: enmasse.channel.rest.49
    service: demo.ping
    url_path: /enmasse.rest.49

  - name: enmasse.channel.rest.50
    service: demo.ping
    url_path: /enmasse.rest.50
    data_format: json

  - name: enmasse.channel.rest.51
    service: demo.ping
    url_path: /enmasse.rest.51
    security: enmasse.basic_auth.12
    data_format: json

  - name: enmasse.channel.rest.52
    service: demo.ping
    url_path: /enmasse.rest.52
    data_format: json
    groups:
      - enmasse.group.13
      - enmasse.group.14

  - name: enmasse.channel.rest.53
    service: demo.ping
    url_path: /enmasse.rest.53

  - name: enmasse.channel.rest.54
    service: demo.ping
    url_path: /enmasse.rest.54
    data_format: json

  - name: enmasse.channel.rest.55
    service: demo.ping
    url_path: /enmasse.rest.55
    security: enmasse.basic_auth.16
    data_format: json

  - name: enmasse.channel.rest.56
    service: demo.ping
    url_path: /enmasse.rest.56
    data_format: json
    groups:
      - enmasse.group.17
      - enmasse.group.18

  - name: enmasse.channel.rest.57
    service: demo.ping
    url_path: /enmasse.rest.57

  - name: enmasse.channel.rest.58
    service: demo.ping
    url_path: /enmasse.rest.58
    data_format: json

  - name: enmasse.channel.rest.59
    service: demo.ping
    url_path: /enmasse.rest.59
    security: enmasse.basic_auth.20
    data_format: json

  - name: enmasse.channel.rest.60
    service: demo.ping
    url_path: /enmasse.rest.60
    data_format: json
    groups:
      - enmasse.group.21
      - enmasse.group.22

  - name: enmasse.channel.rest.61
    service: demo.ping
    url_path: /enmasse.rest.61

  - name: enmasse.channel.rest.62
    service: demo.ping
    url_path: /enmasse.rest.62
    data_format: json

  - name: enmasse.channel.rest.63
    service: demo.ping
    url_path: /enmasse.rest.63
    security: enmasse.basic_auth.24
    data_format: json

  - name: enmasse.channel.rest.64
    service: demo.ping
    url_path: /enmasse.rest.64
    data_format: json
    groups:
      - enmasse.group.25
      - enmasse.group.26

  - name: enmasse.channel.rest.65
    service: demo.ping
    url_path: /enmasse.rest.65

  - name: enmasse.channel.rest.66
    service: demo.ping
    url_path: /enmasse.rest.66
    data_format: json

  - name: enmasse.channel.rest.67
    service: demo.ping
    url_path: /enmasse.rest.67
    security: enmasse.basic_auth.28
    data_format: json

  - name: enmasse.channel.rest.68
    service: demo.ping
    url_path: /enmasse.rest.68
    data_format: json
    groups:
      - enmasse.group.29
      - enmasse.group.30

  - name: enmasse.channel.rest.69
    service: demo.ping
    url_path: /enmasse.rest.69

  - name: enmasse.channel.rest.70
    service: demo.ping
    url_path: /enmasse.rest.70
    data_format: json

  - name: enmasse.channel.rest.71
    service: demo.ping
    url_path: /enmasse.rest.71
    security: enmasse.basic_auth.32
    data_format: json

  - name: enmasse.channel.rest.72
    service: demo.ping
    url_path: /enmasse.rest.72
    data_format: json
    groups:
      - enmasse.group.33
      - enmasse.group.34

  - name: enmasse.channel.rest.73
    service: demo.ping
    url_path: /enmasse.rest.73

  - name: enmasse.channel.rest.74
    service: demo.ping
    url_path: /enmasse.rest.74
    data_format: json

  - name: enmasse.channel.rest.75
    service: demo.ping
    url_path: /enmasse.rest.75
    security: enmasse.basic_auth.36
    data_format: json

  - name: enmasse.channel.rest.76
    service: demo.ping
    url_path: /enmasse.rest.76
    data_format: json
    groups:
      - enmasse.group.37
      - enmasse.group.38

  - name: enmasse.channel.rest.77
    service: demo.ping
    url_path: /enmasse.rest.77

  - name: enmasse.channel.rest.78
    service: demo.ping
    url_path: /enmasse.rest.78
    data_format: json

  - name: enmasse.channel.rest.79
    service: demo.ping
    url_path: /enmasse.rest.79
    security: enmasse.basic_auth.40
    data_format: json

  - name: enmasse.channel.rest.80
    service: demo.ping
    url_path: /enmasse.rest.80
    data_format: json
    groups:
      - enmasse.group.1
      - enmasse.group.2


outgoing_rest:
  - name: enmasse.outgoing.rest.1
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.2
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/2
    security: enmasse.bearer_token.3
    timeout: 20

  - name: enmasse.outgoing.rest.3
    host: https://example.azurewebsites.net
    url_path: /abc/3
    data_format: json

  - name: enmasse.outgoing.rest.4
    host: https://example.com
    url_path: /abc/4
    ping_method: GET

  - name: enmasse.outgoing.rest.5
    host: https://example.com
    url_path: /abc/5
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.6
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.7
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/7
    security: enmasse.bearer_token.8
    timeout: 20

  - name: enmasse.outgoing.rest.8
    host: https://example.azurewebsites.net
    url_path: /abc/8
    data_format: json

  - name: enmasse.outgoing.rest.9
    host: https://example.com
    url_path: /abc/9
    ping_method: GET

  - name: enmasse.outgoing.rest.10
    host: https://example.com
    url_path: /abc/10
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.11
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.12
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/12
    security: enmasse.bearer_token.13
    timeout: 20

  - name: enmasse.outgoing.rest.13
    host: https://example.azurewebsites.net
    url_path: /abc/13
    data_format: json

  - name: enmasse.outgoing.rest.14
    host: https://example.com
    url_path: /abc/14
    ping_method: GET

  - name: enmasse.outgoing.rest.15
    host: https://example.com
    url_path: /abc/15
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.16
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.17
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/17
    security: enmasse.bearer_token.18
    timeout: 20

  - name: enmasse.outgoing.rest.18
    host: https://example.azurewebsites.net
    url_path: /abc/18
    data_format: json

  - name: enmasse.outgoing.rest.19
    host: https://example.com
    url_path: /abc/19
    ping_method: GET

  - name: enmasse.outgoing.rest.20
    host: https://example.com
    url_path: /abc/20
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.21
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.22
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/22
    security: enmasse.bearer_token.23
    timeout: 20

  - name: enmasse.outgoing.rest.23
    host: https://example.azurewebsites.net
    url_path: /abc/23
    data_format: json

  - name: enmasse.outgoing.rest.24
    host: https://example.com
    url_path: /abc/24
    ping_method: GET

  - name: enmasse.outgoing.rest.25
    host: https://example.com
    url_path: /abc/25
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.26
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.27
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/27
    security: enmasse.bearer_token.28
    timeout: 20

  - name: enmasse.outgoing.rest.28
    host: https://example.azurewebsites.net
    url_path: /abc/28
    data_format: json

  - name: enmasse.outgoing.rest.29
    host: https://example.com
    url_path: /abc/29
    ping_method: GET

  - name: enmasse.outgoing.rest.30
    host: https://example.com
    url_path: /abc/30
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.31
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.32
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/32
    security: enmasse.bearer_token.33
    timeout: 20

  - name: enmasse.outgoing.rest.33
    host: https://example.azurewebsites.net
    url_path: /abc/33
    data_format: json

  - name: enmasse.outgoing.rest.34
    host: https://example.com
    url_path: /abc/34
    ping_method: GET

  - name: enmasse.outgoing.rest.35
    host: https://example.com
    url_path: /abc/35
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.36
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.37
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/37
    security: enmasse.bearer_token.38
    timeout: 20

  - name: enmasse.outgoing.rest.38
    host: https://example.azurewebsites.net
    url_path: /abc/38
    data_format: json

  - name: enmasse.outgoing.rest.39
    host: https://example.com
    url_path: /abc/39
    ping_method: GET

  - name: enmasse.outgoing.rest.40
    host: https://example.com
    url_path: /abc/40
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.41
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.42
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/42
    security: enmasse.bearer_token.3
    timeout: 20

  - name: enmasse.outgoing.rest.43
    host: https://example.azurewebsites.net
    url_path: /abc/43
    data_format: json

  - name: enmasse.outgoing.rest.44
    host: https://example.com
    url_path: /abc/44
    ping_method: GET

  - name: enmasse.outgoing.rest.45
    host: https://example.com
    url_path: /abc/45
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.46
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.47
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/47
    security: enmasse.bearer_token.8
    timeout: 20

  - name: enmasse.outgoing.rest.48
    host: https://example.azurewebsites.net
    url_path: /abc/48
    data_format: json

  - name: enmasse.outgoing.rest.49
    host: https://example.com
    url_path: /abc/49
    ping_method: GET

  - name: enmasse.outgoing.rest.50
    host: https://example.com
    url_path: /abc/50
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.51
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.52
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/52
    security: enmasse.bearer_token.13
    timeout: 20

  - name: enmasse.outgoing.rest.53
    host: https://example.azurewebsites.net
    url_path: /abc/53
    data_format: json

  - name: enmasse.outgoing.rest.54
    host: https://example.com
    url_path: /abc/54
    ping_method: GET

  - name: enmasse.outgoing.rest.55
    host: https://example.com
    url_path: /abc/55
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.56
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.57
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/57
    security: enmasse.bearer_token.18
    timeout: 20

  - name: enmasse.outgoing.rest.58
    host: https://example.azurewebsites.net
    url_path: /abc/58
    data_format: json

  - name: enmasse.outgoing.rest.59
    host: https://example.com
    url_path: /abc/59
    ping_method: GET

  - name: enmasse.outgoing.rest.60
    host: https://example.com
    url_path: /abc/60
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.61
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.62
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/62
    security: enmasse.bearer_token.23
    timeout: 20

  - name: enmasse.outgoing.rest.63
    host: https://example.azurewebsites.net
    url_path: /abc/63
    data_format: json

  - name: enmasse.outgoing.rest.64
    host: https://example.com
    url_path: /abc/64
    ping_method: GET

  - name: enmasse.outgoing.rest.65
    host: https://example.com
    url_path: /abc/65
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.66
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.67
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/67
    security: enmasse.bearer_token.28
    timeout: 20

  - name: enmasse.outgoing.rest.68
    host: https://example.azurewebsites.net
    url_path: /abc/68
    data_format: json

  - name: enmasse.outgoing.rest.69
    host: https://example.com
    url_path: /abc/69
    ping_method: GET

  - name: enmasse.outgoing.rest.70
    host: https://example.com
    url_path: /abc/70
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.71
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.72
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/72
    security: enmasse.bearer_token.33
    timeout: 20

  - name: enmasse.outgoing.rest.73
    host: https://example.azurewebsites.net
    url_path: /abc/73
    data_format: json

  - name: enmasse.outgoing.rest.74
    host: https://example.com
    url_path: /abc/74
    ping_method: GET

  - name: enmasse.outgoing.rest.75
    host: https://example.com
    url_path: /abc/75
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.76
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.77
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/77
    security: enmasse.bearer_token.38
    timeout: 20

  - name: enmasse.outgoing.rest.78
    host: https://example.azurewebsites.net
    url_path: /abc/78
    data_format: json

  - name: enmasse.outgoing.rest.79
    host: https://example.com
    url_path: /abc/79
    ping_method: GET

  - name: enmasse.outgoing.rest.80
    host: https://example.com
    url_path: /abc/80
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.81
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.82
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/82
    security: enmasse.bearer_token.3
    timeout: 20

  - name: enmasse.outgoing.rest.83
    host: https://example.azurewebsites.net
    url_path: /abc/83
    data_format: json

  - name: enmasse.outgoing.rest.84
    host: https://example.com
    url_path: /abc/84
    ping_method: GET

  - name: enmasse.outgoing.rest.85
    host: https://example.com
    url_path: /abc/85
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.86
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.87
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/87
    security: enmasse.bearer_token.8
    timeout: 20

  - name: enmasse.outgoing.rest.88
    host: https://example.azurewebsites.net
    url_path: /abc/88
    data_format: json

  - name: enmasse.outgoing.rest.89
    host: https://example.com
    url_path: /abc/89
    ping_method: GET

  - name: enmasse.outgoing.rest.90
    host: https://example.com
    url_path: /abc/90
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.91
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.92
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/92
    security: enmasse.bearer_token.13
    timeout: 20

  - name: enmasse.outgoing.rest.93
    host: https://example.azurewebsites.net
    url_path: /abc/93
    data_format: json

  - name: enmasse.outgoing.rest.94
    host: https://example.com
    url_path: /abc/94
    ping_method: GET

  - name: enmasse.outgoing.rest.95
    host: https://example.com
    url_path: /abc/95
    ping_method: GET
    tls_verify: false

  - name: enmasse.outgoing.rest.96
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.97
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/97
    security: enmasse.bearer_token.18
    timeout: 20

  - name: enmasse.outgoing.rest.98
    host: https://example.azurewebsites.net
    url_path: /abc/98
    data_format: json

  - name: enmasse.outgoing.rest.99
    host: https://example.com
    url_path: /abc/99
    ping_method: GET

  - name: enmasse.outgoing.rest.100
    host: https://example.com
    url_path: /abc/100
    ping_method: GET
    tls_verify: false


scheduler:
  - name: enmasse.scheduler.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 2
    is_active: True

  - name: enmasse.scheduler.2
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 3

  - name: enmasse.scheduler.3
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 4

  - name: enmasse.scheduler.4
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 5

  - name: enmasse.scheduler.5
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 6
    is_active: True

  - name: enmasse.scheduler.6
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 7

  - name: enmasse.scheduler.7
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 8

  - name: enmasse.scheduler.8
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 9

  - name: enmasse.scheduler.9
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 10
    is_active: True

  - name: enmasse.scheduler.10
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 11

  - name: enmasse.scheduler.11
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 12

  - name: enmasse.scheduler.12
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 13

  - name: enmasse.scheduler.13
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 14
    is_active: True

  - name: enmasse.scheduler.14
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 15

  - name: enmasse.scheduler.15
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 16

  - name: enmasse.scheduler.16
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 17

  - name: enmasse.scheduler.17
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 18
    is_active: True

  - name: enmasse.scheduler.18
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 19

  - name: enmasse.scheduler.19
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 20

  - name: enmasse.scheduler.20
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 21

  - name: enmasse.scheduler.21
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 22
    is_active: True

  - name: enmasse.scheduler.22
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 23

  - name: enmasse.scheduler.23
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 1

  - name: enmasse.scheduler.24
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 25

  - name: enmasse.scheduler.25
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 26
    is_active: True

  - name: enmasse.scheduler.26
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 27

  - name: enmasse.scheduler.27
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 5

  - name: enmasse.scheduler.28
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 1

  - name: enmasse.scheduler.29
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 30
    is_active: True

  - name: enmasse.scheduler.30
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 31

  - name: enmasse.scheduler.31
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 9

  - name: enmasse.scheduler.32
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 5

  - name: enmasse.scheduler.33
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 34
    is_active: True

  - name: enmasse.scheduler.34
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 35

  - name: enmasse.scheduler.35
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 13

  - name: enmasse.scheduler.36
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 9

  - name: enmasse.scheduler.37
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 38
    is_active: True

  - name: enmasse.scheduler.38
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 39

  - name: enmasse.scheduler.39
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 17

  - name: enmasse.scheduler.40
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 13

  - name: enmasse.scheduler.41
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 42
    is_active: True

  - name: enmasse.scheduler.42
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 43

  - name: enmasse.scheduler.43
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 21

  - name: enmasse.scheduler.44
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 17

  - name: enmasse.scheduler.45
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 46
    is_active: True

  - name: enmasse.scheduler.46
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 47

  - name: enmasse.scheduler.47
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 2

  - name: enmasse.scheduler.48
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 21

  - name: enmasse.scheduler.49
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 50
    is_active: True

  - name: enmasse.scheduler.50
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 51

  - name: enmasse.scheduler.51
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 6

  - name: enmasse.scheduler.52
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 25

  - name: enmasse.scheduler.53
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 54
    is_active: True

  - name: enmasse.scheduler.54
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 55

  - name: enmasse.scheduler.55
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 10

  - name: enmasse.scheduler.56
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 1

  - name: enmasse.scheduler.57
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 58
    is_active: True

  - name: enmasse.scheduler.58
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 59

  - name: enmasse.scheduler.59
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 14

  - name: enmasse.scheduler.60
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 5

  - name: enmasse.scheduler.61
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 3
    is_active: True

  - name: enmasse.scheduler.62
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 4

  - name: enmasse.scheduler.63
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 18

  - name: enmasse.scheduler.64
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 9

  - name: enmasse.scheduler.65
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 7
    is_active: True

  - name: enmasse.scheduler.66
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 8

  - name: enmasse.scheduler.67
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 22

  - name: enmasse.scheduler.68
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 13

  - name: enmasse.scheduler.69
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 11
    is_active: True

  - name: enmasse.scheduler.70
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 12

  - name: enmasse.scheduler.71
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 3

  - name: enmasse.scheduler.72
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 17

  - name: enmasse.scheduler.73
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 15
    is_active: True

  - name: enmasse.scheduler.74
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 16

  - name: enmasse.scheduler.75
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 7

  - name: enmasse.scheduler.76
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 21

  - name: enmasse.scheduler.77
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 19
    is_active: True

  - name: enmasse.scheduler.78
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 20

  - name: enmasse.scheduler.79
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 11

  - name: enmasse.scheduler.80
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 25


ldap:
  - name: enmasse.ldap.1
    username: 'CN=enmasse1,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.1:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password1

  - name: enmasse.ldap.2
    username: 'CN=enmasse2,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.2:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password2

  - name: enmasse.ldap.3
    username: 'CN=enmasse3,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.3:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password3

  - name: enmasse.ldap.4
    username: 'CN=enmasse4,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.4:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password4

  - name: enmasse.ldap.5
    username: 'CN=enmasse5,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.5:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password5

  - name: enmasse.ldap.6
    username: 'CN=enmasse6,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.6:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password6

  - name: enmasse.ldap.7
    username: 'CN=enmasse7,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.7:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password7

  - name: enmasse.ldap.8
    username: 'CN=enmasse8,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.8:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password8

  - name: enmasse.ldap.9
    username: 'CN=enmasse9,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.9:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password9

  - name: enmasse.ldap.10
    username: 'CN=enmasse10,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.10:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password10

  - name: enmasse.ldap.11
    username: 'CN=enmasse11,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.11:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password11

  - name: enmasse.ldap.12
    username: 'CN=enmasse12,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.12:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password12

  - name: enmasse.ldap.13
    username: 'CN=enmasse13,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.13:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password13

  - name: enmasse.ldap.14
    username: 'CN=enmasse14,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.14:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password14

  - name: enmasse.ldap.15
    username: 'CN=enmasse15,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.15:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password15

  - name: enmasse.ldap.16
    username: 'CN=enmasse16,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.16:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password16

  - name: enmasse.ldap.17
    username: 'CN=enmasse17,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.17:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password17

  - name: enmasse.ldap.18
    username: 'CN=enmasse18,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.18:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password18

  - name: enmasse.ldap.19
    username: 'CN=enmasse19,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.19:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password19

  - name: enmasse.ldap.20
    username: 'CN=enmasse20,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.20:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password20


sql:
  - name: enmasse.sql.1
    type: mysql
    host: 127.0.0.2
    port: 3306
    db_name: MYDB_2
    username: enmasse.1
    password: Zato_Enmasse_Env.SQL_Password_1

  - name: enmasse.sql.2
    type: oracle
    host: 10.152.81.3
    port: 1521
    db_name: MYDB_3
    username: enmasse.2
    password: Zato_Enmasse_Env.SQL_Password_2
    extra: connect_timeout=3
    pool_size: 3

  - name: enmasse.sql.3
    type: mysql
    host: 127.0.0.4
    port: 3306
    db_name: MYDB_4
    username: enmasse.3
    password: Zato_Enmasse_Env.SQL_Password_3

  - name: enmasse.sql.4
    type: oracle
    host: 10.152.81.5
    port: 1521
    db_name: MYDB_5
    username: enmasse.4
    password: Zato_Enmasse_Env.SQL_Password_4
    extra: connect_timeout=5
    pool_size: 5

  - name: enmasse.sql.5
    type: mysql
    host: 127.0.0.6
    port: 3306
    db_name: MYDB_6
    username: enmasse.5
    password: Zato_Enmasse_Env.SQL_Password_5

  - name: enmasse.sql.6
    type: oracle
    host: 10.152.81.7
    port: 1521
    db_name: MYDB_7
    username: enmasse.6
    password: Zato_Enmasse_Env.SQL_Password_6
    extra: connect_timeout=7
    pool_size: 7

  - name: enmasse.sql.7
    type: mysql
    host: 127.0.0.8
    port: 3306
    db_name: MYDB_8
    username: enmasse.7
    password: Zato_Enmasse_Env.SQL_Password_7

  - name: enmasse.sql.8
    type: oracle
    host: 10.152.81.9
    port: 1521
    db_name: MYDB_9
    username: enmasse.8
    password: Zato_Enmasse_Env.SQL_Password_8
    extra: connect_timeout=9
    pool_size: 9

  - name: enmasse.sql.9
    type: mysql
    host: 127.0.0.10
    port: 3306
    db_name: MYDB_10
    username: enmasse.9
    password: Zato_Enmasse_Env.SQL_Password_9

  - name: enmasse.sql.10
    type: oracle
    host: 10.152.81.11
    port: 1521
    db_name: MYDB_1
    username: enmasse.10
    password: Zato_Enmasse_Env.SQL_Password_10
    extra: connect_timeout=11
    pool_size: 11

  - name: enmasse.sql.11
    type: mysql
    host: 127.0.0.12
    port: 3306
    db_name: MYDB_2
    username: enmasse.11
    password: Zato_Enmasse_Env.SQL_Password_11

  - name: enmasse.sql.12
    type: oracle
    host: 10.152.81.13
    port: 1521
    db_name: MYDB_3
    username: enmasse.12
    password: Zato_Enmasse_Env.SQL_Password_12
    extra: connect_timeout=13
    pool_size: 13

  - name: enmasse.sql.13
    type: mysql
    host: 127.0.0.14
    port: 3306
    db_name: MYDB_4
    username: enmasse.13
    password: Zato_Enmasse_Env.SQL_Password_13

  - name: enmasse.sql.14
    type: oracle
    host: 10.152.81.15
    port: 1521
    db_name: MYDB_5
    username: enmasse.14
    password: Zato_Enmasse_Env.SQL_Password_14
    extra: connect_timeout=15
    pool_size: 15

  - name: enmasse.sql.15
    type: mysql
    host: 127.0.0.16
    port: 3306
    db_name: MYDB_6
    username: enmasse.15
    password: Zato_Enmasse_Env.SQL_Password_15

  - name: enmasse.sql.16
    type: oracle
    host: 10.152.81.17
    port: 1521
    db_name: MYDB_7
    username: enmasse.16
    password: Zato_Enmasse_Env.SQL_Password_16
    extra: connect_timeout=17
    pool_size: 17

  - name: enmasse.sql.17
    type: mysql
    host: 127.0.0.18
    port: 3306
    db_name: MYDB_8
    username: enmasse.17
    password: Zato_Enmasse_Env.SQL_Password_17

  - name: enmasse.sql.18
    type: oracle
    host: 10.152.81.19
    port: 1521
    db_name: MYDB_9
    username: enmasse.18
    password: Zato_Enmasse_Env.SQL_Password_18
    extra: connect_timeout=19
    pool_size: 19

  - name: enmasse.sql.19
    type: mysql
    host: 127.0.0.20
    port: 3306
    db_name: MYDB_10
    username: enmasse.19
    password: Zato_Enmasse_Env.SQL_Password_19

  - name: enmasse.sql.20
    type: oracle
    host: 10.152.81.21
    port: 1521
    db_name: MYDB_1
    username: enmasse.20
    password: Zato_Enmasse_Env.SQL_Password_20
    extra: connect_timeout=21
    pool_size: 1

  - name: enmasse.sql.21
    type: mysql
    host: 127.0.0.22
    port: 3306
    db_name: MYDB_2
    username: enmasse.21
    password: Zato_Enmasse_Env.SQL_Password_21

  - name: enmasse.sql.22
    type: oracle
    host: 10.152.81.23
    port: 1521
    db_name: MYDB_3
    username: enmasse.22
    password: Zato_Enmasse_Env.SQL_Password_22
    extra: connect_timeout=23
    pool_size: 3

  - name: enmasse.sql.23
    type: mysql
    host: 127.0.0.24
    port: 3306
    db_name: MYDB_4
    username: enmasse.23
    password: Zato_Enmasse_Env.SQL_Password_23

  - name: enmasse.sql.24
    type: oracle
    host: 10.152.81.25
    port: 1521
    db_name: MYDB_5
    username: enmasse.24
    password: Zato_Enmasse_Env.SQL_Password_24
    extra: connect_timeout=25
    pool_size: 5

  - name: enmasse.sql.25
    type: mysql
    host: 127.0.0.26
    port: 3306
    db_name: MYDB_6
    username: enmasse.25
    password: Zato_Enmasse_Env.SQL_Password_25

  - name: enmasse.sql.26
    type: oracle
    host: 10.152.81.27
    port: 1521
    db_name: MYDB_7
    username: enmasse.26
    password: Zato_Enmasse_Env.SQL_Password_26
    extra: connect_timeout=27
    pool_size: 7

  - name: enmasse.sql.27
    type: mysql
    host: 127.0.0.28
    port: 3306
    db_name: MYDB_8
    username: enmasse.27
    password: Zato_Enmasse_Env.SQL_Password_27

  - name: enmasse.sql.28
    type: oracle
    host: 10.152.81.29
    port: 1521
    db_name: MYDB_9
    username: enmasse.28
    password: Zato_Enmasse_Env.SQL_Password_28
    extra: connect_timeout=29
    pool_size: 9

  - name: enmasse.sql.29
    type: mysql
    host: 127.0.0.30
    port: 3306
    db_name: MYDB_10
    username: enmasse.29
    password: Zato_Enmasse_Env.SQL_Password_29

  - name: enmasse.sql.30
    type: oracle
    host: 10.152.81.31
    port: 1521
    db_name: MYDB_1
    username: enmasse.30
    password: Zato_Enmasse_Env.SQL_Password_30
    extra: connect_timeout=1
    pool_size: 11

  - name: enmasse.sql.31
    type: mysql
    host: 127.0.0.32
    port: 3306
    db_name: MYDB_2
    username: enmasse.31
    password: Zato_Enmasse_Env.SQL_Password_31

  - name: enmasse.sql.32
    type: oracle
    host: 10.152.81.33
    port: 1521
    db_name: MYDB_3
    username: enmasse.32
    password: Zato_Enmasse_Env.SQL_Password_32
    extra: connect_timeout=3
    pool_size: 13

  - name: enmasse.sql.33
    type: mysql
    host: 127.0.0.34
    port: 3306
    db_name: MYDB_4
    username: enmasse.33
    password: Zato_Enmasse_Env.SQL_Password_33

  - name: enmasse.sql.34
    type: oracle
    host: 10.152.81.35
    port: 1521
    db_name: MYDB_5
    username: enmasse.34
    password: Zato_Enmasse_Env.SQL_Password_34
    extra: connect_timeout=5
    pool_size: 15

  - name: enmasse.sql.35
    type: mysql
    host: 127.0.0.36
    port: 3306
    db_name: MYDB_6
    username: enmasse.35
    password: Zato_Enmasse_Env.SQL_Password_35

  - name: enmasse.sql.36
    type: oracle
    host: 10.152.81.37
    port: 1521
    db_name: MYDB_7
    username: enmasse.36
    password: Zato_Enmasse_Env.SQL_Password_36
    extra: connect_timeout=7
    pool_size: 17

  - name: enmasse.sql.37
    type: mysql
    host: 127.0.0.38
    port: 3306
    db_name: MYDB_8
    username: enmasse.37
    password: Zato_Enmasse_Env.SQL_Password_37

  - name: enmasse.sql.38
    type: oracle
    host: 10.152.81.39
    port: 1521
    db_name: MYDB_9
    username: enmasse.38
    password: Zato_Enmasse_Env.SQL_Password_38
    extra: connect_timeout=9
    pool_size: 19

  - name: enmasse.sql.39
    type: mysql
    host: 127.0.0.40
    port: 3306
    db_name: MYDB_10
    username: enmasse.39
    password: Zato_Enmasse_Env.SQL_Password_39

  - name: enmasse.sql.40
    type: oracle
    host: 10.152.81.41
    port: 1521
    db_name: MYDB_1
    username: enmasse.40
    password: Zato_Enmasse_Env.SQL_Password_40
    extra: connect_timeout=11
    pool_size: 1


outgoing_soap:
  - name: enmasse.outgoing.soap.1
    host: https://example1.com
    url_path: /SOAP
    security: enmasse.ntlm.1
    soap_action: urn:microsoft-dynamics-schemas/page/example1:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 21

  - name: enmasse.outgoing.soap.2
    host: https://example2.com
    url_path: /SOAP
    security: enmasse.ntlm.2
    soap_action: urn:microsoft-dynamics-schemas/page/example2:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 22

  - name: enmasse.outgoing.soap.3
    host: https://example3.com
    url_path: /SOAP
    security: enmasse.ntlm.3
    soap_action: urn:microsoft-dynamics-schemas/page/example3:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 23

  - name: enmasse.outgoing.soap.4
    host: https://example4.com
    url_path: /SOAP
    security: enmasse.ntlm.4
    soap_action: urn:microsoft-dynamics-schemas/page/example4:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 24

  - name: enmasse.outgoing.soap.5
    host: https://example5.com
    url_path: /SOAP
    security: enmasse.ntlm.5
    soap_action: urn:microsoft-dynamics-schemas/page/example5:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 25

  - name: enmasse.outgoing.soap.6
    host: https://example6.com
    url_path: /SOAP
    security: enmasse.ntlm.6
    soap_action: urn:microsoft-dynamics-schemas/page/example6:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 26

  - name: enmasse.outgoing.soap.7
    host: https://example7.com
    url_path: /SOAP
    security: enmasse.ntlm.7
    soap_action: urn:microsoft-dynamics-schemas/page/example7:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 27

  - name: enmasse.outgoing.soap.8
    host: https://example8.com
    url_path: /SOAP
    security: enmasse.ntlm.8
    soap_action: urn:microsoft-dynamics-schemas/page/example8:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 28

  - name: enmasse.outgoing.soap.9
    host: https://example9.com
    url_path: /SOAP
    security: enmasse.ntlm.9
    soap_action: urn:microsoft-dynamics-schemas/page/example9:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 29

  - name: enmasse.outgoing.soap.10
    host: https://example10.com
    url_path: /SOAP
    security: enmasse.ntlm.10
    soap_action: urn:microsoft-dynamics-schemas/page/example10:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 30

  - name: enmasse.outgoing.soap.11
    host: https://example11.com
    url_path: /SOAP
    security: enmasse.ntlm.11
    soap_action: urn:microsoft-dynamics-schemas/page/example11:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 31

  - name: enmasse.outgoing.soap.12
    host: https://example12.com
    url_path: /SOAP
    security: enmasse.ntlm.12
    soap_action: urn:microsoft-dynamics-schemas/page/example12:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 32

  - name: enmasse.outgoing.soap.13
    host: https://example13.com
    url_path: /SOAP
    security: enmasse.ntlm.13
    soap_action: urn:microsoft-dynamics-schemas/page/example13:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 33

  - name: enmasse.outgoing.soap.14
    host: https://example14.com
    url_path: /SOAP
    security: enmasse.ntlm.14
    soap_action: urn:microsoft-dynamics-schemas/page/example14:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 34

  - name: enmasse.outgoing.soap.15
    host: https://example15.com
    url_path: /SOAP
    security: enmasse.ntlm.15
    soap_action: urn:microsoft-dynamics-schemas/page/example15:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 35

  - name: enmasse.outgoing.soap.16
    host: https://example16.com
    url_path: /SOAP
    security: enmasse.ntlm.16
    soap_action: urn:microsoft-dynamics-schemas/page/example16:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 36

  - name: enmasse.outgoing.soap.17
    host: https://example17.com
    url_path: /SOAP
    security: enmasse.ntlm.17
    soap_action: urn:microsoft-dynamics-schemas/page/example17:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 37

  - name: enmasse.outgoing.soap.18
    host: https://example18.com
    url_path: /SOAP
    security: enmasse.ntlm.18
    soap_action: urn:microsoft-dynamics-schemas/page/example18:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 38

  - name: enmasse.outgoing.soap.19
    host: https://example19.com
    url_path: /SOAP
    security: enmasse.ntlm.19
    soap_action: urn:microsoft-dynamics-schemas/page/example19:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 39

  - name: enmasse.outgoing.soap.20
    host: https://example20.com
    url_path: /SOAP
    security: enmasse.ntlm.20
    soap_action: urn:microsoft-dynamics-schemas/page/example20:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 40


microsoft_365:
  - name: enmasse.cloud.microsoft365.1
    is_active: true
    client_id: 00000001-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue1
    scopes: Mail.Read Mail.Send
    tenant_id: 00000039-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.2
    is_active: true
    client_id: 00000002-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue2
    scopes: Mail.Read Mail.Send
    tenant_id: 00000038-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.3
    is_active: true
    client_id: 00000003-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue3
    scopes: Mail.Read Mail.Send
    tenant_id: 00000037-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.4
    is_active: true
    client_id: 00000004-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue4
    scopes: Mail.Read Mail.Send
    tenant_id: 00000036-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.5
    is_active: true
    client_id: 00000005-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue5
    scopes: Mail.Read Mail.Send
    tenant_id: 00000035-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.6
    is_active: true
    client_id: 00000006-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue6
    scopes: Mail.Read Mail.Send
    tenant_id: 00000034-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.7
    is_active: true
    client_id: 00000007-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue7
    scopes: Mail.Read Mail.Send
    tenant_id: 00000033-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.8
    is_active: true
    client_id: 00000008-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue8
    scopes: Mail.Read Mail.Send
    tenant_id: 00000032-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.9
    is_active: true
    client_id: 00000009-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue9
    scopes: Mail.Read Mail.Send
    tenant_id: 00000031-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.10
    is_active: true
    client_id: 00000010-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue10
    scopes: Mail.Read Mail.Send
    tenant_id: 00000030-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.11
    is_active: true
    client_id: 00000011-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue11
    scopes: Mail.Read Mail.Send
    tenant_id: 00000029-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.12
    is_active: true
    client_id: 00000012-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue12
    scopes: Mail.Read Mail.Send
    tenant_id: 00000028-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.13
    is_active: true
    client_id: 00000013-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue13
    scopes: Mail.Read Mail.Send
    tenant_id: 00000027-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.14
    is_active: true
    client_id: 00000014-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue14
    scopes: Mail.Read Mail.Send
    tenant_id: 00000026-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.15
    is_active: true
    client_id: 00000015-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue15
    scopes: Mail.Read Mail.Send
    tenant_id: 00000025-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.16
    is_active: true
    client_id: 00000016-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue16
    scopes: Mail.Read Mail.Send
    tenant_id: 00000024-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.17
    is_active: true
    client_id: 00000017-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue17
    scopes: Mail.Read Mail.Send
    tenant_id: 00000023-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.18
    is_active: true
    client_id: 00000018-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue18
    scopes: Mail.Read Mail.Send
    tenant_id: 00000022-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.19
    is_active: true
    client_id: 00000019-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue19
    scopes: Mail.Read Mail.Send
    tenant_id: 00000021-4321-4321-4321-987654321000

  - name: enmasse.cloud.microsoft365.20
    is_active: true
    client_id: 00000020-1234-1234-1234-123456789000
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue20
    scopes: Mail.Read Mail.Send
    tenant_id: 00000020-4321-4321-4321-987654321000


cache:
  - name: enmasse.cache.builtin.1
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.2
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.3
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.4
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.5
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.6
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.7
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.8
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.9
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.10
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.11
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.12
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.13
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.14
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.15
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.16
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.17
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.18
    extend_expiry_on_get: true
    extend_expiry_on_set: false

  - name: enmasse.cache.builtin.19
    extend_expiry_on_get: false
    extend_expiry_on_set: true

  - name: enmasse.cache.builtin.20
    extend_expiry_on_get: true
    extend_expiry_on_set: false


confluence:
  - name: enmasse.confluence.1
    address: https://example1.atlassian.net
    username: api_user1@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken1

  - name: enmasse.confluence.2
    address: https://example2.atlassian.net
    username: api_user2@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken2

  - name: enmasse.confluence.3
    address: https://example3.atlassian.net
    username: api_user3@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken3

  - name: enmasse.confluence.4
    address: https://example4.atlassian.net
    username: api_user4@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken4

  - name: enmasse.confluence.5
    address: https://example5.atlassian.net
    username: api_user5@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken5

  - name: enmasse.confluence.6
    address: https://example6.atlassian.net
    username: api_user6@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken6

  - name: enmasse.confluence.7
    address: https://example7.atlassian.net
    username: api_user7@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken7

  - name: enmasse.confluence.8
    address: https://example8.atlassian.net
    username: api_user8@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken8

  - name: enmasse.confluence.9
    address: https://example9.atlassian.net
    username: api_user9@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken9

  - name: enmasse.confluence.10
    address: https://example10.atlassian.net
    username: api_user10@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken10

  - name: enmasse.confluence.11
    address: https://example11.atlassian.net
    username: api_user11@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken11

  - name: enmasse.confluence.12
    address: https://example12.atlassian.net
    username: api_user12@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken12

  - name: enmasse.confluence.13
    address: https://example13.atlassian.net
    username: api_user13@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken13

  - name: enmasse.confluence.14
    address: https://example14.atlassian.net
    username: api_user14@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken14

  - name: enmasse.confluence.15
    address: https://example15.atlassian.net
    username: api_user15@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken15

  - name: enmasse.confluence.16
    address: https://example16.atlassian.net
    username: api_user16@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken16

  - name: enmasse.confluence.17
    address: https://example17.atlassian.net
    username: api_user17@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken17

  - name: enmasse.confluence.18
    address: https://example18.atlassian.net
    username: api_user18@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken18

  - name: enmasse.confluence.19
    address: https://example19.atlassian.net
    username: api_user19@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken19

  - name: enmasse.confluence.20
    address: https://example20.atlassian.net
    username: api_user20@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken20


email_imap:
  - name: enmasse.email.imap.1
    host: imap1.example.com
    port: 993
    username: enmasse1@example.com
    password: Zato_Enmasse_Env.IMAPPassword1

  - name: enmasse.email.imap.2
    host: imap2.example.com
    port: 993
    username: enmasse2@example.com
    password: Zato_Enmasse_Env.IMAPPassword2

  - name: enmasse.email.imap.3
    host: imap3.example.com
    port: 993
    username: enmasse3@example.com
    password: Zato_Enmasse_Env.IMAPPassword3

  - name: enmasse.email.imap.4
    host: imap4.example.com
    port: 993
    username: enmasse4@example.com
    password: Zato_Enmasse_Env.IMAPPassword4

  - name: enmasse.email.imap.5
    host: imap5.example.com
    port: 993
    username: enmasse5@example.com
    password: Zato_Enmasse_Env.IMAPPassword5

  - name: enmasse.email.imap.6
    host: imap6.example.com
    port: 993
    username: enmasse6@example.com
    password: Zato_Enmasse_Env.IMAPPassword6

  - name: enmasse.email.imap.7
    host: imap7.example.com
    port: 993
    username: enmasse7@example.com
    password: Zato_Enmasse_Env.IMAPPassword7

  - name: enmasse.email.imap.8
    host: imap8.example.com
    port: 993
    username: enmasse8@example.com
    password: Zato_Enmasse_Env.IMAPPassword8

  - name: enmasse.email.imap.9
    host: imap9.example.com
    port: 993
    username: enmasse9@example.com
    password: Zato_Enmasse_Env.IMAPPassword9

  - name: enmasse.email.imap.10
    host: imap10.example.com
    port: 993
    username: enmasse10@example.com
    password: Zato_Enmasse_Env.IMAPPassword10

  - name: enmasse.email.imap.11
    host: imap11.example.com
    port: 993
    username: enmasse11@example.com
    password: Zato_Enmasse_Env.IMAPPassword11

  - name: enmasse.email.imap.12
    host: imap12.example.com
    port: 993
    username: enmasse12@example.com
    password: Zato_Enmasse_Env.IMAPPassword12

  - name: enmasse.email.imap.13
    host: imap13.example.com
    port: 993
    username: enmasse13@example.com
    password: Zato_Enmasse_Env.IMAPPassword13

  - name: enmasse.email.imap.14
    host: imap14.example.com
    port: 993
    username: enmasse14@example.com
    password: Zato_Enmasse_Env.IMAPPassword14

  - name: enmasse.email.imap.15
    host: imap15.example.com
    port: 993
    username: enmasse15@example.com
    password: Zato_Enmasse_Env.IMAPPassword15

  - name: enmasse.email.imap.16
    host: imap16.example.com
    port: 993
    username: enmasse16@example.com
    password: Zato_Enmasse_Env.IMAPPassword16

  - name: enmasse.email.imap.17
    host: imap17.example.com
    port: 993
    username: enmasse17@example.com
    password: Zato_Enmasse_Env.IMAPPassword17

  - name: enmasse.email.imap.18
    host: imap18.example.com
    port: 993
    username: enmasse18@example.com
    password: Zato_Enmasse_Env.IMAPPassword18

  - name: enmasse.email.imap.19
    host: imap19.example.com
    port: 993
    username: enmasse19@example.com
    password: Zato_Enmasse_Env.IMAPPassword19

  - name: enmasse.email.imap.20
    host: imap20.example.com
    port: 993
    username: enmasse20@example.com
    password: Zato_Enmasse_Env.IMAPPassword20


email_smtp:
  - name: enmasse.email.smtp.1
    host: smtp1.example.com
    port: 587
    username: enmasse1@example.com
    password: Zato_Enmasse_Env.SMTPPassword1

  - name: enmasse.email.smtp.2
    host: smtp2.example.com
    port: 587
    username: enmasse2@example.com
    password: Zato_Enmasse_Env.SMTPPassword2

  - name: enmasse.email.smtp.3
    host: smtp3.example.com
    port: 587
    username: enmasse3@example.com
    password: Zato_Enmasse_Env.SMTPPassword3

  - name: enmasse.email.smtp.4
    host: smtp4.example.com
    port: 587
    username: enmasse4@example.com
    password: Zato_Enmasse_Env.SMTPPassword4

  - name: enmasse.email.smtp.5
    host: smtp5.example.com
    port: 587
    username: enmasse5@example.com
    password: Zato_Enmasse_Env.SMTPPassword5

  - name: enmasse.email.smtp.6
    host: smtp6.example.com
    port: 587
    username: enmasse6@example.com
    password: Zato_Enmasse_Env.SMTPPassword6

  - name: enmasse.email.smtp.7
    host: smtp7.example.com
    port: 587
    username: enmasse7@example.com
    password: Zato_Enmasse_Env.SMTPPassword7

  - name: enmasse.email.smtp.8
    host: smtp8.example.com
    port: 587
    username: enmasse8@example.com
    password: Zato_Enmasse_Env.SMTPPassword8

  - name: enmasse.email.smtp.9
    host: smtp9.example.com
    port: 587
    username: enmasse9@example.com
    password: Zato_Enmasse_Env.SMTPPassword9

  - name: enmasse.email.smtp.10
    host: smtp10.example.com
    port: 587
    username: enmasse10@example.com
    password: Zato_Enmasse_Env.SMTPPassword10

  - name: enmasse.email.smtp.11
    host: smtp11.example.com
    port: 587
    username: enmasse11@example.com
    password: Zato_Enmasse_Env.SMTPPassword11

  - name: enmasse.email.smtp.12
    host: smtp12.example.com
    port: 587
    username: enmasse12@example.com
    password: Zato_Enmasse_Env.SMTPPassword12

  - name: enmasse.email.smtp.13
    host: smtp13.example.com
    port: 587
    username: enmasse13@example.com
    password: Zato_Enmasse_Env.SMTPPassword13

  - name: enmasse.email.smtp.14
    host: smtp14.example.com
    port: 587
    username: enmasse14@example.com
    password: Zato_Enmasse_Env.SMTPPassword14

  - name: enmasse.email.smtp.15
    host: smtp15.example.com
    port: 587
    username: enmasse15@example.com
    password: Zato_Enmasse_Env.SMTPPassword15

  - name: enmasse.email.smtp.16
    host: smtp16.example.com
    port: 587
    username: enmasse16@example.com
    password: Zato_Enmasse_Env.SMTPPassword16

  - name: enmasse.email.smtp.17
    host: smtp17.example.com
    port: 587
    username: enmasse17@example.com
    password: Zato_Enmasse_Env.SMTPPassword17

  - name: enmasse.email.smtp.18
    host: smtp18.example.com
    port: 587
    username: enmasse18@example.com
    password: Zato_Enmasse_Env.SMTPPassword18

  - name: enmasse.email.smtp.19
    host: smtp19.example.com
    port: 587
    username: enmasse19@example.com
    password: Zato_Enmasse_Env.SMTPPassword19

  - name: enmasse.email.smtp.20
    host: smtp20.example.com
    port: 587
    username: enmasse20@example.com
    password: Zato_Enmasse_Env.SMTPPassword20


jira:
  - name: enmasse.jira.1
    address: https://example1.atlassian.net
    username: enmasse1@example.com
    password: Zato_Enmasse_Env.JiraAPIToken1

  - name: enmasse.jira.2
    address: https://example2.atlassian.net
    username: enmasse2@example.com
    password: Zato_Enmasse_Env.JiraAPIToken2

  - name: enmasse.jira.3
    address: https://example3.atlassian.net
    username: enmasse3@example.com
    password: Zato_Enmasse_Env.JiraAPIToken3

  - name: enmasse.jira.4
    address: https://example4.atlassian.net
    username: enmasse4@example.com
    password: Zato_Enmasse_Env.JiraAPIToken4

  - name: enmasse.jira.5
    address: https://example5.atlassian.net
    username: enmasse5@example.com
    password: Zato_Enmasse_Env.JiraAPIToken5

  - name: enmasse.jira.6
    address: https://example6.atlassian.net
    username: enmasse6@example.com
    password: Zato_Enmasse_Env.JiraAPIToken6

  - name: enmasse.jira.7
    address: https://example7.atlassian.net
    username: enmasse7@example.com
    password: Zato_Enmasse_Env.JiraAPIToken7

  - name: enmasse.jira.8
    address: https://example8.atlassian.net
    username: enmasse8@example.com
    password: Zato_Enmasse_Env.JiraAPIToken8

  - name: enmasse.jira.9
    address: https://example9.atlassian.net
    username: enmasse9@example.com
    password: Zato_Enmasse_Env.JiraAPIToken9

  - name: enmasse.jira.10
    address: https://example10.atlassian.net
    username: enmasse10@example.com
    password: Zato_Enmasse_Env.JiraAPIToken10

  - name: enmasse.jira.11
    address: https://example11.atlassian.net
    username: enmasse11@example.com
    password: Zato_Enmasse_Env.JiraAPIToken11

  - name: enmasse.jira.12
    address: https://example12.atlassian.net
    username: enmasse12@example.com
    password: Zato_Enmasse_Env.JiraAPIToken12

  - name: enmasse.jira.13
    address: https://example13.atlassian.net
    username: enmasse13@example.com
    password: Zato_Enmasse_Env.JiraAPIToken13

  - name: enmasse.jira.14
    address: https://example14.atlassian.net
    username: enmasse14@example.com
    password: Zato_Enmasse_Env.JiraAPIToken14

  - name: enmasse.jira.15
    address: https://example15.atlassian.net
    username: enmasse15@example.com
    password: Zato_Enmasse_Env.JiraAPIToken15

  - name: enmasse.jira.16
    address: https://example16.atlassian.net
    username: enmasse16@example.com
    password: Zato_Enmasse_Env.JiraAPIToken16

  - name: enmasse.jira.17
    address: https://example17.atlassian.net
    username: enmasse17@example.com
    password: Zato_Enmasse_Env.JiraAPIToken17

  - name: enmasse.jira.18
    address: https://example18.atlassian.net
    username: enmasse18@example.com
    password: Zato_Enmasse_Env.JiraAPIToken18

  - name: enmasse.jira.19
    address: https://example19.atlassian.net
    username: enmasse19@example.com
    password: Zato_Enmasse_Env.JiraAPIToken19

  - name: enmasse.jira.20
    address: https://example20.atlassian.net
    username: enmasse20@example.com
    password: Zato_Enmasse_Env.JiraAPIToken20


odoo:
  - name: enmasse.odoo.1
    host: odoo1.example.com
    port: 8069
    user: admin1
    password: Zato_Enmasse_Env.OdooPassword1
    database: enmasse_db1

  - name: enmasse.odoo.2
    host: odoo2.example.com
    port: 8069
    user: admin2
    password: Zato_Enmasse_Env.OdooPassword2
    database: enmasse_db2

  - name: enmasse.odoo.3
    host: odoo3.example.com
    port: 8069
    user: admin3
    password: Zato_Enmasse_Env.OdooPassword3
    database: enmasse_db3

  - name: enmasse.odoo.4
    host: odoo4.example.com
    port: 8069
    user: admin4
    password: Zato_Enmasse_Env.OdooPassword4
    database: enmasse_db4

  - name: enmasse.odoo.5
    host: odoo5.example.com
    port: 8069
    user: admin5
    password: Zato_Enmasse_Env.OdooPassword5
    database: enmasse_db5

  - name: enmasse.odoo.6
    host: odoo6.example.com
    port: 8069
    user: admin6
    password: Zato_Enmasse_Env.OdooPassword6
    database: enmasse_db6

  - name: enmasse.odoo.7
    host: odoo7.example.com
    port: 8069
    user: admin7
    password: Zato_Enmasse_Env.OdooPassword7
    database: enmasse_db7

  - name: enmasse.odoo.8
    host: odoo8.example.com
    port: 8069
    user: admin8
    password: Zato_Enmasse_Env.OdooPassword8
    database: enmasse_db8

  - name: enmasse.odoo.9
    host: odoo9.example.com
    port: 8069
    user: admin9
    password: Zato_Enmasse_Env.OdooPassword9
    database: enmasse_db9

  - name: enmasse.odoo.10
    host: odoo10.example.com
    port: 8069
    user: admin10
    password: Zato_Enmasse_Env.OdooPassword10
    database: enmasse_db10

  - name: enmasse.odoo.11
    host: odoo11.example.com
    port: 8069
    user: admin11
    password: Zato_Enmasse_Env.OdooPassword11
    database: enmasse_db11

  - name: enmasse.odoo.12
    host: odoo12.example.com
    port: 8069
    user: admin12
    password: Zato_Enmasse_Env.OdooPassword12
    database: enmasse_db12

  - name: enmasse.odoo.13
    host: odoo13.example.com
    port: 8069
    user: admin13
    password: Zato_Enmasse_Env.OdooPassword13
    database: enmasse_db13

  - name: enmasse.odoo.14
    host: odoo14.example.com
    port: 8069
    user: admin14
    password: Zato_Enmasse_Env.OdooPassword14
    database: enmasse_db14

  - name: enmasse.odoo.15
    host: odoo15.example.com
    port: 8069
    user: admin15
    password: Zato_Enmasse_Env.OdooPassword15
    database: enmasse_db15

  - name: enmasse.odoo.16
    host: odoo16.example.com
    port: 8069
    user: admin16
    password: Zato_Enmasse_Env.OdooPassword16
    database: enmasse_db16

  - name: enmasse.odoo.17
    host: odoo17.example.com
    port: 8069
    user: admin17
    password: Zato_Enmasse_Env.OdooPassword17
    database: enmasse_db17

  - name: enmasse.odoo.18
    host: odoo18.example.com
    port: 8069
    user: admin18
    password: Zato_Enmasse_Env.OdooPassword18
    database: enmasse_db18

  - name: enmasse.odoo.19
    host: odoo19.example.com
    port: 8069
    user: admin19
    password: Zato_Enmasse_Env.OdooPassword19
    database: enmasse_db19

  - name: enmasse.odoo.20
    host: odoo20.example.com
    port: 8069
    user: admin20
    password: Zato_Enmasse_Env.OdooPassword20
    database: enmasse_db20


elastic_search:
  - name: enmasse.elastic.1
    is_active: true
    hosts: http://elasticsearch1:9200
    timeout: 60
    body_as: json

  - name: enmasse.elastic.2
    is_active: true
    hosts: http://elasticsearch2:9200
    timeout: 61
    body_as: json

  - name: enmasse.elastic.3
    is_active: true
    hosts: http://elasticsearch3:9200
    timeout: 62
    body_as: json

  - name: enmasse.elastic.4
    is_active: true
    hosts: http://elasticsearch4:9200
    timeout: 63
    body_as: json

  - name: enmasse.elastic.5
    is_active: true
    hosts: http://elasticsearch5:9200
    timeout: 64
    body_as: json

  - name: enmasse.elastic.6
    is_active: true
    hosts: http://elasticsearch6:9200
    timeout: 65
    body_as: json

  - name: enmasse.elastic.7
    is_active: true
    hosts: http://elasticsearch7:9200
    timeout: 66
    body_as: json

  - name: enmasse.elastic.8
    is_active: true
    hosts: http://elasticsearch8:9200
    timeout: 67
    body_as: json

  - name: enmasse.elastic.9
    is_active: true
    hosts: http://elasticsearch9:9200
    timeout: 68
    body_as: json

  - name: enmasse.elastic.10
    is_active: true
    hosts: http://elasticsearch10:9200
    timeout: 69
    body_as: json

  - name: enmasse.elastic.11
    is_active: true
    hosts: http://elasticsearch11:9200
    timeout: 70
    body_as: json

  - name: enmasse.elastic.12
    is_active: true
    hosts: http://elasticsearch12:9200
    timeout: 71
    body_as: json

  - name: enmasse.elastic.13
    is_active: true
    hosts: http://elasticsearch13:9200
    timeout: 72
    body_as: json

  - name: enmasse.elastic.14
    is_active: true
    hosts: http://elasticsearch14:9200
    timeout: 73
    body_as: json

  - name: enmasse.elastic.15
    is_active: true
    hosts: http://elasticsearch15:9200
    timeout: 74
    body_as: json

  - name: enmasse.elastic.16
    is_active: true
    hosts: http://elasticsearch16:9200
    timeout: 75
    body_as: json

  - name: enmasse.elastic.17
    is_active: true
    hosts: http://elasticsearch17:9200
    timeout: 76
    body_as: json

  - name: enmasse.elastic.18
    is_active: true
    hosts: http://elasticsearch18:9200
    timeout: 77
    body_as: json

  - name: enmasse.elastic.19
    is_active: true
    hosts: http://elasticsearch19:9200
    timeout: 78
    body_as: json

  - name: enmasse.elastic.20
    is_active: true
    hosts: http://elasticsearch20:9200
    timeout: 79
    body_as: json
"""

# ################################################################################################################################
# ################################################################################################################################

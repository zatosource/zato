# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_sms.africas_talking import AfricasTalkingSimulator
from live_sms.infobip import InfobipSimulator
from live_sms.twilio import TwilioSimulator
from live_sms.vonage import VonageSimulator
from zato.common.api import SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sms.base import SMSSimulator
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The one account each simulator serves
Twilio_Account_SID = 'AC' + '0' * 30 + 'a1'
Twilio_Auth_Token = 'twilio-auth-token-for-tests'

Vonage_API_Key = 'a1b2c3d4'
Vonage_API_Secret = 'vonage-api-secret-for-tests'
Vonage_Signature_Secret = 'vonage-signature-secret-for-tests'

Infobip_API_Key = 'infobip-api-key-for-tests'

Africas_Talking_Username = 'sandbox'
Africas_Talking_API_Key = 'africas-talking-api-key-for-tests'

# Infobip authenticates with its API key alone, the username is for the connection's record only
Infobip_Username = 'infobip-account'

# The environment variables an enmasse template reads each simulator's address from
Host_Variables = {
    SMS.Provider.Twilio: 'Zato_Test_SMS_Twilio_Host',
    SMS.Provider.Vonage: 'Zato_Test_SMS_Vonage_Host',
    SMS.Provider.Infobip: 'Zato_Test_SMS_Infobip_Host',
    SMS.Provider.Africas_Talking: 'Zato_Test_SMS_Africas_Talking_Host',
}

# ################################################################################################################################
# ################################################################################################################################

class SimulatorSuite:
    """ The four provider simulators of one test session, started and stopped together.
    """

    def __init__(self) -> 'None':
        self.twilio = TwilioSimulator(Twilio_Account_SID, Twilio_Auth_Token)
        self.vonage = VonageSimulator(Vonage_API_Key, Vonage_API_Secret, Vonage_Signature_Secret)
        self.infobip = InfobipSimulator(Infobip_Username, Infobip_API_Key)
        self.africas_talking = AfricasTalkingSimulator(Africas_Talking_Username, Africas_Talking_API_Key)

        self.all:'list[SMSSimulator]' = [self.twilio, self.vonage, self.infobip, self.africas_talking]

# ################################################################################################################################

    def start(self) -> 'None':
        for item in self.all:
            item.start()
            print(f'[SMS-SIM] {item.provider} at {item.url}')

# ################################################################################################################################

    def stop(self) -> 'None':
        for item in self.all:
            item.stop()

# ################################################################################################################################

    def reset(self) -> 'None':
        for item in self.all:
            item.reset()

# ################################################################################################################################

    def by_provider(self, provider:'str') -> 'SMSSimulator':
        for item in self.all:
            if item.provider == provider:
                out = item
                break
        else:
            raise Exception(f'No simulator for provider `{provider}`')

        return out

# ################################################################################################################################

    def host_environment(self) -> 'strstrdict':
        """ The variables that point each connection of an enmasse template at its simulator.
        """
        out:'strstrdict' = {}

        for item in self.all:
            out[Host_Variables[item.provider]] = item.url

        return out

# ################################################################################################################################
# ################################################################################################################################

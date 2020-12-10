import requests

CD_MSG_TITLE = 'Code Defender has detected a new incident'

class PerimeterXManagerException(Exception):
    """ General Exception for PerimeterX manager """
    pass

class PerimeterXManager(object):

    def __init__(self, slack_channel=None, slack_api_key=None, connector_type=None, offset_in_seconds=0):
        self.slack_channel = slack_channel
        self.slack_api_key = slack_api_key
        self.slack_offset = self.convert_offset(offset_in_seconds)
        self.connector_type = connector_type
        self.slack_cursor = ''
        self.paginated = False
        self.messages = []


    """ This is a bit of a hack but it works for now """
    def convert_offset(self, seconds):
        if(seconds == 0):
            return seconds
        return float(((seconds*1000)+1)/1000000)


    def get_slack_channel_id(self):
        response = requests.get(
            'https://slack.com/api/conversations.list',
            headers={'Authorization': 'Bearer ' + self.slack_api_key}
        )
        # curl -H 'Authorization: Bearer slack_api_key' https://slack.com/api/conversations.list
        # foreach channels if name == slack_channel, then return id
        if response.status_code != 200:
            print('Failure')
            return False

        json_response = response.json()

        # check to make sure we've got a channels array
        if 'channels' not in json_response:
            print('No Channels Identified')
            return False

        # check to make sure the channels is a list
        if type(json_response['channels']) != list:
            print('Not a valid list of channels')
            return False

        # step through the channels looking for the one we want
        for x in json_response['channels']:
            # if this is the channel we want then return the id
            if x['name'] == self.slack_channel:
                return x['id']

        return False


    def f(self, x):
        return {
            'slack': self.get_slack_messages()
        }.get(x, False)


    def getItemFromList(self, list, searchItem, searchValue, returnValue):
        for x in list:
            if x[searchItem] == searchValue:
                return x[returnValue]
        return False


    def before(self, value, a):
        # Find first part and return slice before it.
        pos_a = value.find(a)
        if pos_a == -1: return value
        return value[0:pos_a]


    def formatSlackMsg(self, msg):
        return {
            'type': 'slack',
            'ts': msg['ts'],
            'text': self.before(msg['attachments'][0]['text'], '\n'),
            'fullText': msg['attachments'][0]['text'],
            'title': msg['attachments'][0]['title'],
            'severity': self.getItemFromList(msg['attachments'][0]['fields'], 'title', 'Risk Level', 'value'),
            'script': self.getItemFromList(msg['attachments'][0]['fields'], 'title', 'Script', 'value'),
            'domain': self.getItemFromList(msg['attachments'][0]['fields'], 'title', 'Host Domain', 'value'),
            'deepLink': self.getItemFromList(msg['attachments'][0]['actions'], 'text', 'View in Console', 'url')
        }


    def get_slack_messages(self):
        channelId = self.get_slack_channel_id()

        if channelId == False:
            print('No Channel ID Given for get_slack_messages')
            return False

        response = requests.get(
            'https://slack.com/api/conversations.history',
            params={'channel': channelId, 'limit': 100, 'cursor': self.slack_cursor, 'oldest': self.slack_offset},
            headers={'Authorization': 'Bearer ' + self.slack_api_key}
        )

        if response.status_code != 200:
            print('Failure')
            return False

        json_response = response.json()

        if json_response['has_more'] == True:
            self.pagination = 1
            self.slack_cursor = json_response['response_metadata']['next_cursor']
        else:
            self.pagination = 0
            self.slack_cursor = ''

        if 'messages' not in json_response:
            return False

        # Check to make sure we got some messages returned
        if json_response['messages'] == False:
            return False

        # Check to make sure there's messages in the list
        if len(json_response['messages']) < 1:
            print('Empty messages')
            return False

        # walk through our retrieved messages to find CD related entries
        for x in json_response['messages']:
            # Check for a Code Defender specific message
            if x['type'] == 'message' and 'attachments' in x and x['attachments'][0]['title'] == CD_MSG_TITLE:
                self.messages.append(self.formatSlackMsg(x))

        if self.pagination == 1:
            self.get_slack_messages()

        return self.messages


    def get_cd_alerts(self, integrationType):
        # Execute the desired message retrieval
        return self.f(integrationType)


    def get_connector_type(self):
        return self.connector_type
        
        
    def auth(self):
        response = requests.post(
            'https://slack.com/api/auth.test',
            headers={'Authorization': 'Bearer ' + self.slack_api_key}
        )
        if response.status_code != 200:
            print('Failure Code getting slack channel ID')
            return False

        json_response = response.json()
        if 'ok' in json_response and json_response['ok'] == True:
            print('Valid Authentication')
            return True

        if 'ok' in json_response and json_response['ok'] == False:
            print('Authentication Failed')
            return False

        return False

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from PerimeterXManager import PerimeterXManager,PerimeterXManagerException

INTEGRATION_NAME = "PerimeterX"

SCRIPT_NAME = "Ping"

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info(u"----------------- Main - Param Init -----------------")

    param_slack_api_key = siemplify.extract_configuration_param(INTEGRATION_NAME,"Slack API Key")
    param_slack_channel = siemplify.extract_configuration_param(INTEGRATION_NAME,"Slack Channel")

    siemplify.LOGGER.info(u"----------------- Main - Started -----------------")

    try:
        pX = PerimeterXManager(slack_channel=param_slack_channel, slack_api_key=param_slack_api_key, connector_type='slack')
        pX.auth()
        output_message = u'Connection to Slack established successfully.'
        result = 'true'
        status = EXECUTION_STATE_COMPLETED
        siemplify.LOGGER.info(u'Script Name: {} | {}'.format(SCRIPT_NAME, output_message))
    except PerimeterXManagerException as e:
        output_message = u'An error occurred when trying to connect to the API: {}'.format(e)
        result = 'false'
        status = EXECUTION_STATE_FAILED
        siemplify.LOGGER.error(u'Script Name: {} | {}'.format(SCRIPT_NAME, output_message))
        siemplify.LOGGER.exception(e)

    siemplify.LOGGER.info(u"----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(u'Status: {}'.format(status))
    siemplify.LOGGER.info(u'Result: {}'.format(result))
    siemplify.LOGGER.info(u'Output Message: {}'.format(output_message))

    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()

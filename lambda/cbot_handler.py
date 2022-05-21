import coinmarketcapapi
import boto3

ssm = boto3.client("ssm")


def get_slots(intent_request):
    return intent_request["sessionState"]["intent"]["slots"]


def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]["value"]["interpretedValue"]
    else:
        return None


def get_session_attributes(intent_request):
    sessionState = intent_request["sessionState"]
    if "sessionAttributes" in sessionState:
        return sessionState["sessionAttributes"]

    return {}


def elicit_intent(intent_request, session_attributes, message):
    return {
        "sessionState": {
            "dialogAction": {"type": "ElicitIntent"},
            "sessionAttributes": session_attributes,
        },
        "messages": [message] if message != None else None,
        "requestAttributes": intent_request["requestAttributes"]
        if "requestAttributes" in intent_request
        else None,
    }


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request["sessionState"]["intent"]["state"] = fulfillment_state
    return {
        "sessionState": {
            "sessionAttributes": session_attributes,
            "dialogAction": {"type": "Close"},
            "intent": intent_request["sessionState"]["intent"],
        },
        "messages": [message],
        "sessionId": intent_request["sessionId"],
        "requestAttributes": intent_request["requestAttributes"]
        if "requestAttributes" in intent_request
        else None,
    }


def search_crypto(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    crypto = get_slot(intent_request, "crypto")
    cmc_api_key = ssm.get_parameter(Name="/dev/crypto-bot/COIN_MARKETCAP_API_KEY")
    cmc = coinmarketcapapi.CoinMarketCapAPI(cmc_api_key["Parameter"]["Value"])
    r = cmc.cryptocurrency_info(symbol=crypto.upper())
    text = repr(r.data[crypto]["description"])
    message = {"contentType": "PlainText", "content": text}
    fulfillment_state = "Fulfilled"
    return close(intent_request, session_attributes, fulfillment_state, message)

    
def dispatch(intent_request):
    intent_name = intent_request["sessionState"]["intent"]["name"]
    response = None
    return search_crypto(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    response = dispatch(event)
    return response
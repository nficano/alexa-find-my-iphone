import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
site_packages = os.path.join(cwd, 'site-packages')
sys.path.append(site_packages)

from pyicloud import PyiCloudService  # noqa


def lambda_handler(event, context):
    request_type = event['request']['type']
    if request_type == 'LaunchRequest':
        return on_launch()
    elif request_type == 'IntentRequest':
        return on_intent(event['request'])


def on_launch():
    speech_output = (
        'Welcome to the icloud skill, to start, say \'find my iphone\''
    )
    speechlet_response = build_speechlet_response(
        title='Welcome',
        output=speech_output,
        reprompt_text=speech_output,
        should_end_session=False,
    )
    return build_response(
        session_attributes={},
        speechlet_response=speechlet_response,
    )


def on_intent(request):
    api = PyiCloudService(os.environ['APPLE_ID'], os.environ['PASSWORD'])
    for iphone in get_iphones(api):
        iphone.play_sound()

    speechlet_response = build_speechlet_response(
        title=request['intent']['name'],
        output='Ok, you should be able to hear it beeping now.',
        reprompt_text='Ok, you should be able to hear it beeping now.',
        should_end_session=True,
    )
    return build_response(
        session_attributes={},
        speechlet_response=speechlet_response,
    )


def get_iphones(api):
    for device in api.devices:
        data = device.data
        if all([
            data['deviceClass'] == 'iPhone',
            data['isLocating'] is True,
        ]):
            yield device


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output,
        },
        'card': {
            'type': 'Simple',
            'title': f'SessionSpeechlet - {title}',
            'content': f'SessionSpeechlet - {output}',
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text,
            },
        },
        'shouldEndSession': should_end_session,
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.2',
        'sessionAttributes': session_attributes,
        'response': speechlet_response,
    }

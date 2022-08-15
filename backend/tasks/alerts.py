import json
import requests

from core.config import settings
from tasks.utils import is_url


def send_mm_alert(check):
    hook = settings.MATTERMOST_HOOK
    if is_url(hook):
        msg = """
    #### :x: Check "{check_name}" failed.
    **Url**: {url} 
        """.format(
            check_name=check.name,
            url=settings.SERVER_HOST + f'/#/{"custom_checks" if check.check_class == "customcheck" else "checks"}/?filter={{"id":{check.id}}}'
        )
        requests.post(hook, data=json.dumps({'text': msg}), headers={'Content-Type': 'application/json'})

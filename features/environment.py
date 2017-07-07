import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pulp_behave.tag_selector_matcher import SelectorTagMatcher
from pulp_smash import api, config
from pulp_smash.constants import ORPHANS_PATH

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def before_all(context):
    context.cfg = config.get_config()
    context.matcher = SelectorTagMatcher(context.cfg)


def before_feature(context, feature):
    if context.matcher.should_exclude_with(feature.tags):
        if context.matcher.exclude_reason:
            feature.skip(context.matcher.exclude_reason)
        else:
            feature.skip()


def before_scenario(context, scenario):
    context.resources = set()
    if context.matcher.should_exclude_with(scenario.effective_tags):
        if context.matcher.exclude_reason:
            scenario.skip(context.matcher.exclude_reason)
        else:
            scenario.skip()


def after_scenario(context, scenario):
    """Delete all resources"""
    client = api.Client(context.cfg)
    for resource in context.resources:
        client.delete(resource)
    client.delete(ORPHANS_PATH)

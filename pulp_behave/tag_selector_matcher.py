import operator

from behave.tag_matcher import ActiveTagMatcher

from packaging.version import Version
from pulp_smash import selectors


class SelectorTagMatcher(ActiveTagMatcher):

    tag_schema = r"^(?P<prefix>%s)\.with_(?P<category>\w+(\.\w+)*[<>]?)%s(?P<value>.*)$"

    def __init__(self, cfg, *args, **kwargs):
        self.category_handlers = {
            "testable": self.testable_handler,
            "version": self.version_handler,
            "version>": self.version_handler,
            "version<": self.version_handler,
            "not_present": self.not_present_handler,
        }
        self.cfg = cfg

        super().__init__(None, *args, **kwargs)

    def should_exclude_with(self, tags):
        self.exclude_reason = None
        super().should_exclude_with(tags)

    def is_tag_group_enabled(self, group_category, group_tag_pairs):
        """

        Gherkin:

            @only.with_testable=2650
            @only.with_testable=2250
            Scenario: Test something
            ...

        :return: True, if all tags in tag-group are enabled.
        """
        if not group_tag_pairs:
            return True

        handler = self.category_handlers.get(group_category, None)
        if handler is None:  # Ignore unknown categories
            return True

        tags_enabled = []
        for category_tag, tag_match in group_tag_pairs:
            tag_prefix = tag_match.group("prefix")
            category = tag_match.group("category")
            tag_value = tag_match.group("value")

            tags_enabled.append(handler(tag_prefix, category, tag_value))

        return all(tags_enabled)

    def testable_handler(self, prefix, category, value):
        if prefix.startswith('not'):
            test_func = selectors.bug_is_untestable
        else:
            test_func = selectors.bug_is_testable

        self.exclude_reason = 'https://pulp.plan.io/issues/%s' % value
        return test_func(int(value), self.cfg.version)

    def version_handler(self, prefix, category, value):
        test_func = operator.nq if prefix.startswith('not') else operator.eq

        if category.endswith("<"):
            out = self.cfg.version <= Version(value)
        elif category.endswith(">"):
            out = self.cfg.version >= Version(value)
        else:
            out = self.cfg.version == Version(value)

        return test_func(True, out)

    def not_present_handler(self, prefix, category, value):
        """Check for special bugs."""

        out = None
        if value == "2620":
            out = not (self.cfg.version >= Version('2.12') and
                       selectors.bug_is_untestable(2620, self.cfg.version))
        else:
            raise NotImplementedError("Check for bug %s is not implemented." % value)

        if out:
            self.exclude_reason = 'https://pulp.plan.io/issues/%s' % value
            test_func = operator.nq if prefix.startswith('not') else operator.eq
            return test_func(True, out)
        else:
            return True

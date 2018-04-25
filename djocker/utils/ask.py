from collections import OrderedDict

from .colors import Colors, color


class ValidationError(Exception):
    pass


def ask(question, default=None, choices=None, validator=None, newline=True):  # noqa: C901
    options = {'question': question,
               'default': '' if not default else '[{}]'.format(color(default, Colors.BOLD))}

    choices_has_mapping = isinstance(choices, dict) or isinstance(choices, OrderedDict)
    if choices_has_mapping:
        index_mapping = dict(enumerate(choices.keys()))
        choices = list(choices.values())

    if choices:
        choices_string = '\n'
        if default:
            default_index = str(choices.index(default))
            options['default'] = '[{} ({})]'.format(default, color(default_index, Colors.BOLD))
        for index, choice in enumerate(choices):
            choices_string += '{} : {}\n'.format(color(index, Colors.BOLD), choice)

    options['choices'] = '' if not choices else choices_string

    q = '{question}'
    if options.get('choices') or options.get('default'):
        q += ' {choices}{default}'
    q += '> '
    q = q.format(**options)

    if newline:
        print("")

    response_given = False
    response = None

    while not response_given or (not response and not default):
        if not response_given:
            response = input(q)
        else:
            response = input('> ')
        response_given = True

    if default and not response:
        if choices:
            response = default_index
        else:
            response = default

    if choices and not choices_has_mapping:
        try:
            response_value = choices[int(response)]
        except ValueError:
            return ask(question, default, choices, validator)
    elif choices_has_mapping:
        response_value = index_mapping[int(response)]
    else:
        response_value = response

    if validator:
        try:
            validator.validate(response_value)
        except ValidationError as e:
            print(color(str(e), Colors.FAIL))
            return ask(question, default, choices, validator)

    return response_value

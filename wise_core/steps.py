"""
Helpers for `wise_core/components/_steps.html`, the design system's Steps.

    from wise_core.steps import wizard_steps

    context['steps'] = wizard_steps([_('Identity'), _('Contact'), _('Document')], current=1)

Steps before `current` (a zero-based index) are done, the one at `current`
is current, the rest are upcoming. Pass `urls` (one per step, or None) to
let a visitor go back to a finished step.
"""


def wizard_steps(labels, current, urls=None, keys=None):
    """The list of dicts `_steps.html` renders, one per label."""
    steps = []
    for index, label in enumerate(labels):
        if index < current:
            state = 'done'
        elif index == current:
            state = 'current'
        else:
            state = 'upcoming'
        steps.append({
            'label': label,
            'state': state,
            'number': index + 1,
            'key': keys[index] if keys else index + 1,
            'url': urls[index] if urls else None,
        })
    return steps

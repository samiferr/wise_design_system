# Appearances: Lumen and Tangerine

An **appearance** is a whole design language: typeface, colors, shape, borders, control sizes and
focus style together. wise_core ships two, and a visitor can switch between them at any time:

| Appearance | Value | What it looks like |
|---|---|---|
| **Lumen** (default) | `lumen` | Calm and neutral, in the Spectrum tradition: Source Sans 3, one accent hue, pill buttons, 8px fields, a gray page with white layers. Everything in `tokens.css`. |
| **Tangerine** | `tangerine` | Square and dense, built from Canonical's Vanilla framework: Ubuntu Sans, 1.5px borders, 37px controls with no rounding, fields with only a bottom border, a green main action, link-blue "on" controls, a thin `h2`, and a 3px focus outline drawn inside the edge. `css/appearances/tangerine.css`. |

Tangerine's values come from the [Tangerine design system](https://claude.ai/artifact/APTcw3L1RY7xkfiwdsqjnR)
(its `tokens.json`, README and *How to customize Tangerine* page).

**Templates don't change.** An appearance re-points the system tokens that every component reads
(`--color-*`, `--text-*`, `--corner-radius-*`, `--shadow-*`, `--control-height-*`, `--focus-ring-*`)
and adds a few shape overrides for the things tokens can't express. `.btn btn-primary`, `.card`,
`.form-field` and `.data-table` keep their class names, so a page written for Lumen renders in
Tangerine with no edits.

- [How it works](#how-it-works)
- [Turn it on in your project](#turn-it-on-in-your-project)
- [Let people switch](#let-people-switch)
- [Read the appearance in Python](#read-the-appearance-in-python)
- [Save the choice on the user](#save-the-choice-on-the-user)
- [Settings reference](#settings-reference)
- [How it combines with the other axes](#how-it-combines-with-the-other-axes)
- [Add your own appearance](#add-your-own-appearance)
- [Caching and security notes](#caching-and-security-notes)

## How it works

```
 request ──▶ AppearanceMiddleware ──▶ request.appearance = "tangerine"
              (query ▸ cookie ▸ session ▸ resolver ▸ default)
                         │
                         ▼
             appearance context processor ──▶ {{ wise_appearance }}, {{ wise_appearances }}
                         │
                         ▼
   base.html:  <html data-appearance="tangerine">     ◀── first paint is already right
                         │
                         ▼
   tailwind.css:  :root[data-appearance="tangerine"] { --color-accent-background: #0066cc; ... }
```

1. **The server decides.** `wise_core.middleware.AppearanceMiddleware` works out the appearance for
   each request and stores it on `request.appearance`. Sources, first match wins:
   1. a `?appearance=tangerine` query parameter (and the response then sets the cookie, so the
      rest of the visit stays in that appearance);
   2. the `wise_appearance` cookie;
   3. the session (`request.session['wise_appearance']`);
   4. your `WISE_APPEARANCE_RESOLVER(request)` hook, for example a user-profile field;
   5. `WISE_DEFAULT_APPEARANCE`.

   Unknown values are ignored at every step, so a stale cookie falls through to the default.
2. **The template renders it.** `wise_core/base.html` writes it on `<html data-appearance="…">`.
   Because this happens on the server, the page never flashes in the wrong appearance. The theme,
   palette, radius and shadow axes are different: they live in `localStorage` and are applied by a
   small inline script.
3. **The stylesheet reacts.** `tokens.css` imports `appearances/tangerine.css` as its last line.
   That file redefines the tokens under `:root[data-appearance="tangerine"]` (and
   `…[data-theme="dark"]`), loads Ubuntu Sans with `@font-face` (only downloaded when Tangerine is
   in use), and restyles fields, buttons, tabs and headings. Both appearances ship in the one
   `tailwind.css`, so there's no second stylesheet to load and no rebuild when someone switches.
4. **Switching is instant.** In the browser, `wiseSetAppearance('tangerine')` flips the attribute,
   writes the cookie for the next request, and fires a `wise:appearancechange` event (live charts
   redraw on their own). Without JavaScript, a plain form POSTs to `wise_set_appearance`, Django's
   `set_language` pattern applied to design.

## Turn it on in your project

Rebuild the stylesheet first (`npm run build:css`) so your `tailwind.css` contains the Tangerine
rules. `tokens.css` imports them, so there's nothing to add to your `input.css`.

**1. Middleware.** Put it after `SessionMiddleware` (it reads the session when one exists) and before
anything that renders:

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'wise_core.middleware.AppearanceMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

**2. Context processor.** This gives templates `wise_appearance`, `wise_appearances`,
`wise_appearance_default` and `wise_appearance_cookie`, and it's what makes the settings panel show
the **Appearance** buttons:

```python
TEMPLATES = [{
    # ...
    'OPTIONS': {'context_processors': [
        # ...
        'django.template.context_processors.request',
        'wise_core.context_processors.nav',
        'wise_core.context_processors.appearance',
    ]},
}]
```

**3. URLs** (for the no-JavaScript form and `fetch()` switching):

```python
# urls.py
urlpatterns = [
    # ...
    path('wise/', include('wise_core.urls')),   # -> {% url 'wise_set_appearance' %}
]
```

**4. Optional settings.** The defaults are fine; list them only to change something:

```python
WISE_APPEARANCES = [('lumen', 'Lumen'), ('tangerine', 'Tangerine')]
WISE_DEFAULT_APPEARANCE = 'lumen'
```

That's all. If your pages extend `wise_core/base.html`, the `<html>` attribute, the switcher in the
design settings panel and the bootstrap config are already in place. If you have your own base
template, add the attribute and the config yourself:

```django
<html lang="{{ LANGUAGE_CODE }}" data-appearance="{{ wise_appearance }}">
<head>
  <script>
    window.WISE_APPEARANCE = {
      cookie: "{{ wise_appearance_cookie|escapejs }}",
      fallback: "{{ wise_appearance_default|escapejs }}"
    };
  </script>
  <link rel="stylesheet" href="{% static 'wise_core/css/tailwind.css' %}">
```

To **force one appearance** for the whole site and offer no choice, set
`WISE_APPEARANCES = [('tangerine', 'Tangerine')]`. With a single choice, the settings panel hides its
Appearance group.

## Let people switch

Use any one of these, or combine them.

### The design settings panel (zero code)

`wise_core/components/_settings_panel.html`, opened by the gear icon in `base.html`, has an
**Appearance** group with one button per entry in `WISE_APPEARANCES` whenever the `appearance`
context processor is installed and there's more than one choice. Under Tangerine it hides the **Accent color** and **Rounding** groups
(those are Lumen-only axes) and shows a one-line note explaining why.

### A JavaScript button (no reload)

```html
<button type="button" class="btn btn-secondary"
        data-wise-pref="appearance" data-wise-value="tangerine"
        onclick="wiseSetAppearance('tangerine')">Tangerine</button>
```

`data-wise-pref` / `data-wise-value` are optional. With them, `common.js` keeps `aria-pressed` on the
button in sync with the current appearance. `wiseSetAppearance('')` clears the choice and returns to
`WISE_DEFAULT_APPEARANCE`. Listen for changes with:

```js
document.addEventListener('wise:appearancechange', e => console.log(e.detail.appearance))
```

### A form (works without JavaScript)

```django
<form action="{% url 'wise_set_appearance' %}" method="post" class="flex gap-2">
    {% csrf_token %}
    <input type="hidden" name="next" value="{{ request.get_full_path }}">
    {% for choice in wise_appearances %}
        <button class="btn btn-secondary" name="appearance" value="{{ choice.value }}"
                aria-pressed="{{ choice.selected|yesno:'true,false' }}">{{ choice.label }}</button>
    {% endfor %}
</form>
```

The view checks the value (an unknown one returns 400) and accepts POST only (405 otherwise). It
sets the cookie, plus the session when one exists, sends `appearance_changed`, and redirects to
`next`. If `next` is missing or points to another host, it falls back to the referrer, then `/`.

### `fetch()` (the server is told without a page load)

```js
fetch('/wise/appearance/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
    body: new URLSearchParams({appearance: 'tangerine'}),
}).then(() => wiseSetAppearance('tangerine'))
```

With `Accept: application/json` or `X-Requested-With: XMLHttpRequest`, the view answers
`204 No Content` instead of redirecting. Use this when you also want the `appearance_changed`
signal to fire, for example to save the choice on the user.

### A link

`?appearance=tangerine` on any URL switches the appearance and remembers it. It's handy for sharing a
screenshot link or a QA checklist. Set `WISE_APPEARANCE_QUERY_PARAM = None` to turn it off.

## Read the appearance in Python

```python
def report(request):
    if request.appearance == 'tangerine':
        ...
```

In templates, use `{{ wise_appearance }}`. To read it without the middleware (in a management command
that renders a template, for example), call `wise_core.appearance.get_appearance_from_request(request)`.

## Save the choice on the user

Cookies are per browser. To make a signed-in user's choice follow them to another device, store it
on the user and plug both ends in:

```python
# myapp/appearance.py
from django.dispatch import receiver
from wise_core.appearance import appearance_changed


def appearance_for(request):
    """WISE_APPEARANCE_RESOLVER: consulted when there is no cookie or session value."""
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        return user.profile.appearance or None
    return None


@receiver(appearance_changed)
def save_appearance(sender, request, appearance, **kwargs):
    if request.user.is_authenticated:
        request.user.profile.appearance = appearance
        request.user.profile.save(update_fields=['appearance'])
```

```python
# settings.py
WISE_APPEARANCE_RESOLVER = 'myapp.appearance.appearance_for'
```

Import `myapp.appearance` in your `AppConfig.ready()` so the receiver connects. To have the
JavaScript-only switch (the settings panel) also save to the user, make the switch through `fetch()`
as shown above. `wiseSetAppearance()` on its own writes only the cookie.

The resolver comes after the cookie on purpose: a choice made on this browser wins over the stored
default until the user changes it.

## Settings reference

| Setting | Default | Meaning |
|---|---|---|
| `WISE_APPEARANCES` | `[('lumen', 'Lumen'), ('tangerine', 'Tangerine')]` | The `(value, label)` choices, in display order. Values must have CSS (`lumen` needs none). |
| `WISE_DEFAULT_APPEARANCE` | `'lumen'` | Used when nothing else applies. If it isn't in `WISE_APPEARANCES`, the first choice is used instead. |
| `WISE_APPEARANCE_COOKIE_NAME` | `'wise_appearance'` | The cookie read by the middleware and written by the view and `wiseSetAppearance()`. |
| `WISE_APPEARANCE_COOKIE_AGE` | one year | Cookie lifetime in seconds (server-set cookies). |
| `WISE_APPEARANCE_QUERY_PARAM` | `'appearance'` | `?appearance=` switches and remembers. `None` disables it. |
| `WISE_APPEARANCE_SESSION_KEY` | `'wise_appearance'` | Also read from and written to the session. `None` disables it. |
| `WISE_APPEARANCE_RESOLVER` | `None` | Dotted path to `callable(request) -> str | None`, consulted after the cookie and session. |

| Python API (`wise_core.appearance`) | |
|---|---|
| `get_appearance_from_request(request)` | The resolved appearance for a request. |
| `get_appearances()` / `get_default_appearance()` / `is_valid_appearance(v)` | The configured choices. |
| `persist_appearance(request, response, value)` | Write the cookie (and session), for your own views. |
| `appearance_changed` | Signal sent by `set_appearance` with `request` and `appearance`. |

| JavaScript (`common.js`) | |
|---|---|
| `wiseSetAppearance(value)` | Switch now and write the cookie. `''` means back to the default. |
| `wise:appearancechange` | Event on `document`, `event.detail.appearance`. |

## How it combines with the other axes

The four [switchable axes](design-tokens.md#switchable-axes) still apply:

| Axis | Lumen | Tangerine |
|---|---|---|
| `data-theme` (light / dark) | yes | yes: Vanilla's light and dark values (#ffffff / #262626 panels on #f7f7f7 / #202020) |
| `data-palette` (accent) | yes | **ignored**: Tangerine's colors are fixed (link blue `#0066cc`, green main action `#0e8420`) |
| `data-radius` (rounding) | yes | **ignored**: Tangerine is square, except the round marks (switch, avatar, step marker) |
| `data-shadow` (cards) | yes | yes |

The settings panel hides the two groups that don't apply. Elements with the classes
`.wise-lumen-only` and `.wise-tangerine-only` show only in that appearance; use them in your own
templates when a hint applies to just one appearance.

**What Tangerine changes, token by token.** The full list is in
`wise_core/static/wise_core/css/appearances/tangerine.css`. In short:

| | Lumen | Tangerine |
|---|---|---|
| Typeface | Source Sans 3 / Source Code Pro | Ubuntu Sans / Ubuntu Sans Mono (vendored, Ubuntu Font Licence) |
| Bold | 700 / 800 | 550; `h2` is a thin 180 and `h4` a light 275 |
| Corners | 4-16px, pill buttons | 0 everywhere; the switch track stays a pill |
| Borders | 2px controls, 1px cards | 1.5px controls and cards, 1px rules, 3px tab bar |
| Fields | 8px, outlined in #dadada | `#f5f5f5` fill with only a 1.5px `#707070` bottom border |
| Control height | 32px (40 touch) | 37px (44 touch) |
| Main action (`.btn-primary`) | accent fill | green `#0e8420` |
| Links, checked controls | accent | `#0066cc` (dark `#6699cc`) |
| Focus | 2px ring, 2px outside | 3px `#2e96ff` outline, 3px inside |
| Table headers | sentence case | 12/16 uppercase, weight 550 |

**Accessibility.** Tangerine keeps three of Vanilla's own pairs exactly, even though they miss the
contrast floors (the Tangerine README lists them): the light focus blue (`#2e96ff`, 2.5–3.0:1 on
gray), caution amber as text (`#cc7900`, 3.0:1), and the green focus outline on the dark positive
button. Status text in Tangerine therefore always needs its icon and word (Lumen's rule anyway), and
notice-colored text should never stand alone.

## Add your own appearance

1. Create `wise_core/static/wise_core/css/appearances/<name>.css`, or a file in your own project
   imported after `tokens.css`. Copy `tangerine.css` as a template: a `:root[data-appearance="<name>"]`
   block that re-points the system tokens, a `[data-theme="dark"]` block, and a coarse-pointer block
   if you change control heights.
2. Re-point **system tokens only** (`--color-background-*`, `--color-content-*`, `--color-accent-*`,
   `--corner-radius-*`, `--border-width-*`, `--control-height-*`, `--font-brand`, the `--text-*`
   weights, `--focus-ring-*`). Add component overrides in `@layer components` only when no token
   can express the change, and always prefix them with `:root[data-appearance="<name>"]`.
3. `@import` it at the end of `tokens.css` (or your entry CSS, after `tokens.css`). It must come
   after Lumen's axis blocks so selectors of equal specificity win.
4. Add `('<name>', 'Label')` to `WISE_APPEARANCES`, run `npm run build:css`, and check it in light,
   dark, on a phone, and with `data-shadow="elevated"`.

## Caching and security notes

- The middleware adds **`Vary: Cookie`** to every response, so a shared cache never serves one
  visitor's appearance to another. If you full-page cache, include the appearance cookie in the
  cache key.
- The cookie holds only a short identifier that is checked against `WISE_APPEARANCES` before it is
  used. It never reaches the template unchecked, so it can't inject markup or CSS.
- `set_appearance` is POST-only, protected by CSRF, and validates `next` with Django's
  `url_has_allowed_host_and_scheme`, so it can't be used as an open redirect.
- The cookie isn't `HttpOnly`, because `wiseSetAppearance()` writes it from the browser. It's
  `SameSite=Lax`, and `Secure` over HTTPS.

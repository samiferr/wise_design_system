# Lumen components → Wise classes

Every class below is defined in `wise_core/static/wise_core/css/tokens.css`. The live, rendered catalog
with code for each is the demo docs site (`/docs/`). Icons use the `{% lucide "name" size=18 %}`
template tag (`{% load wise_icons %}`); only the icons vendored in
`wise_core/static/wise_core/icons/lucide/` exist, so check there before using a name.

Lumen's own components are Button, ActionButton, TextField, Checkbox, Switch, RadioGroup, Tabs,
StatusLight, Badge, ProgressBar, InlineAlert and Divider. Everything else here (menus, dialogs,
tables, ...) is built from the same tokens in the same shapes.

## Actions

### Buttons

Fully round, `title-s` (14px, 700), 32px tall (24px compact, 40px on touch), 16px side padding
(12px for quiet buttons), 2px border so filled and outlined buttons are the same size.

```django
<button class="btn btn-primary">Save</button>                 {# accent fill: the one main action #}
<button class="btn btn-brand">Save draft</button>             {# neutral fill (fill-neutral-hover) #}
<button class="btn btn-secondary">Cancel</button>             {# neutral outline #}
<button class="btn btn-ghost">Learn more</button>             {# quiet: lowest emphasis #}
<button class="btn btn-elevated">Import</button>              {# raised: layer-2 + emphasized shadow #}
<button class="btn btn-danger">Delete</button>                {# negative fill #}
<button class="btn btn-primary">{% lucide "plus" size=16 %}<span>New</span></button>
<a class="btn btn-secondary btn-disabled" aria-disabled="true">Can't</a>  {# disabled <a> #}
<button class="btn btn-primary btn-sm">Small</button>         {# btn-sm 24px, btn-lg 40px, btn-xl 48px #}
```

Aliases: `btn-filled` = `btn-primary`, `btn-tonal` = `btn-brand`, `btn-outlined` = `btn-secondary`,
`btn-text` = `btn-ghost`. Emphasis order on a screen: at most one accent fill, then neutral fill,
then outline, then quiet. Hover steps a fill one shade (`accent-background-hover`), press two
(`-down`); outline and quiet buttons fill with `fill-neutral-hover` / `-down`. Disabled: `content-disabled`
on `fill-neutral-hover`.

### Icon buttons

Round, sized to the control height. `.btn-icon` works with or without `.btn`. Always give an
accessible name.

```django
<button class="btn-icon" aria-label="Edit">{% lucide "pencil" size=16 %}</button>                     {# quiet #}
<button class="btn-icon btn-secondary" aria-label="Filter">{% lucide "filter" size=16 %}</button>     {# outlined #}
<button class="btn btn-primary btn-icon" aria-label="Search">{% lucide "search" size=16 %}</button>   {# accent fill #}
<button class="btn btn-brand btn-icon" aria-label="Favorite">{% lucide "star" size=16 %}</button>     {# neutral fill #}
```

### FAB

```django
<button class="fab" aria-label="Compose">{% lucide "pencil" size=24 %}</button>
<button class="fab fab-extended">{% lucide "plus" size=24 %}<span>New order</span></button>
```

A 56px accent pill with the `elevated` shadow. Place it fixed bottom-right (`fixed bottom-6 right-6`)
on screens with one dominant action.

### Button group (`.btn-group`)

```django
<div class="btn-group" role="group" aria-label="View">
    <a class="btn selected" href="?view=cards">Cards</a>
    <a class="btn" href="?view=table">Table</a>
</div>
```

Outlined segments with shared borders and round ends; the selected segment is filled with
`neutral-background` (the pressed action-button look). Icon-only segments: `btn btn-icon` children.

### Menu (`.dropdown`)

`<details>`-based; `common.js` handles click-away, Escape and overflow escape. A popover:
`background-elevated`, `border-subtle` edge, 10px corners, `shadow-elevated`, 32px items.

```django
<details class="dropdown">
    <summary class="btn-icon" aria-label="Row actions">{% lucide "ellipsis-vertical" size=16 %}</summary>
    <div class="dropdown-panel">
        <div class="dropdown-header">Record</div>
        <a class="dropdown-item" href="{{ edit_url }}">{% lucide "pencil" size=16 %}Edit</a>
        <hr class="dropdown-divider">
        <a class="dropdown-item dropdown-item-danger" href="{{ delete_url }}">{% lucide "trash-2" size=16 %}Delete</a>
    </div>
</details>
```

## Communication

| Lumen | Wise | Notes |
|---|---|---|
| Badge (count) | `<span class="badge-count">3</span>` | negative fill, `detail-xs` |
| Badge | `badge` (neutral) / `badge-green` (positive) / `badge-orange` (notice) / `badge-red` (negative) / `badge-action` (informative) / `badge-brand` (accent) / `badge-tertiary` (purple) / `badge-grey` (neutral) | solid pill, `title-xs`, always a word |
| StatusLight | `<span class="status-light status-light-positive">Approved</span>` (`-notice`, `-negative`, `-informative`, `-purple`, `-cyan`; bare = neutral) | 8px dot + label |
| InlineAlert | `.callout` + `.callout-info/-success/-warning/-danger` (`.callout-icon`, `.callout-title`) | layer-2 box, 2px status border and icon, 8px corners |
| Toast | `.toast` (`.toast-success/-error/-warning/-info` = solid status fill) in `ul.toast-stack` | neutral-background by default. Django `messages` render automatically as `.flash-messages` |
| Tooltip | `<span class="tooltip" data-tooltip="Copied">…</span>` (`.tooltip-bottom`) | neutral-background, 4px corners |
| ProgressBar | `<div class="progress"><span class="progress-value" style="--value: 40%"></span></div>` (`.progress-lg`) | 6px `border-subtle` track, accent fill |
| Circular progress | `.progress-ring` (SVG, `.progress-ring-track` + `.progress-ring-indicator`), indeterminate `.spinner` (`-sm`/`-lg`) | |
| Empty state | `.empty-state` > `.empty-state-icon`, `.empty-state-title`, `.empty-state-text`, `.empty-state-actions` | `wise_core/components/_no_data.html` renders it for lists |

## Containment

| Need | Wise |
|---|---|
| Card | `.card` (layer-2 + `border-subtle`; raised with a shadow under `data-shadow`), `.card-outlined`, `.card-elevated`, `.card-filled`; inside: `.card-kicker` (detail-s accent), `.card-title` (title-m), `.card-content` (body-s content-subdued), `.card-meta`. `<a class="card">` darkens its border on hover. |
| Dialog | `<dialog class="dialog" id="x">` > `.dialog-header` (`h2.dialog-title`), `.dialog-body`, `.dialog-footer` (neutral/quiet buttons, then the confirming button last). Open with `wiseOpenDialog('x')`. 16px corners, `shadow-dragged`. |
| Side sheet (modal) | `.drawer` / `.drawer-left` + `.drawer-backdrop`, sections `.drawer-header/-body/-footer`. `wiseOpenDrawer(id)` / `wiseCloseDrawer(id)`. |
| Divider | `hr.divider` (1px `border-subtle`), `.divider-m` (2px), `.divider-l` (4px), `.divider-vertical`, `.divider-labeled` |
| Accordion | `.accordion` > `details.accordion-item` > `summary` (+ `.accordion-chevron`) + `.accordion-content` |
| Carousel | `.carousel` > `.carousel-track` > `.carousel-item`; `.carousel-nav` > `a.carousel-dot(.selected)` |
| Toolbar | `.top-actions-header` with `.top-nav-item` actions (the CRUD back/edit/delete bar) |

## Navigation

| Need | Wise |
|---|---|
| Side navigation | `wise_core/components/nav_menu.html`: `.menu-node > h3` (section heading, title-xs) + `a.menu-link(.selected)` rows (selected = `fill-neutral-hover`, bold `content-heading`) |
| Tree nav | `.tree` > `details.tree-item` > `summary` + `.tree-item-children` > `a.tree-leaf(.selected)` |
| Tabs | `.tab-bar` > `a.bar-item(.selected)` with optional icon and `.tab-count`; tabs are links (one URL per tab). Bold `title-s`, selected tab gets a 2px `content-heading` indicator |
| Top app bar | `.top-bar` (mobile), `.top-bar-logo` |
| Breadcrumb | `nav.breadcrumb` > `a.breadcrumb-item`, `.breadcrumb-separator` |
| Pagination | `a.pagination-link` (`.selected` = `neutral-background`, `.disabled`), rendered by `_pagination.html` |

## Selection & text inputs

| Lumen | Wise |
|---|---|
| TextField | `.input` (`.input-sm`, `.input-lg`), `.select`, `.textarea`; inside `.form-field` any Django widget is styled automatically. 32px, 8px corners, `border-default` on `background-layer-2`; focus draws the 2px ring; invalid thickens the border to 2px `negative-content` |
| Label / help / error | `.form-label` (+ `.form-required`), `.helptext`, `.errorlist`; wrap in `.form-field.form-field-error` for the error state |
| Form layout | `.form-stack` (one column) / `.form-stack-compact` (two), `.form-actions` footer, `.form-alert` for non-field errors; `_form_fields.html` renders all of this from a Django form |
| Prefix/suffix | `.input-group` > `.input-group-addon` + `.input` |
| Checkbox / radio | `.checkbox`, `.radio` (16px, 2px `border-default`; accent fill + white check / 5px accent ring when selected). Also applied to unclassed checkboxes and radios inside `.form-field` |
| Switch | `<input type="checkbox" class="switch">` (28×16 pill, 8px handle) |
| Tag | `.tag` (24px outlined, 4px corners), `.tag-action` (selected, neutral fill), `.tag-remove` (trailing ×) |
| Rating | `.rating` / `.rating-input` |
| OTP | `.otp-group` > `input.otp-input` |
| Date/time/color/file | native inputs inside `.form-field`; `.color-input`; the file button renders as a neutral-fill button |
| Autocomplete / rich text | `wise_autocomplete` and `wise_richtext` widgets (popover surface `.autocomplete-panel`; Quill themed by `wise_richtext.css`) |

## Data display

| Need | Wise |
|---|---|
| Table | `table.data-table` (title-s headers with a 2px rule, body-s cells, subtle row dividers, `fill-neutral-hover` row hover); sortable headers via `_sortable_th.html` |
| Record detail | `.detail-panel` (> `.detail-panel-header`, `table` of `th`/`td`) |
| Avatar | `.avatar` (40px circle, neutral fill), `.avatar-sm`/`-lg`, `.avatar-square`, `.avatar-group` |
| Charts | `<canvas class="chart-canvas" data-chart="{% chart_json cfg %}">` in a `.chart-frame`; series colors are the accent then Lumen step-900 hues (`wise_core/charts.py`) |
| Donut | `.donut-chart` (`style="--value: 64"`) |
| Calendar | `.calendar` > `.calendar-header`, `.calendar-weekdays`, `.calendar-grid` > `.calendar-day(.is-today/.is-outside)` > `.calendar-event` (accent-subtle) |

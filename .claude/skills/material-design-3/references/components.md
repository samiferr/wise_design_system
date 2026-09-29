# M3 components → Wise classes

Every class below is defined in `wise_core/static/wise_core/css/tokens.css`. The live, rendered catalog
with code for each is the demo docs site (`/docs/`). Icons use the `{% lucide "name" size=18 %}`
template tag (`{% load wise_icons %}`); only the icons vendored in
`wise_core/static/wise_core/icons/lucide/` exist, so check there before using a name.

## Actions

### Buttons (m3.material.io/components/buttons)

40px tall (32px compact), pill-shaped, `label-large`, 24px side padding (12px for text buttons).

```django
<button class="btn btn-primary">Save</button>                 {# M3 filled: the one main action #}
<button class="btn btn-brand">Save draft</button>             {# M3 filled tonal: secondary-container #}
<button class="btn btn-secondary">Cancel</button>             {# M3 outlined #}
<button class="btn btn-ghost">Learn more</button>             {# M3 text: lowest emphasis #}
<button class="btn btn-elevated">Import</button>              {# M3 elevated #}
<button class="btn btn-danger">Delete</button>                {# filled, error role #}
<button class="btn btn-primary">{% lucide "plus" size=18 %}<span>New</span></button>
<a class="btn btn-secondary btn-disabled" aria-disabled="true">Can't</a>  {# disabled <a> #}
```

M3-named aliases: `btn-filled` = `btn-primary`, `btn-tonal` = `btn-brand`, `btn-outlined` =
`btn-secondary`, `btn-text` = `btn-ghost`. Emphasis order on a screen: at most one filled, then
tonal, then outlined, then text.

### Icon buttons

40px circles. `.btn-icon` works with or without `.btn`. Always give an accessible name.

```django
<button class="btn-icon" aria-label="Edit">{% lucide "pencil" size=20 %}</button>                     {# standard #}
<button class="btn-icon btn-secondary" aria-label="Filter">{% lucide "filter" size=20 %}</button>     {# outlined #}
<button class="btn btn-primary btn-icon" aria-label="Search">{% lucide "search" size=20 %}</button>   {# filled #}
<button class="btn btn-brand btn-icon" aria-label="Favorite">{% lucide "star" size=20 %}</button>         {# tonal #}
```

### FAB

```django
<button class="fab" aria-label="Compose">{% lucide "pencil" size=24 %}</button>
<button class="fab fab-extended">{% lucide "plus" size=24 %}<span>New order</span></button>
```

Place it fixed bottom-right (`fixed bottom-6 right-6`) on screens with one dominant action.

### Segmented button (`.btn-group`)

```django
<div class="btn-group" role="group" aria-label="View">
    <a class="btn selected" href="?view=cards">Cards</a>
    <a class="btn" href="?view=table">Table</a>
</div>
```

Outlined segments, pill ends, selected segment in `secondary-container`. Icon-only segments:
`btn btn-icon` children.

### Menu (`.dropdown`)

`<details>`-based; `common.js` handles click-away, Escape and overflow escape.

```django
<details class="dropdown">
    <summary class="btn-icon" aria-label="Row actions">{% lucide "ellipsis-vertical" size=20 %}</summary>
    <div class="dropdown-panel">
        <div class="dropdown-header">Record</div>
        <a class="dropdown-item" href="{{ edit_url }}">{% lucide "pencil" size=18 %}Edit</a>
        <hr class="dropdown-divider">
        <a class="dropdown-item dropdown-item-danger" href="{{ delete_url }}">{% lucide "trash-2" size=18 %}Delete</a>
    </div>
</details>
```

## Communication

| M3 | Wise | Notes |
|---|---|---|
| Badge (count) | `<span class="badge-count">3</span>` | error role, `label-small` |
| Status label (assist-chip look) | `badge badge-green` (success) / `badge-orange` (warning) / `badge-red` (error) / `badge-grey` (neutral) / `badge-action` (primary) / `badge-brand` (secondary) / `badge-tertiary` | 8px corners, `label-medium` |
| Snackbar | `.toast` (`.toast-success/-error/-warning` tint only the icon) in `ul.toast-stack` | inverse-surface. Django `messages` render automatically as `.flash-messages` |
| Plain tooltip | `<span class="tooltip" data-tooltip="Copied">…</span>` (`.tooltip-bottom`) | inverse-surface |
| Linear progress | `<div class="progress"><span class="progress-value" style="--value: 40%"></span></div>` (`.progress-lg`) | secondary-container track |
| Circular progress | `.progress-ring` (SVG, `.progress-ring-track` + `.progress-ring-indicator`), indeterminate `.spinner` (`-sm`/`-lg`) | |
| Inline message (no M3 equivalent) | `.callout` + `.callout-info/-success/-warning/-danger` | tonal container, 12px corners |
| Empty state | `.empty-state` > `.empty-state-icon`, `.empty-state-title`, `.empty-state-text`, `.empty-state-actions` | `wise_core/components/_no_data.html` renders it for lists |

## Containment

| M3 | Wise |
|---|---|
| Card | `.card` (outlined, or elevated under `data-shadow`), `.card-outlined`, `.card-elevated`, `.card-filled`; inside: `.card-kicker` (label-medium primary), `.card-title` (title-medium), `.card-content` (body-medium on-surface-variant), `.card-meta`. `<a class="card">` gets a state layer + elevation on hover. |
| Dialog (basic) | `<dialog class="dialog" id="x">` > `.dialog-header` (`h2.dialog-title`), `.dialog-body`, `.dialog-footer` (text buttons, then the confirming button last). Open with `wiseOpenDialog('x')`. |
| Side sheet (modal) | `.drawer` / `.drawer-left` + `.drawer-backdrop`, sections `.drawer-header/-body/-footer`. `wiseOpenDrawer(id)` / `wiseCloseDrawer(id)`. |
| Divider | `hr.divider`, `.divider-vertical`, `.divider-labeled` |
| List / expansion | `.accordion` > `details.accordion-item` > `summary` (+ `.accordion-chevron`) + `.accordion-content` |
| Carousel | `.carousel` > `.carousel-track` > `.carousel-item`; `.carousel-nav` > `a.carousel-dot(.selected)` |
| Toolbar (docked) | `.top-actions-header` with `.top-nav-item` actions (the CRUD back/edit/delete bar) |

## Navigation

| M3 | Wise |
|---|---|
| Navigation drawer | `wise_core/components/nav_menu.html`: `.menu-node > h3` (section headline) + `a.menu-link(.selected)` pills (secondary-container active indicator) |
| Tree nav | `.tree` > `details.tree-item` > `summary` + `.tree-item-children` > `a.tree-leaf(.selected)` |
| Primary tabs | `.tab-bar` > `a.bar-item(.selected)` with optional icon and `.tab-count`; tabs are links (one URL per tab) |
| Top app bar (small) | `.top-bar` (mobile), `.top-bar-logo` |
| Breadcrumb | `nav.breadcrumb` > `a.breadcrumb-item`, `.breadcrumb-separator` |
| Pagination | `a.pagination-link` (`.selected`, `.disabled`), rendered by `_pagination.html` |

## Selection & text inputs

| M3 | Wise |
|---|---|
| Outlined text field | `.input` (`.input-sm`, `.input-lg`), `.select`, `.textarea`; inside `.form-field` any Django widget is styled automatically |
| Field label / supporting text / error | `.form-label` (+ `.form-required`), `.helptext`, `.errorlist`; wrap in `.form-field.form-field-error` for the error state |
| Form layout | `.form-stack` (one column) / `.form-stack-compact` (two), `.form-actions` footer, `.form-alert` for non-field errors; `_form_fields.html` renders all of this from a Django form |
| Prefix/suffix | `.input-group` > `.input-group-addon` + `.input` |
| Checkbox / radio | `.checkbox`, `.radio` (18px, primary accent) |
| Switch | `<input type="checkbox" class="switch">` (52x32 M3 switch) |
| Chips | `.tag` (outlined, 8px), `.tag-action` (selected filter chip), `.tag-remove` (trailing ×) |
| Rating | `.rating` / `.rating-input` |
| OTP | `.otp-group` > `input.otp-input` |
| Date/time/color/file | native inputs inside `.form-field`; `.color-input`; the file button renders as a tonal button |
| Autocomplete / rich text | `wise_autocomplete` and `wise_richtext` widgets (menu surface `.autocomplete-panel`) |

## Data display

| Need | Wise |
|---|---|
| Table | `table.data-table` (title-small headers, body-medium cells, hover state layer); sortable headers via `_sortable_th.html` |
| Record detail | `.detail-panel` (> `.detail-panel-header`, `table` of `th`/`td`) |
| Avatar | `.avatar` (40px circle, primary-container), `.avatar-sm`/`-lg`, `.avatar-square`, `.avatar-group` |
| Charts | `<canvas class="chart-canvas" data-chart="{% chart_json cfg %}">` in a `.chart-frame`; series colors are M3 roles (`wise_core/charts.py`) |
| Donut | `.donut-chart` (`style="--value: 64"`) |
| Calendar | `.calendar` > `.calendar-header`, `.calendar-weekdays`, `.calendar-grid` > `.calendar-day(.is-today/.is-outside)` > `.calendar-event` |

// Boots every Chart.js chart on the page from its `<canvas data-chart="...">`
// attribute (a JSON-encoded Chart.js config, written by the `chart_json`
// template tag - see wise_core/charts.py).
//
// Canvas has no CSS cascade of its own, so a color written as
// `var(--color-action-600)` would draw as nothing. Every string in the config
// is resolved against the page's live computed style before it reaches
// Chart.js, so charts re-theme along with everything else (palette, dark
// mode, ...) with no server round-trip. A trailing `@alpha` (e.g.
// `"var(--color-action-600)@0.15"`, written by `charts.color_alpha()`) bakes
// in translucency - useful for an area fill under a line, where a flat
// design token would be too strong.
(function () {
    'use strict';

    var VAR_RE = /^var\((--[\w-]+)\)(?:@([\d.]+))?$/;
    var normalizeCtx = null;

    // Canvas normalizes any color it's given (hex, oklch, named, ...) to
    // `#rrggbb` or `rgb(a)(...)` when the property is read back - the same
    // trick lets us bolt an alpha channel onto a color we didn't compute.
    function withAlpha(cssColor, alpha) {
        normalizeCtx = normalizeCtx || document.createElement('canvas').getContext('2d');
        normalizeCtx.fillStyle = '#000';
        normalizeCtx.fillStyle = cssColor;
        var normalized = normalizeCtx.fillStyle;
        if (normalized.charAt(0) === '#') {
            var r = parseInt(normalized.slice(1, 3), 16);
            var g = parseInt(normalized.slice(3, 5), 16);
            var b = parseInt(normalized.slice(5, 7), 16);
            return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
        }
        return normalized.replace(/rgba?\(([^)]+)\)/, function (_, parts) {
            var rgb = parts.split(',').slice(0, 3).join(',');
            return 'rgba(' + rgb + ',' + alpha + ')';
        });
    }

    function resolve(value) {
        if (Array.isArray(value)) return value.map(resolve);
        if (value && typeof value === 'object') return resolveAll(value);
        if (typeof value !== 'string') return value;
        var match = VAR_RE.exec(value);
        if (!match) return value;
        var resolved = getComputedStyle(document.documentElement).getPropertyValue(match[1]).trim();
        return match[2] ? withAlpha(resolved, parseFloat(match[2])) : resolved;
    }

    function resolveAll(config) {
        var out = Array.isArray(config) ? [] : {};
        for (var key in config) {
            if (Object.prototype.hasOwnProperty.call(config, key)) out[key] = resolve(config[key]);
        }
        return out;
    }

    function createChart(canvas) {
        var raw = canvas.getAttribute('data-chart');
        if (!raw) return null;
        return new Chart(canvas, resolveAll(JSON.parse(raw)));
    }

    function boot(root) {
        (root || document).querySelectorAll('canvas[data-chart]').forEach(function (canvas) {
            if (canvas.wiseChart) canvas.wiseChart.destroy();
            canvas.wiseChart = createChart(canvas);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { boot(document); });
    } else {
        boot(document);
    }

    // The settings panel flips data-theme/data-palette/... on <html> without
    // a reload (see docs/design-tokens.md), which changes what every
    // `var(--color-*)` above resolves to - rebuild live charts to match.
    new MutationObserver(function () { boot(document); })
        .observe(document.documentElement, {attributes: true});

    window.wiseCharts = {boot: boot};
})();

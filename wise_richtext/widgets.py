from django import forms


class RichTextInputWidget(forms.Textarea):
    """
    A `forms.Textarea` drop-in that renders as a Quill (https://quilljs.com)
    rich-text editor, extracted verbatim from DCMS7's `core.widgets.RichTextInputWidget`.
    The textarea itself stays in the DOM (hidden) as the real form field;
    Quill mirrors its HTML content into it on every edit, so `field.value`
    on the server is plain HTML - sanitize it before rendering untrusted
    HTML back out. See docs/rich-text-widget.md.
    """
    template_name = 'wise_richtext/widgets/rich_html.html'

    class Media:
        css = {'all': ('wise_richtext/css/quill_snow.css',)}
        js = ('wise_richtext/js/quill.js',)

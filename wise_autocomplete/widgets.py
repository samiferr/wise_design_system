from django import forms


class AutocompleteInputWidget(forms.TextInput):
    template_name = 'wise_autocomplete/widgets/autocomplete_input.html'

    class Media:
        js = ('wise_autocomplete/js/axios.min.js',)


class AutoSuggestInputWidget(forms.TextInput):
    template_name = 'wise_autocomplete/widgets/autosuggest_input.html'

    class Media:
        js = ('wise_autocomplete/js/axios.min.js',)

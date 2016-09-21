/**
 * Main JS file for admin site. No jQuery required.
 * Depends on:
 * - codemirror.js
 * - jinja2.js
 */


window.onload = function() {

    /**
     * Starts the jinja2 code editor for the EmailKind template field.
     */
    var templateTextarea = document.getElementById('id_template');
    if (templateTextarea) {
        var templateEditor = startEditor(
            templateTextarea,
            'htmlmixed',
            '{# Write here the HTML email template. Use jinja2 syntax. #}'
        );
    }

    var contextFragmentTextarea = document.getElementById('id_content');
    if (contextFragmentTextarea) {
        var templateEditor = startEditor(
            contextFragmentTextarea,
            'htmlmixed',
            '{# Write here the HTML email template. Use jinja2 syntax. #}'
        );
    }

    /**
     * Starts the jinja2 code editor for the EmailKind plain template field.
     */
    var plainTemplateTextarea = document.getElementById('id_plain_template');
    if (plainTemplateTextarea) {
        var plainTemplateEditor = startEditor(
            plainTemplateTextarea,
            'jinja2',
            '{# Write here the plain email template. Use jinja2 syntax. #}'
        );
    }

    /**
     * Starts the javascript/json code editor for the EmailKind default context field.
     */
    var defaultContextTextarea = document.getElementById('id_default_context');
    if (defaultContextTextarea) {
        var defaultContextEditor = startEditor(
            defaultContextTextarea,
            'application/json'
        );
    }

    /**
     * Starts the javascript/json code editor for the EmailKind test context field.
     */
    var testContextTextarea = document.getElementById('id_test_context');
    if (testContextTextarea) {
        var testContextEditor = startEditor(
            testContextTextarea,
            'application/json',
            '{}'
        );
    }

    /**
     * Starts the javascript/json code editor for the EmailKind test params field.
     */
    var testParamsTextarea = document.getElementById('id_test_params');
    if (testParamsTextarea) {
        var testParamsEditor = startEditor(
            testParamsTextarea,
            'application/json'
        );
    }

    /**
     * Starts the javascript/json code editor for the EmailEntry context.
     */
    var contextTextarea = document.getElementById('id_context');
    if (contextTextarea) {
        var contextEditor = startEditor(
            contextTextarea,
            'application/json',
            null,
            true
        );
    }

    /**
     * Starts the html code editor for the EmailEntry rendered template.
     */
    var renderedTemplateTextarea = document.getElementById('id_rendered_template');
    if (renderedTemplateTextarea) {
        var renderedTemplateEditor = startEditor(
            renderedTemplateTextarea,
            'htmlmixed',
            null,
            true
        );
    }

    /**
     * Starts the jinja2 code editor for the EmailEntry plain template.
     */
    var plainRenderedTemplateTextarea = document.getElementById('id_rendered_plain_template');
    if (plainRenderedTemplateTextarea) {
      var plainRenderedTemplateEditor = startEditor(
          plainRenderedTemplateTextarea,
          'jinja2',
          null,
          true
      );
    }

    /**
     * Starts the javascript/json code editor for the EmailEntry metadata.
     */
    var metadataTextarea = document.getElementById('id_metadata');
    if (metadataTextarea) {
        var metadataEditor = startEditor(
            metadataTextarea,
            'application/json',
            null,
            true
        );
    }

};

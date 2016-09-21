function startEditor(textarea, mode, defaultContent, readOnly) {
    defaultContent = defaultContent || '';
    readOnly = readOnly || false;
    var editor = CodeMirror.fromTextArea(textarea, {
            mode: mode,
            lineNumbers: true,
            readOnly: readOnly
    });
    // For some reason the property 'value' does not work in constructor.
    var content = textarea.innerHTML === '' ?
            defaultContent :
            htmlDecode(textarea.innerHTML);
    editor.setValue(content);
}

/**
 * Snippet to decode html characters.
 * Taken from CSS-TRICKS:
 * https://css-tricks.com/snippets/javascript/unescape-html-in-js/
 */
function htmlDecode(input) {
  var e = document.createElement('div');
  e.innerHTML = input;
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
}

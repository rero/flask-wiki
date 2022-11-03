/*
  This file is part of Flask-Wiki
  Copyright (C) 2020 RERO

  Flask-Wiki is free software; you can redistribute it and/or modify
  it under the terms of the Revised BSD License; see LICENSE file for
  more details.
*/

$(document).ready(function () {
  // ask the backend for the preview and render it
  $('.wiki-editor #preview-tab').on('click', function () {
    var url = $(this).data('preview-url');
    var $form = $('form');
    var $inputs = $form.find('input, textarea, button');
    var $pre = $('#preview');
    var bodycontent = 'title: preview\n\n' + $form.find('textarea').val();
    $inputs.prop('disabled', true);
    $pre
      .removeClass('alert')
      .removeClass('alert-error')
      .html('Loading...');
    $.ajax({
      url: url,
      type: 'POST',
      data: { body: bodycontent },
      success: function (msg) {
        $pre.html(msg);
      },
      error: function (e) {
        console.log('error: ', e);
        $pre.addClass('alert').addClass('alert-error');
        $pre.html('There was a problem with the preview.');
      },
      complete: function () {
        $inputs.prop('disabled', false);
      }
    });
  });

  // Add the following code if you want the name of the file appear on select
  $('.wiki-files .custom-file-input').on('change', function () {
    var form = $('form');
    form.submit();
  });

  // copy the markdown code in the clip board
  $('.wiki-files .copy-md-code').on('click', function () {
    // function copy(name, link) {
    var name = $(this).data('name');
    var link = $(this).data('link');;
    copyToClipboard(`![${name}](${link} "${name}")`);
  });

  // copy the url code in the clip board
  $('.copy-file-code').on('click', function () {
    // function copy(name, link) {
    var name = $(this).data('name');
    var link = $(this).data('link');
    copyToClipboard(`[${name}](${link})`);
  });

  // Change the target modal when an element is clicked
  $('.delete-file').on('click', function (e) {
    var file = e.currentTarget.id;
    var confirm = document.getElementById("confirm");
    var url = confirm.href.concat(file);
    document.getElementById("confirm").href=url;
  });
});

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(
    () => {
      $('#copy-success').toast('show');
    },
    () => {
      $('#copy-error').toast('show');
    }
  );
}

// Load Easy MDE in editor-body
try {
    const easyMDE = new EasyMDE({
    spellChecker: false, // Disable spellchecker (only English)
    sideBySideFullscreen: false, // Allow side by side preview
    showIcons: ["code", "table", "heading-1", "heading-2", "heading-3"],
    forceSync: true, // So that textArea doesn't appear as empty to flask
    maxHeight: "500px",
  });
} catch (TypeError) {}

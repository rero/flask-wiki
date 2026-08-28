// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: BSD-3-Clause

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

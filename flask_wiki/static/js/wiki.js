// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: BSD-3-Clause

$(document).ready(function () {
  // reveal the messages flashed by the server
  $('.wiki-toasts .toast[data-autoshow]').toast('show');

  // ask the backend for the preview and render it
  $('#preview-tab').on('click', function () {
    const $tab = $(this);
    const $form = $tab.closest('form');
    const $inputs = $form.find('input, textarea, button');
    const $pre = $('#preview');
    const bodycontent = 'title: preview\n\n' + $form.find('textarea').val();
    $inputs.prop('disabled', true);
    $pre.removeClass('alert alert-danger').text($tab.data('loading-text'));
    $.ajax({
      url: $tab.data('preview-url'),
      type: 'POST',
      data: { body: bodycontent },
      success: function (msg) {
        $pre.html(msg);
      },
      error: function (e) {
        console.log('error: ', e);
        $pre.addClass('alert alert-danger').text($tab.data('error-text'));
      },
      complete: function () {
        $inputs.prop('disabled', false);
      }
    });
  });

  // selecting a file uploads it, no further click needed
  $('.wiki-files .custom-file-input').on('change', function () {
    $(this).closest('form').submit();
  });

  // copy the markdown code of a file to the clipboard
  $('.wiki-files .copy-md-code').on('click', function () {
    const name = $(this).data('name');
    const link = $(this).data('link');
    copyToClipboard(`![${name}](${link} "${name}")`);
  });

  // copy the link of a page to the clipboard
  $('.copy-file-code').on('click', function () {
    const name = $(this).data('name');
    const link = $(this).data('link');
    copyToClipboard(`[${name}](${link})`);
  });

  // point the confirmation button at the file the reader asked to delete
  $('.delete-file').on('click', function () {
    $('#confirm').attr('href', $(this).data('delete-url'));
  });
});

function copyToClipboard(text) {
  // the clipboard API is missing outside a secure context
  if (!navigator.clipboard) {
    $('#copy-error').toast('show');
    return;
  }
  navigator.clipboard.writeText(text).then(
    () => {
      $('#copy-success').toast('show');
    },
    () => {
      $('#copy-error').toast('show');
    }
  );
}

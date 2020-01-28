/*
  This file is part of Flask-Wiki
  Copyright (C) 2020 RERO

  Flask-Wiki is free software; you can redistribute it and/or modify
  it under the terms of the Revised BSD License; see LICENSE file for
  more details.
*/

$(document).ready(function () {
  // ask the backend for the preview and reder it
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
    console.log('test');
    var form = $('form');
    form.submit();
  });

  // copy the markdown code in the clip board
  $('.wiki-files .copy-md-code').on('click', function () {
    // function copy(name, link) {
    var name = $(this).data('name');
    var link = $(this).data('link');
    var $temp = $('<div>');
    $('body').append($temp);
    $temp
      .attr('contenteditable', true)
      .html('![' + name + '](' + link + ' "' + name + '"' + ')')
      .select()
      .on('focus', function () {
        document.execCommand('selectAll', false, null);
      })
      .focus();
    document.execCommand('copy');
    $temp.remove();
    $('.wiki-files .toast').toast('show');
  });
});

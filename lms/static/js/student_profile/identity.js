;(function(define, undefined) {
    'use strict';

    define(['gettext', 'jquery', 'underscore', 'js/views/message_banner'],
        function(gettext, $, _, MessageBannerView) {

            return function (options) {

                var messageView = new MessageBannerView({
                    el: $('.message-banner'),
                    type: 'error'
                });
                $("#id_change").change(function() {
                    $(".proof-frame").css("opacity","0.4");
                    $(".p-field-upload-button").css("display","none");
                    $(".proof-uploading").show();

                    var files = $("#id_change").prop('files');
                    if (files.length) {
                        var proofData = new FormData();
                        proofData.append('file', $("#id_change").prop('files')[0]);
                        $.ajax({
                            type: 'POST',
                            url: options.identity_proof_upload_url,
                            cache: false,
                            processData: false,
                            contentType: false,
                            data: proofData,
                        }).success(function() {
                            $.getJSON("/get_identity_proof", function(data) {
                                $(".proof-uploading").hide();
                                $(".p-field-upload-button").show();
                                $(".proof-upload-button-title").html("Change identity proof");
                                $(".p-field-remove-button").css("display","inline");
                                $(".proof-frame").attr('src', data.id_url);
                                $(".proof-frame").css("opacity","1");
                            });
                        }).error(function(data) {
                            messageView.showMessage(data.responseJSON.user_message);
                            $(".proof-uploading").hide();
                            $(".p-field-upload-button").show();
                            $(".proof-upload-button-title").html("Change identity proof");
                            $(".proof-frame").css("opacity","1");
                        }); // ajax
                    }
                });
                $("#id_remove").click(function() {
                    $(".p-field-remove-button").hide();
                    $(".removing").show();
                    $.ajax({
                        type: 'POST',
                        url: options.identity_proof_remove_url,
                    }).success(function() {
                        $.getJSON("/get_identity_proof", function(data) {
                            $('.proof-frame').attr('src', data.id_url);
                            $(".p-field-remove-button").css("display","none");
                            $(".removing").hide();
                            $(".proof-upload-button-title").html("Upload an Image");
                        });
                    }); // ajax
                });
            };

        }); // function

}).call(this, define || RequireJS.define);
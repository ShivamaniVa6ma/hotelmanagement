

function ValidateFreeTrial() {
    var buttonFormSubmit = $('#button-form-free-trial');
    var $form = $('#form-free-trial');
    if ($form.valid() == false) {
        $form.submit();
    }
    else {
        buttonFormSubmit.html('Requesting...');
        $.ajax({
            type: "POST",
            url: "mail-post.php",
            data: 'fname=' + $('#fname').val() + '&pname=' + $('#pname').val() + '&phone=' + $('#phone').val() + '&email=' + $('#email').val() + '&cname=' + $('#cname').val() + '&message=' + $('#message').val(),
            success: function (data) {
                if (data == '1')
                    gtag_report_conversion('confirmation.html');
                else
                    alert('An error has occurred.');
            },
            error: function (data) {
                alert('An error has occurred.');
            },
            complete: function (data) {
                buttonFormSubmit.html('Request Trial<span class="lnr lnr-arrow-right"></span>');
            }
        });
    }
}

//$(document).ready(function () {
//    var form = $('#myForm'); // contact form
//    var submit = $('.submit-btn'); // submit button
//    var alert = $('.alert-msg'); // alert div for show alert message

//    // form submit event
//    form.on('submit', function (e) {
//        e.preventDefault(); // prevent default form submit

//        $.ajax({
//            url: 'mail.php', // form action url
//            type: 'POST', // form submit method get/post
//            dataType: 'html', // request type html/json/xml
//            data: form.serialize(), // serialize form data
//            beforeSend: function () {
//                alert.fadeOut();
//                submit.html('Sending....'); // change submit button text
//            },
//            success: function (data) {
//                alert.html(data).fadeIn(); // fade in response data
//                form.trigger('reset'); // reset form
//                submit.attr("style", "display: none !important");; // reset submit button text
//            },
//            error: function (e) {
//                console.log(e)
//            }
//        });
//    });
//});
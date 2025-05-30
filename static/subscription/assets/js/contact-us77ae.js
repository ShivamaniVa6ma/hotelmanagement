function ValidateFreeTrial() {
    var buttonFormSubmit = $('#button-form-contact');
    var $form = $('#form-contact-us');
    if ($form.valid() == false) {
        $form.submit();
    }
    else {
        buttonFormSubmit.html('Submitting...');
        $.ajax({
            type: "POST",
            url: "contact-us.php",
            data: 'fname=' + $('#fname').val() + '&phone=' + $('#phone').val() + '&email=' + $('#email').val() + '&message=' + $('#message').val(),
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
                buttonFormSubmit.html('Submit<span class="lnr lnr-arrow-right"></span>');
            }
        });
    }
}
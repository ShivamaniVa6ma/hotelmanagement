$(document).ready(function () {
    // Select the input fields where you want to restrict copy-paste
    $('.input-restrict').on('copy paste cut', function (e) {
        e.preventDefault(); // Prevent the default action
    });

    // Optionally, disable right-click context menu on the specific input
    $('.input-restrict').on('contextmenu', function (e) {
        e.preventDefault(); // Prevent right-click menu
    });

    // Disable keyboard shortcuts for copy (Ctrl+C), paste (Ctrl+V), and cut (Ctrl+X)
    $(document).on('keydown', function (e) {
        // Check if the target is an input field with the class 'no-copy-paste'
        if ($(e.target).hasClass('input-restrict')) {
            if (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'x')) {
                e.preventDefault(); // Prevent the action
            }
        }
    });
});
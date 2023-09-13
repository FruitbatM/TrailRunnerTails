$(document).ready(function() {
    // Highlight the navigation link on click
    // Add a click event handler to all navigation links with the class "nav-link"
    $('.nav-link').click(function() {
        // Remove the "active" class from all navigation links
        $('.nav-link').removeClass('active');
        // Add the "active" class to the clicked navigation link
        $(this).addClass('active');
    });
});
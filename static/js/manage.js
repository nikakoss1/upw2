$(document).ready(function(){
    var form = $('#manage_form');
    var start_button = $('#id_start');
    var stop_button = $('#id_stop');
    var refresh_button = $('#id_refresh');

    start_button.on("click", function(e) {
        e.preventDefault(); //Prevent submit
        var data = {
          'website_id' : form.data('website'),
        };
        var formData = form.serialize() + '&' + $.param(data);
        var thisURL = start_button.data('url');
        $.ajax({
            method: "POST",
            url: thisURL,
            dataType: "json",
            data: formData,
            success: handleFoodFormSuccess,
            error: handleFoodFormError,
            timeout:3000,
        });
        return false;

        function handleFoodFormSuccess(data, textStatus, jqXHR){
            location.reload();
       }
       function handleFoodFormError(errorThrown){
            console.log(errorThrown);
       }
    });

    stop_button.on("click", function(e) {
        e.preventDefault(); //Prevent submit
        var data = {
          'website_id' : form.data('website'),
        };
        var formData = form.serialize() + '&' + $.param(data);
        var thisURL = stop_button.data('url');
        console.log(thisURL)
        console.log(formData)
        $.ajax({
            method: "POST",
            url: thisURL,
            dataType: "json",
            data: formData,
            success: handleFoodFormSuccess,
            error: handleFoodFormError,
            timeout:3000,
        });
        return false;

        function handleFoodFormSuccess(data, textStatus, jqXHR){
            location.reload();
       }
       function handleFoodFormError(errorThrown){
            console.log(errorThrown);
       }
    });
    refresh_button.on("click", function(e){
        e.preventDefault();
        location.reload();
    });

    refresh_button.on("click", function(e){
        e.preventDefault();
        location.reload();
    });
});
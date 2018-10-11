$(document).ready(function(){
    $('#username').keyup(function(){
        data = $("#regForm").serialize()
        $.ajax({
            method: "POST",
            url: "/username",
            data: data
        })
        .done(function(x){
             console.log("response came back", x);
             $('#usernamemsg').html(x)
        })
        .fail(function(err){
            console.log("we got an error", err);
        })
        .always(function(){
            console.log('It is over');
        })
 
    })
    
 
 })
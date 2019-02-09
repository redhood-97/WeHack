

  //  var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var request = new XMLHttpRequest();
    function call() {
        request.open('GET','http://localhost:8080/monitor', true);
        request.onload = function () {
        // console.log(this.responseText);
        var data = JSON.parse(this.responseText);
        
        $('#server_output_data').text(data["processed_st"]);

    }
    request.send();
}
setInterval(call, 1000);
    


 
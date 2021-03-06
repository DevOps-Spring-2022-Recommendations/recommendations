$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#id").val(res.id);
        $("#type").val(res.type);
        $("#status").val(res.status);
        $("#rec_product_id").val(res.rec_product_id);
        $("#src_product_id").val(res.src_product_id);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#id").val("");
        $("#type").val("");
        $("#status").val("");
        $("#rec_product_id").val("");
        $("#src_product_id").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        let type = $("#type").val();
        let status = $("#status").val();
        let src_product_id = parseInt($("#src_product_id").val());
        let rec_product_id = parseInt($("#rec_product_id").val());
    

        let data = {
            
            "src_product_id": src_product_id,
            "rec_product_id": rec_product_id,
            "type": type,
            "status": status
        };

        $("#flash_message").empty();
       
        let ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
            flash_message("error")
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        let id = $("#id").val();
        let type = $("#type").val();
        let status = $("#status").val();
        let src_product_id = parseInt($("#src_product_id").val());
        let rec_product_id = parseInt($("#rec_product_id").val());

        let data = {
            
            "src_product_id": src_product_id,
            "rec_product_id": rec_product_id,
            "type": type,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/recommendations/${id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Pet
    // ****************************************

    $("#retrieve-btn").click(function () {

        let id = $("#id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations/${id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        let id = $("#id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/recommendations/${id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        let src_product_id = parseInt($("#src_product_id").val());
        let rec_product_id = parseInt($("#rec_product_id").val());
        let type = $("#type").val();
        let status = $("#status").val();

        let queryString = "";

        if (src_product_id) {
            queryString += 'src_product_id=' + src_product_id
        }   
        if (rec_product_id) {
            if (queryString.length > 0) {
                queryString += '&rec_product_id=' + rec_product_id
            } else {
                queryString += 'rec_product_id=' + rec_product_id
            }
        }
        if (type) {
            if (queryString.length > 0) {
                queryString += '&type=' + type
            } else {
                queryString += 'type=' + type
            }
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">src_product_id</th>'
            table += '<th class="col-md-2">rec_product_id</th>'
            table += '<th class="col-md-2">type</th>'
            table += '<th class="col-md-2">status</th>'
        
            table += '</tr></thead><tbody>'
            let firstPet = "";
         
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.src_product_id}</td><td>${pet.rec_product_id}</td><td>${pet.type}</td><td>${pet.status}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})

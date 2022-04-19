$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        // let type = $("#r_type").val();
        // let status = $("#r_status").val();
        // let src_product_id = parseInt($("#sourceid").val());
        // let rec_product_id = parseInt($("#targetid").val());
        
        $("#pet_id").val(res.id);
        $("#r_type").val(res.type);
        $("#r_status").val(res.status);
        $("#targetid").val(res.rec_product_id);
        $("#sourceid").val(res.src_product_id);
        // $("#pet_name").val(res.name);
        // $("#pet_category").val(res.category);
        // if (res.available == true) {
        //     $("#pet_available").val("true");
        // } else {
        //     $("#pet_available").val("false");
        // }
        // $("#pet_gender").val(res.gender);
        // $("#pet_birthday").val(res.birthday);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#pet_id").val("");
        $("#r_type").val("");
        $("#r_status").val("");
        $("#targetid").val("");
        $("#sourceid").val("");
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

        let type = $("#r_type").val();
        let status = $("#r_status").val();
        let src_product_id = parseInt($("#sourceid").val());
        let rec_product_id = parseInt($("#targetid").val());
    

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
            // flash_message(src_product_id)
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        let pet_id = $("#pet_id").val();
        let type = $("#r_type").val();
        let status = $("#r_status").val();
        let src_product_id = parseInt($("#sourceid").val());
        let rec_product_id = parseInt($("#targetid").val());

        let data = {
            
            "src_product_id": src_product_id,
            "rec_product_id": rec_product_id,
            "type": type,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/recommendations/${pet_id}`,
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

        let pet_id = $("#pet_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations/${pet_id}`,
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

        let pet_id = $("#pet_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/recommendations/${pet_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommandation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {
      
        // let name = $("#pet_name").val();
        // let category = $("#pet_category").val();
        // let available = $("#pet_available").val() == "true";

        let queryString = "";

        // if (name) {
        //     queryString += 'name=' + name
        // }
        // if (category) {
        //     if (queryString.length > 0) {
        //         queryString += '&category=' + category
        //     } else {
        //         queryString += 'category=' + category
        //     }
        // }
        // if (available) {
            // if (queryString.length > 0) {
            //     queryString += '&available=' + available
            // } else {
        //         queryString += 'available=' + available
        //     }
        // }
        let pet_id = $("#pet_id").val();
        let type = $("#r_type").val();
        let status = $("#r_status").val();
        let src_product_id = parseInt($("#sourceid").val());
        let rec_product_id = parseInt($("#targetid").val());
        // let name = $("#pet_name").val();
        // let category = $("#pet_category").val();
        // let available = $("#pet_available").val() == "true";

        

        // if (type) {
        //     queryString += 'type=' + type
        // }
        // if (status) {
           
        //         queryString += 'category=' + category
           
        // }
        if (src_product_id) {
           
            if (queryString.length > 0) {
                queryString += '&src_product_id=' + src_product_id
            } else {queryString += 'src_product_id=' + src_product_id}
       
        }   
        // if (rec_product_id) {
        //     if (queryString.length > 0) {
        //         queryString += '&rec_product_id=' + rec_product_id
        //     } else {
        //     queryString += 'rec_product_id=' + rec_product_id
        //     }
   
        // }
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

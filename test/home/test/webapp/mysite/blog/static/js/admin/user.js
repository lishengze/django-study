$(function () {
    console.log ('This is user.js!')
    var selectedNumb = 0;
    var sum_checkbox_id = 'action-toggle'
  	var setNumbSelector = $('.paginator')
  	var testCheckbox = 0;
    $(':checkbox').change(function(){
		    // console.log(++testCheckbox);
        if ($(this).attr('id') === sum_checkbox_id) {
            if ($(this).is(':checked')) {
                $('.action-select').each(function() {
                    if (!$(this).is(':checked')) {
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 位用户被选中');
                    }
                });
            } else {
                $('.action-select').each(function() {
                    if ($(this).is(':checked')) {

                        $(this).attr("checked", false);
                        --selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 位用户被选中');
                    }
                });
            }
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
                $(this).attr("checked", true);
            } else {
                --selectedNumb;
                $(this).attr("checked", false);
            }
            setNumbSelector.text(selectedNumb + ' 位用户被选中');
            // $('.action-select').each(function() {
            //     // console.log ($(this).attr('checked'));
            //     // console.log ($(this).is(':checked'));
            // })
        }
    })

    $('.hrefJump').click(function(){
        user_name = $(this).text();
        console.log(user_name);
        $.ajax({
          url: '/AJAX/Set_Chosen_User/',
          data: {'req_json': user_name},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              if (responseJSON.error !== '') {
                alert(responseJSON.error)
              } else {
				        console.log (responseJSON.data)
                window.location.href = responseJSON.data;
              }
          }
        });
    })

    $("#execute_selection").click(function(){
        if ($("select option:selected").attr('value') === "delete_selected") {
            var delete_user = [];
            $(":checked").each(function(){
                user_name = $(this).parent().parent().find(".hrefJump").text()
                delete_user.push(user_name)
            })

            delete_user.shift();
            console.log (delete_user)

            $.ajax({
                url: '/AJAX/Delete_User/',
                data: {'req_json': delete_user},
                dataType: 'json',
                type: 'POST',
                traditional: true,
                success: function (responseJSON) {
                    console.log (responseJSON)
                }
            });
        }
        // return false
    })

    $("input[value='搜索']").click(function(){
      var searchValue = $("#searchbar").val()
      console.log ('/admin/auth/user/search=' + searchValue + '/')
      window.location.href = '/admin/auth/user/search=' + searchValue + '/';
      return false;
    })
});

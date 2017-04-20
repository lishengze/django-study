$(function () {
    // console.log ('This is class Test!')

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
                    // if ($(this).attr('checked') !== 'checked') {
						// console.log('Is action-toggle checked!')
						// console.log ('')
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });
            } else {
                $('.action-select').each(function() {
                    if ($(this).is(':checked')) {
						// console.log('Is action-toggle unchecked!')
						// console.log ('')
                        $(this).attr("checked", false);
                        --selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });
            }

            $('.action-select').each(function() {
                // console.log ($(this).attr('checked'));
                // console.log ($(this).is(':checked'));
            })
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
                $(this).attr("checked", true);
            } else {
                --selectedNumb;
                $(this).attr("checked", false);
            }
            setNumbSelector.text(selectedNumb + ' 个被选中');

            $('.action-select').each(function() {
                // console.log ($(this).attr('checked'));
                // console.log ($(this).is(':checked'));
            })
        }
    })

    $('.hrefJump').click(function(){
        url = '/admin.html/'
        group_name = $(this).text();
        console.log(group_name);
        $.ajax({
          url: '/AJAX/Set_Chosen_Group/',
          data: {'req_json': group_name},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
            //   console.log (responseJSON)
              if (responseJSON.error !== '') {
                alert(responseJSON.error)
              } else {
				        console.log (responseJSON.data)
                window.location.href = responseJSON.data;
              }
          }
        });
        // window.location.href = url;
    })

    $("#execute_selection").click(function(){
        // console.log($("select option:selected").attr('value'))
        // console.log($("select option:selected").text())
        if ($("select option:selected").attr('value') === "delete_selected") {
            // console.log($("select option:selected").text());
            var delete_group = [];
            $(":checked").each(function(){
                group_name = $(this).parent().parent().find(".hrefJump").text()
                // console.log(group_name)
                delete_group.push(group_name)
            })

            delete_group.shift();
            console.log (delete_group)

            $.ajax({
                url: '/AJAX/Delete_Group/',
                data: {'req_json': delete_group},
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
      console.log ('/admin/auth/group/search=' + searchValue + '/')
      window.location.href = '/admin/auth/group/search=' + searchValue + '/';
      return false;
    })

});

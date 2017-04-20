$(function () {
    console.log ('This is group change!')
    console.log ($('#group_id').attr('value'))
    $("input[value='保存']").click(function(){
      var group_name = $("#id_name").val();
      var group_group = '';

      $("#id_permissions_to").find("option").each(function(){
          group_group += $(this).text() + ";"
      })

      if (group_group === '') {
        alert('还没选择组群权限!')
      } else {
        var req_data = {
          'name': group_name,
          'permission':group_group,
          'group_id': $('#group_id').attr('value')
        }
        console.log (req_data)
        $.ajax({
          url: '/AJAX/Change_Group/',
          data: {'req_json': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.status === "Successful") {
                window.location.href = '/admin/auth/group';
              } else {
                alert(responseJSON.info);
              }
          }
        });
      }
      return false;
    })

    $("input[value='保存并继续添加']").click(function(){
      var group_name = $("#id_name").val();
      var group_group = '';

      $("#id_permissions_to").find("option").each(function(){
          group_group += $(this).text() + ";"
      })

      if (group_group === '') {
        alert('还没选择组群权限!')
      } else {
        var req_data = {
          'name': group_name,
          'permission':group_group
        }
        console.log (req_data)
        $.ajax({
          url: '/AJAX/Change_Group/',
          data: {'req_json': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.status === "Successful") {
                window.location.href = '/admin/auth/group/add';
              } else {
                alert('修改组群失败!');
              }
          }
        });
      }
      return false;
    })

    $("input[value='删除']").click(function(){
      var group_name = $("#id_name").val();
      console.log (group_name)
      $.ajax({
          url: '/AJAX/Delete_Group/',
          data: {'req_json': group_name},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
            console.log (responseJSON)
              if (responseJSON.failed.length === 0) {
                window.location.href = '/admin/auth/group';
              } else {
                alert(responseJSON.failed)
              }
          }
      });
    })

    var g_permission_array = []
    $("#id_permissions_from").find("option").each(function(){
        g_permission_array.push($(this).text());
    })

    $("#id_permissions_input").keyup(function(event){
      var inputValue = $(this).val()
      console.log ('inputValue: ' + inputValue);
      $("#id_permissions_from").find("option").each(function(){
            $(this).remove()
      })

      if (inputValue === '') {
        for(var i =0; i < g_permission_array.length; ++i) {
          var value = g_permission_array[i];
          var html_element = '<option " title="'+ value +'"> '+ value + ' </option>'
          $("#id_permissions_from").append(html_element);
        }
      } else {
        for(var i =0; i < g_permission_array.length; ++i) {
          var value = g_permission_array[i];
          if (value.indexOf(inputValue) >= 0) {
            var html_element = '<option " title="'+ value +'"> '+ value + ' </option>'
            $("#id_permissions_from").append(html_element);
          }
        }
      }
    })

    $("#id_permissions_from").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_permissions_from").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_permissions_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_permissions_to").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_permissions_to").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_permissions_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_permissions_add_link").click(function(){
      // 添加选中的权限
      $("#id_permissions_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
              var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'"> '+ $(this).text() +' </option>'
              $("#id_permissions_to").append(html_element);
          }
      })
    })

    $("#id_permissions_remove_link").click(function(){
      // 移除选中的权限
      $("#id_permissions_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              $(this).remove()
          }
      })
    })

    $("#id_permissions_add_all_link").click(function(){
      // 添加选中的权限
      $("#id_permissions_from").find("option").each(function(){
            var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'"> '+ $(this).text() +' </option>'
            $("#id_permissions_to").append(html_element);
      })
    })

    $("#id_permissions_remove_all_link").click(function(){
      // 移除选中的权限
      $("#id_permissions_to").find("option").each(function(){
            $(this).remove()
      })
    })
});

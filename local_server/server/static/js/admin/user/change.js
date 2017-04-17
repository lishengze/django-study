$(function () {
    console.log ('This is user change!')

    $("input[value='保存']").click(function(){
      var user_name = $("#id_username").val();
      var user_permission = '';
      var user_groups = '';
      var email = $("#id_email").val();
      $("#id_user_permissions_to").find("option").each(function(){
          user_permission += $(this).text() + ";"
      })

      $("#id_groups_to").find("option").each(function(){
          user_groups += $(this).text() + ";"
      })

      if (user_permission === '') {
        alert('还没选择用户权限!')
      } else {
        var req_data = {
          'name': user_name,
          'email': email,
          'permission':user_permission,
          'groups': user_groups
        }
        console.log (req_data)
        $.ajax({
          url: '/AJAX/Change_User/',
          data: {'req_json': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.status === "Successful") {
                window.location.href = '/admin/auth/user';
              } else {
                alert('修改组群失败!');
              }
          }
        });
      }
      return false;
    })

    $("input[value='保存并继续添加']").click(function(){
      var user_name = $("#id_username").val();
      var user_permission = '';
      var user_groups = '';
      var email = $("#id_email").val();
      $("#id_user_permissions_to").find("option").each(function(){
          user_permission += $(this).text() + ";"
      })

      $("#id_groups_to").find("option").each(function(){
          user_groups += $(this).text() + ";"
      })

      if (user_permission === '') {
        alert('还没选择用户权限!')
      } else {
        var req_data = {
          'name': user_name,
          'email': email,
          'permission':user_permission,
          'groups': user_groups
        }
        console.log (req_data)
        $.ajax({
          url: '/AJAX/Change_User/',
          data: {'req_json': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.status === "Successful") {
                window.location.href = '/admin/auth/user/add';
              } else {
                alert('修改组群失败!');
              }
          }
        });
      }
      return false;
    })

    $("#id_user_permissions_from").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_user_permissions_from").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_user_permissions_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_user_permissions_to").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_user_permissions_to").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_user_permissions_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_user_permissions_add_link").click(function(){
      // 添加选中的权限
      $("#id_user_permissions_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
              var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'"> '+ $(this).text() +' </option>'
              $("#id_user_permissions_to").append(html_element);
          }
      })
    })

    $("#id_user_permissions_remove_link").click(function(){
      // 移除选中的权限
      $("#id_user_permissions_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              $(this).remove()
          }
      })
    })

    $("#id_groups_from").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_groups_from").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_groups_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_groups_to").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_groups_to").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_groups_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_groups_add_link").click(function(){
      // 添加选中的权限
      $("#id_groups_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
              var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'"> '+ $(this).text() +' </option>'
              $("#id_groups_to").append(html_element);
          }
      })
    })

    $("#id_groups_remove_link").click(function(){
      // 移除选中的权限
      $("#id_groups_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              $(this).remove()
          }
      })
    })
});

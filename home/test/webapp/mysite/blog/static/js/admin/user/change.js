$(function () {
    console.log ('This is user change!')
    console.log ($('#user_id').attr('value'))
    var g_permission_array = []
    $("#id_user_permissions_from").find("option").each(function(){
        g_permission_array.push($(this).text());
    })

    var g_groups_array = []
    $("#id_groups_from").find("option").each(function(){
        g_groups_array.push($(this).text());
    })

    $("#id_groups_input").keyup(function(event){
      var inputValue = $(this).val()
      console.log ('inputValue: ' + inputValue);
      $("#id_groups_from").find("option").each(function(){
            $(this).remove()
      })
      if (inputValue === '') {
        for(var i =0; i < g_groups_array.length; ++i) {
          var value = g_groups_array[i];
          var html_element = '<option " title="'+ value +'">'+ value + '</option>'
          $("#id_groups_from").append(html_element);
        }
      } else {
        for(var i =0; i < g_groups_array.length; ++i) {
          var value = g_groups_array[i];
          if (value.indexOf(inputValue) >= 0) {
            var html_element = '<option " title="'+ value +'">'+ value + '</option>'
            $("#id_groups_from").append(html_element);
          }
        }
      }
    })

    $("#id_user_permissions_input").keyup(function(event){
      var inputValue = $(this).val()
      console.log ('inputValue: ' + inputValue);
      $("#id_user_permissions_from").find("option").each(function(){
            $(this).remove()
      })

      if (inputValue === '') {
        for(var i =0; i < g_permission_array.length; ++i) {
          var value = g_permission_array[i];
          var html_element = '<option " title="'+ value +'">'+ value + '</option>'
          $("#id_user_permissions_from").append(html_element);
        }
      } else {
        for(var i =0; i < g_permission_array.length; ++i) {
          var value = g_permission_array[i];
          if (value.indexOf(inputValue) >= 0) {
            var html_element = '<option " title="'+ value +'">'+ value + '</option>'
            $("#id_user_permissions_from").append(html_element);
          }
        }
      }
    })

    $("input[value='保存']").click(function(){
      var user_name = $("#id_username").val();
      var user_permission = '';
      var user_groups = '';
      var email = $("#id_email").val();
      // $("#id_user_permissions_to").find("option").each(function(){
      //     user_permission += $(this).text() + ";"
      // })

      $("#id_groups_to").find("option").each(function(){
          user_groups += $(this).text() + ";"
      })

      var req_data = {
        'name': user_name,
        'email': email,
        'groups': user_groups,
        'user_id': $('#user_id').attr('value')
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
              alert(responseJSON.info);
            }
        }
      });
      return false;
    })

    $("input[value='保存并继续添加']").click(function(){
      var user_name = $("#id_username").val();
      var user_permission = '';
      var user_groups = '';
      var email = $("#id_email").val();
      // $("#id_user_permissions_to").find("option").each(function(){
      //     user_permission += $(this).text() + ";"
      // })

      $("#id_groups_to").find("option").each(function(){
          user_groups += $(this).text() + ";"
      })

      var req_data = {
        'name': user_name,
        'email': email,
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
      return false;
    })

    $("input[value='删除']").click(function(){
      var user_name = $("#id_username").val();
      $.ajax({
          url: '/AJAX/Delete_User/',
          data: {'req_json': user_name},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              if (responseJSON.failed.length === 0) {
                window.location.href = '/admin/auth/user';
              } else {
                alert(responseJSON.failed)
              }
          }
      });
    })

    // $("#id_user_permissions_from").find("option").click(function(event){
    //   // 激活Choose图标, 改变样式.
    //   if (!event.ctrlKey) {
    //     $("#id_user_permissions_from").find("option").each(function(){
    //         $(this).attr('selected', false);
    //     })
    //   }else {
    //     console.log ('Control Key!')
    //   }
    //
    //   $(this).attr('selected', true);
    //
    //   $("#id_user_permissions_from").find("option").each(function(){
    //       if ($(this).attr('selected')) {
    //           console.log ($(this).attr('title'));
    //       }
    //   })
    // })
    //
    // $("#id_user_permissions_to").find("option").click(function(event){
    //   // 激活Choose图标, 改变样式.
    //   if (!event.ctrlKey) {
    //     $("#id_user_permissions_to").find("option").each(function(){
    //         $(this).attr('selected', false);
    //     })
    //   }else {
    //     console.log ('Control Key!')
    //   }
    //
    //   $(this).attr('selected', true);
    //
    //   $("#id_user_permissions_to").find("option").each(function(){
    //       if ($(this).attr('selected')) {
    //           console.log ($(this).attr('title'));
    //       }
    //   })
    // })
    //
    // $("#id_user_permissions_add_link").click(function(){
    //   // 添加选中的权限
    //   $("#id_user_permissions_from").find("option").each(function(){
    //       if ($(this).attr('selected')) {
    //           var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'">'+ $(this).text() +'</option>'
    //           $("#id_user_permissions_to").append(html_element);
    //       }
    //   })
    // })
    //
    // $("#id_user_permissions_add_all_link").click(function(){
    //   $("#id_user_permissions_from").find("option").each(function(){
    //       var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'">'+ $(this).text() +'</option>'
    //       $("#id_user_permissions_to").append(html_element);
    //   })
    // })
    //
    // $("#id_user_permissions_remove_all_link").click(function(){
    //   // 移除选中的权限
    //   $("#id_user_permissions_to").find("option").each(function(){
    //         $(this).remove()
    //   })
    // })
    //
    // $("#id_user_permissions_remove_link").click(function(){
    //   // 移除选中的权限
    //   $("#id_user_permissions_to").find("option").each(function(){
    //       if ($(this).attr('selected')) {
    //           $(this).remove()
    //       }
    //   })
    // })

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

    $("#id_groups_add_all_link").click(function(){
      // 添加选中的权限
      $("#id_groups_from").find("option").each(function(){
          var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'">'+ $(this).text() +'</option>'
          $("#id_groups_to").append(html_element);
      })
    })

    $("#id_groups_add_link").click(function(){
      // 添加选中的权限
      $("#id_groups_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
              var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'">'+ $(this).text() +'</option>'
              $("#id_groups_to").append(html_element);
          }
      })
    })

    $("#id_groups_remove_all_link").click(function(){
      // 移除选中的权限
      $("#id_groups_to").find("option").each(function(){
            $(this).remove()
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

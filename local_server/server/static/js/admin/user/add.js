$(function () {
    console.log ('This is user add!')
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
        }
        console.log (req_data)
        $.ajax({
          url: '/AJAX/Add_Group/',
          data: {'req_json': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.status === "Successful") {
                window.location.href = '/admin/auth/user';
              } else {
                alert('添加组群失败!');
              }
          }
        });
      }
      return false;
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

});

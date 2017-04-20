$(function () {
    console.log ('This is user add!')

    $("input[value='保存']").click(function(){
      var user_name = $("#id_username").val();
      if (user_name === '') {
        alert('用户名不能为空！');
        return false;
      }
      if (user_name.length > 150) {
        alert('用户名长不能超过150个字符！')
        return false;
      }
      if ( $("#id_password1").val() !== $("#id_password2").val() ) {
        alert("两次输入的密码不一致！");
        return false;
      } else {
        var password = $("#id_password1").val()
      }

      var req_data = {
        'name': user_name,
        'password':password,
      }
      console.log (req_data)
      $.ajax({
        url: '/AJAX/Add_User/',
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

    })

});

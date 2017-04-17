$(function () {
  console.log ('Change password');

  function change_password() {
      if ($('#id_new_password2').val() !== $('#id_new_password1').val()) {
        alert('两次密码不一样');
      }

      user_name = localStorage.getItem('logName');
      old_password = $('#id_old_password').val();
      new_password = $('#id_new_password2').val();
      req_data = {
        'name': user_name,
        'old_password': old_password,
        'new_password': new_password
      }
      console.log (req_data);
      $.ajax({
        url: '/AJAX/Change_User_Password/',
        data: {'req_json':  JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
          console.log (responseJSON)
            if (responseJSON.error !== '') {
              alert(responseJSON.error)
            } else {
              window.location.href = responseJSON.info;
            }
        }
      });

      return false;
  }

  $("input[type='submit']").click(change_password);

  $(document).keyup(change_password);

  $(document).ready(function(){
    $("#username_nav").text(localStorage.getItem('logName'));
  });

});

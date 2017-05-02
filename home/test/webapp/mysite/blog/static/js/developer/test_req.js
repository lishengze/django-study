$(document).ready(function(){
    var ntf_task_data = []

    $('#request_real_time_info_task').click(function(){
       var req_data = {
        'ENV_KEY':'TEST_170',
        'type': '',
        '--cmd': 'info',
        '--args':'',
        '--grp': '',
        '--ctr': '',
        '--srv': '',
        '--srvno': '',
        '--ictr': '',
        '--isrv': '',
        '--isrvno': ''
      };
      $.ajax({
        url: '/AJAX/Request_Real_Time_Info_Task/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });

    })

    $('#request_real_time_versionCtr_task').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170',
        'type': 'version_control',
        '--cmd': 'rollback',
        '--args':'xml:ver=0.0.1',
        '--grp': '',
        '--ctr': '',
        '--srv': '',
        '--srvno': '',
        '--ictr': '',
        '--isrv': '',
        '--isrvno': ''
      };
      $.ajax({
        url: '/AJAX/Request_Real_Time_VersionCtr_Task/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });

    })

    $('#Request_Task_Ntf').click(function(){
      req_data = {
        'ENV_KEY':'PTEST_170',
        'type': '',
        'exec_time': 1,
        '--cmd': 'show',
        '--args':'',
        '--grp': '',
        '--ctr': '',
        '--srv': '',
        '--srvno': '',
        '--ictr': '',
        '--isrv': '',
        '--isrvno': ''
      };
      $.ajax({
        url: '/AJAX/Request_Task_Ntf/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log ('Task_data: ')
            console.log (responseJSON)
            ntf_task_data.push(responseJSON);
        }
      });
    })

    $('#Get_NTF_Task_Result').click(function(){
        task_data = ntf_task_data;
        req_data = {
          'ENV_KEY': 'TEST_170',
          'task_data': task_data
        }

      $.ajax({
        url: '/AJAX/Get_NTF_Task_Result/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (result) {
            console.log (result)
            task_result = result.task_result
            for (var value in task_result) {
              task_id = value
              if (task_result[task_id] !== 'Empty') {
                for ( var i = 0 ; i < ntf_task_data.length; ++i) {
                  if (ntf_task_data[i][0] === task_id) {
                    // ntf_task_data.remove()
                  }
                }
              }
            }

        }
      });
    })

    $('#Get_NTF_Task_State').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170'
      }
      $.ajax({
        url: '/AJAX/Get_NTF_Task_State/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Get_All_Group').click(function(){
      var req_data = {
       'ENV_KEY':'TEST_170',
       'type': '',
       '--cmd': 'info',
       '--args':'srvname',
       '--grp': '',
       '--ctr': '',
       '--srv': '',
       '--srvno': '',
       '--ictr': '',
       '--isrv': '',
       '--isrvno': ''
     };

      var req_url = '/AJAX/Request_Real_Time_Info_Task/';
      $.ajax({
        url: req_url,
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (result) {
            console.log (result)
        }
      });
    })

    $('#Get_All_SrvName').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170'
      }
      $.ajax({
        url: '/AJAX/Get_All_SrvName/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Get_Version_Difference').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170',
        'object': "server",
        'ver1': "0.0.4",
        'ver2': "0.0.20"
      };
      $.ajax({
        url: '/AJAX/Get_Version_Difference/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Get_All_UnUpdate_VersionInfo').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170'
      };
      $.ajax({
        url: '/AJAX/Get_All_UnUpdate_VersionInfo/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Delete_Update_File').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170',
        'fileName': "test3.zip"
      };
      $.ajax({
        url: '/AJAX/Delete_Update_File/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Release_Update').click(function(){
      var req_data = {
        'ENV_KEY':'TEST_170',
        'fileName': "update.tar"
      };
      $.ajax({
        url: '/AJAX/Release_Update/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Test_User_Login').click(function(){
      var req_data = {
        'name': 'admin',
        'password': 'admin'
      }
      $.ajax({
        url: '/AJAX/Request_User_Login/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#upload_file').click(function(){
      var ENV_KEY = "TEST_170"
      var Url = '/AJAX/Upload_File/' + ENV_KEY;

      var name = $("#file_upload").val();
      console.log ('name: ' + name)
      var formData = new FormData();
      formData.append("file",$("#file_upload")[0].files[0]);
      formData.append("name",name);

      var file = document.getElementById('file_upload').files[0];
      if (file) {
        console.log (file.size)
      }
      $.ajax({
        url : Url,
        type : 'POST',
        cache: false,
        data : formData,
        processData : false,   // 告诉jQuery不要去处理发送的数据
        contentType : false,   // 告诉jQuery不要去设置Content-Type请求头
        dataType: 'json',
        beforeSend:function(){
          // console.log("正在进行，请稍候");
        },
        success : function(responseStr) {
          console.log (responseStr)
        },
        error : function(responseStr) {
          console.log("error");
        }
      });
    })

    $('#update_srv').click(function(){
      var formData = new FormData();
      formData.append("file",$("#file_update")[0].files[0]);

      var ENV_KEY = "TEST_170"
      var exec_time = $('#exec_time').val();
      if (isNaN(exec_time)) {
        console.log (exec_time)
        exec_time = 1;
      } else {
        console.log ('是数字');
      }
      var Url = '/AJAX/Update_Srv/' + ENV_KEY + '/' + exec_time;
      console.log ('exec_time: ' + exec_time)
      var file = document.getElementById('file_update').files[0];
      if (file) {
        console.log ('fileSize: ' + file.size)
      }
      $.ajax({
        url : Url,
        type : 'POST',
        cache: false,
        data : formData,
        processData : false,   // 告诉jQuery不要去处理发送的数据
        contentType : false,   // 告诉jQuery不要去设置Content-Type请求头
        dataType: 'json',
        beforeSend:function(){
          // console.log("正在进行，请稍候");
        },
        success : function(responseStr) {
          console.log (responseStr)
        },
        error : function(responseStr) {
          console.log("error");
        }
      });
    })

    $('#Release_Update_Complete').click(function(){
      var formData = new FormData();
      formData.append("file",$("#release_update_complete_file")[0].files[0]);

      var exec_time = $('#release_exec_time').val();
      if (isNaN(exec_time)) {
        console.log (exec_time)
        exec_time = 1;
      } else {
        console.log ('是数字');
      }
      var ENV_KEY = "TEST_170"
      var Url = '/AJAX/Release_Update_Complete/' + ENV_KEY + '/' + exec_time;

      var file = document.getElementById('release_update_complete_file').files[0];
      if (file) {
        console.log ('fileSize: ' + file.size)
      }

      $.ajax({
        url : Url,
        type : 'POST',
        cache: false,
        data : formData,
        processData : false,   // 告诉jQuery不要去处理发送的数据
        contentType : false,   // 告诉jQuery不要去设置Content-Type请求头
        dataType: 'json',
        beforeSend:function(){
          // console.log("正在进行，请稍候");
        },
        success : function(responseStr) {
          console.log (responseStr)
        },
        error : function(responseStr) {
          console.log("error");
        }
      });
    })

    $('#Download_File').click(function(){

      var req_data = {
        'ENV_KEY':'TEST_170',
        // 'fileName' : '/home/test/console/down1.txt'
        'fileName': 'server/0.0.4/monagent/bin/monagent.xml'
      }
      $.ajax({
        url: '/AJAX/Download_File/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Set_ENV_KEY').click(function(){
      var ENV_KEY = 'PTEST_170'
      // var ENV_KEY = 'TEST_170'
      $.ajax({
        url: '/AJAX/Set_ENV_KEY/',
        data: {'env_key_value': ENV_KEY},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    });

    $('#Request_Task_Rpc').click(function(){
        var req_data = {
          'type': 'version_control',
          '--cmd': 'show',
          '--args':'',
          '--grp': '',
          '--ctr': '',
          '--srv': '',
          '--srvno': '',
          '--ictr': '',
          '--isrv': '',
          '--isrvno': ''
        };

      // req_data = {
      //   '--cmd': 'deployServer',
      //   // '--cmd': 'undeployServer',
      //   // '--cmd': 'deployConsole',
      //   // '--cmd': 'undeployConsole',
      //   '--args':'',
      //   '--grp': '',
      //   '--ctr': '',
      //   '--srv': '',
      //   '--srvno': '',
      //   '--ictr': '',
      //   '--isrv': '',
      //   '--isrvno': '',
      // }

      $.ajax({
        url: '/AJAX/Request_Task_Rpc/',
        data: {'req_json': JSON.stringify(req_data)},
        dataType: 'json',
        type: 'POST',
        traditional: true,
        success: function (responseJSON) {
            console.log (responseJSON)
        }
      });
    })

    $('#Request_All_SrvStatus').click(function(){
        $.getJSON('/AJAX/Request_All_SrvStatus/',function(rsp_result){
            console.log (rsp_result)
            // $('#Request_All_TaskList_Rsp').append(rsp_result.twz + '<br>');
        })
    })

    $('#Request_All_TaskList').click(function(){
        $.getJSON('/AJAX/Request_All_TaskList/',function(rsp_result){
            console.log (rsp_result)
            // $('#Request_All_TaskList_Rsp').append(rsp_result.twz + '<br>');
        })
    })

    $('#Request_All_TaskResult').click(function(){
        $.getJSON('/AJAX/Request_All_TaskResult/',function(rsp_result){
            console.log (rsp_result)
            // $('#Request_All_TaskResult_Rsp').append(rsp_result.twz + '<br>');
        })
    })

    $('#Request_All_Version').click(function(){
        var req_data = {
          'ENV_KEY':'TEST_170'
        };
        $.ajax({
          url: '/AJAX/Request_All_Version/',
          data: {'req_json': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
          }
        });
    })

    $('#Set_DB_Data').click(function(){
        $.getJSON('/AJAX/Set_DB_Data/',function(rsp_result){
            console.log (rsp_result)
        });
    })

    $('#Get_DB_Data').click(function(){
        $.getJSON('/AJAX/Get_DB_Data/',function(rsp_result){
            console.log (rsp_result)
        });
    })
})

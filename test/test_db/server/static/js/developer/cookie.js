//设置cookie
function setCookie (name, value, iDay) {
  console.log ('setCookie！')
    var cookieString = name + "=" + escape(value);
    // 判断是否设置过期时间
    if(iDay > 0) {
      var oDate=new Date();
      oDate.setDate(oDate.getDate()+iDay);
      cookieString = cookieString + ';expires=' + oDate;
    }
    document.cookie = cookieString;
}
//获取cookie  返回名称为 name的cookie值，如果不存在则返回空
function getCookie (name) {
    console.log ('getCookie！')
    var arr=document.cookie.split('; ');
    var i=0;
    console.log(arr)
    for(i=0;i<arr.length;i++) {
        var arr2=arr[i].split('=');
        if(arr2[0]==name) {
            return unescape(arr2[1]);
        }
    }
    return '';
}
//删除指定名称的cookie,
function removeCookie (name) {
    setCookie(name, '1', -1);
}

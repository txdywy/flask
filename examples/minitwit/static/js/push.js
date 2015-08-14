// 请换成自己的 appId 和 appKey
//var appId = '9dv47dhduhueccd39x88xjrjgjdnisgitca50s5rsj53ipzc';
//var appKey = 'nkgmov89jtzm78bxow1644j7zqdfys67s7r83p2iid3b7ws2';
var push;

// 每次调用生成一个聊天实例
createNew();

function createNew() {
    push = AV.push({
        appId: appId,
        appKey: appKey
    });

    // 可以链式调用
    push.open(function() {
        showLog('可以接收推送');
        //showLogPN('欢迎')
    });

    // 监听推送消息
    push.on('message', function(data) {
        showLog('message');
        showLog(JSON.stringify(data));
    });

    // receive 方法是监听 message 的快捷方法
    push.receive(function(data) {
        showLog('Receive 方法显示和监听 message 事件一致');
        showLog(JSON.stringify(data));
    });

    // 监听网络异常
    push.on('reuse', function() {
        showLog('网络中断正在重试');
    });

    // 发送一条推送
    /*
    push.send({
        // channels: ['aaa'],
        data: {LeanCloud: 123}
    }, function(result) {
        if (result) {
            showLog('推送成功发送');
        } else {
            showLog('error');
        }
    });

    push.subscribe(['test123'], function(data) {
        showLog('关注新的频道');
    });

    push.send({
        channels: ['test123'],
        data: {test123: 123}
    });

    setTimeout(function() {
        
        // 如果不加 channels，可以简单的使用 send 方法发送一个 json
        push.send({
            abc: 123
        });

        push.unsubscribe(['test123'], function(data) {
            showLog('取消关注新的频道');

            push.send({
                channels: ['test123'],
                data: {test123: 123}
            });
        });

    }, 5000);
    */
}

function showLog(msg) {
    console.log(msg);
}



function showLogPN(msg) {
    console.log(msg);
    /*  
    var div = document.getElementById('result');
    var p = document.createElement('p');
    p.innerText = msg;
    div.appendChild(p);
    */
    $(function(){
        new PNotify({
            title: 'Regular Notice',
            text: msg, 
            delay: 1000
        }); 
    }); 
}


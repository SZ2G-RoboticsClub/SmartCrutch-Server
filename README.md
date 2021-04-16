# SmartCrutch-Server

SmartCrutch-v4 Server Repo

## Demoboard Api Document
掌控版Api文档

### /demoboard/heartbeat

#### Description
拐杖心跳包，每隔**5秒**发送一次

#### Request
- uuid: 拐杖uuid
- status: 拐杖状态码:
    - 'ok': 正常
    - 'emergency': 摔倒
    - 'error': 错误
    - ~~ 'offline': 离线，**内部使用，不可通过Api设置** ~~
- loc: *可选项*，位置经纬度数据
    - latitude: 经度
    - longitude: 纬度

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 拐杖未注册
- msg: 返回值信息

### /demoboard/get_settings/{uuid}

#### Description
获取拐杖设置信息
在拐杖启动时请求，若uuid不存在则自动注册

#### Request
- uuid: 拐杖uuid

#### Response
- code: 返回值:
    - 0: 成功
- msg: 返回值信息
- settings: 设置信息
    - home_loc: *可选项*，家庭地址
        - latitude: 经度
        - longitude: 纬度
    - phone: *可选项*，电话号码
    - password: *可选项*，App登录密码
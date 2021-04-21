# SmartCrutch-Server

SmartCrutch-v4 Server Repo

## Demoboard Api
掌控板Api

### Heartbeat

- url: `/demoboard/heartbeat`
- method: `post`

#### Description
拐杖心跳包，每隔**5秒**发送一次

#### Request
- uuid: 拐杖uuid
- status: 拐杖状态码:
    - 'ok': 正常
    - 'emergency': 摔倒
    - 'error': 错误
    - 'offline': 离线，**内部使用，不可通过Api设置**
- loc: *可选项*，位置经纬度数据
    - latitude: 纬度
    - longitude: 经度

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 拐杖未注册
- msg: 返回值信息

### Get Settings

- url: `/demoboard/get_settings/{uuid}`
- method: `get`

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
    - phone: *可选项*，电话号码
    - password: *可选项*，App登录密码
  

## App Api
Android App Api

### Bind

- url: `/app/bind`
- method: `post`

#### Description
绑定拐杖到App账号，App注册时调用

#### Request
- uuid: 拐杖uuid
- username: 用户名，不可为空
- password: 密码，不可为空

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 拐杖uuid未注册
    - 2: 拐杖uuid已绑定账号
    - 3: 密码不可为空
    - 4: 用户名不可为空
    - 5: 用户名已使用
- msg: 返回值信息

### Login

- url: `/app/login`
- method: `post`

#### Description
获取拐杖uuid，App登录时调用

#### Request
- username: 用户名，不可为空
- password: 密码，不可为空

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 用户名不存在
    - 2: 密码错误
- msg: 返回值信息

### Update Settings

- url: `/app/update_settings`
- method: `post`

#### Description
设置信息，保存设置时调用

#### Request
- uuid: 拐杖uuid
- settings: 拐杖设置信息
    - phone: *可选项*，电话号码
    - password: App登录密码，不可为空

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 无效的uuid
    - 2: 密码不可为空
- msg: 返回值信息

### Get Settings

- url: `/app/get_settings/{uuid}`
- method: `get`

#### Description
获取拐杖设置信息，类似 `demoboard/get_settings`，但uuid不存在不会自动注册

#### Request
- uuid: 拐杖uuid

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 无效的uuid
- msg: 返回值信息
- settings: 设置信息
    - phone: *可选项*，电话号码
    - password: App登录密码

### Get Status

- url: `/app/get_status/{uuid}`
- method: `get`

#### Description
获取拐杖状态信息

#### Request
- uuid: 拐杖uuid

#### Response
- code: 返回值:
    - 0: 成功
    - 1: 无效的uuid
- msg: 返回值信息
- status: 拐杖状态码
    - 'ok': 正常
    - 'emergency': 摔倒
    - 'error': 错误
    - 'offline': 离线
- loc: 拐杖位置信息
    - latitude: 纬度
    - longitude: 经度
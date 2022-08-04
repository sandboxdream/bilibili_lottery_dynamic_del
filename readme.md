# b站抽奖动态删除
特点:
    
- 自动识别是否已经开奖
- 只删除已经开奖的动态
- 详细的提示
- 遍历所有动态
## 使用方法
下载python 
   
从github克隆本仓库
```git
git clone https://github.com/sandboxdream/bilibili_lottery_dynamic_del.git
```

将`config_template.json`重命名为`config.json`

在config.json中修改配置:

uid填写为b站uid(纯数字)

bili_jct和SESSDATA为cookie内容，打开b站网页，切换到network选项卡，点开第一个`www.bilibili.com`，在request headers中的cookie中找到SESSDATA和bili_jct
将这两段复制进双引号中(注意只复制等号后面到分号前面）

如果bili_jct或SESSDATA任意一个没有填写，则将自动进入登录选项

del_all配置表示是否执行全部动态删除模式。0表示关闭，1表示开启。
如果开启全部删除模式，将不进行判断直接删除所有的动态

运行main.py
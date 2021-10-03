# b站抽奖动态删除
特点:
    
- 自动识别是否已经开奖
- 只删除已经开奖的动态
- 详细的提示
- 自动向下翻页到最底部
## 使用方法
下载python 
   
从github克隆本仓库
```git
git clone https://github.com/sandboxdream/bilibili_lottery_dynamic_del.git
```

在config.json中修改配置:

uid填写为b站uid(纯数字)

_uuid和SESSDATA为cookie内容，打开b站网页，切换到network选项卡，点开第一个`www.bilibili.com`，在request headers中的cookie中找到uuid和SESSDATA
将这两段复制进双引号中(注意复制_uuid时别复制到;了）

运行main.py
# 淘宝弹幕抓取

-app.py #入口文件(服务调用)
-filterLogin #弹幕抓取文件
-requestFn #接口文件
-requirements.txt #依赖文件
-output.log 日志文件
-dist 打包文件
# 步骤
1 pip install requirements.txt
2 pyinstaller -F --noconsole app.py 或者 pyinstaller app.py
3 打开dist文件夹中exe文件 
4 输入直播间id（项目中的）
5 开始抓取
6 点击×关闭抓取
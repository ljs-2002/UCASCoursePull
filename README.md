# UCAS Course Pull

中国科学院大学本科课程评价快速填写脚本，用于快速填写各个科目的课程评价。

**声明：本脚本只是为了减轻同学们在填写课程评价时的重复劳动，请积极地为各个课程提出你的建议，帮助学校改善教学质量！！！**

## 安装依赖

- 本脚本依赖于`browser_cookie3`库，请使用下列语句安装：

  ```shell
  python -m pip install browser-cookie3
  ```



## 使用方法

- 首先使用**edge**浏览器登陆一次课程评价网站；
- 接着运行`CoursePull.py`文件，即可一次性完成当前所有科目的评价。
- 在`release`中有打包好的exe文件，可以在没有python环境的情况下直接运行。



## 说明

- 本脚本默认所有单选题选择第一个，所有多选题选择前三个，文字简答题的默认回答在`defaultAnswer.ini`中配置。
- 不使用**edge**浏览器的用户可以自行修改`CoursePull.py`中获取`Cookie`和解析出`Admin-Token`的部分，以适配你的设备。



## 注意

- **课后平均投入学习时间**将被设置为“**超过4小时**”，但形势与政策等课程如此回答显然不合理，请注意修改；
- **本课程让你在以下哪些方面受益**将被设置为“**学术知识，专业技能，学术伦理**”，但形势与政策等课程如此回答显然不合理，请注意修改；
- “**你对本课程的助教老师工作的评价**”将被设置为`defaultAnswer.ini`中配置的默认回答，若未修改则为“**助教老师工作认真负责**”，但无助教的课程如此回答显然不合理，请注意修改；
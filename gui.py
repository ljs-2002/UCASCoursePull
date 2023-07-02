from tkinter import Tk,Button,Label,Text,Scrollbar,NORMAL,DISABLED,END
from typing import Union
from requests.exceptions import ConnectionError, ProxyError
from datetime import datetime
from CoursePull import get_term, get_course_list, post_course_pull

def run():
    # 运行你的代码逻辑，可以在此处添加你的代码
    try:
        term_id = get_term()
        id_dict_list = get_course_list(term_id)
        total,post = post_course_pull(id_dict_list)
        return [f"总共{total}门课程，其中{post}门课程未被填写",f"填写完成，填写了{post}门课程"]
    except ConnectionError as e:
        if(isinstance(e,ProxyError)):
            return "代理错误，请检查代理设置或关闭代理后重试"
        else:
            return "网络连接错误，请检查网络连接"
    except Exception as e:
        return str(e.args[0])

def do_update_textbox(message: Union[str, list[str]],color = "black"):
    if isinstance(message, str):
        message = [message]
    for m in message:
        textbox.config(state=NORMAL)  # 将文本框设置为可编辑状态
        current_time = datetime.now().strftime("%H:%M:%S")  # 获取当前时间
        textbox.insert(END, f"[{current_time}] {m}\n",color)  # 在文本框中插入新的文本
        textbox.config(state=DISABLED)  # 将文本框设置为只读状态

def update_textbox():
    do_update_textbox("正在填写...")
    # 在这里调用你的 run() 函数
    result = run()
    # 若返回值为字符串，则说明出现了错误，用红色显示
    if isinstance(result, list):
        color = "blue"
    else:
        color = "red"
    do_update_textbox(result,color)

# 创建主窗口
window = Tk()
# 设置窗口标题
window.title("课程评价填写")
# 设置窗口大小
window.geometry("500x300")

# 创建按钮
button = Button(window, text="开始填写", command=update_textbox)
button.grid(row=0, column=0, pady=5)  # 使用grid布局管理器并设置pady参数

# 创建文本框
textbox = Text(window, height=10, width=50)
textbox.grid(row=2, column=0, sticky="nsew")  # 使用grid布局管理器并设置sticky参数

textbox.tag_config("red", foreground="red")
textbox.tag_config("black", foreground="black")
textbox.tag_config("blue", foreground="blue")

do_update_textbox("就绪.")
do_update_textbox("请先访问一次课程评价系统, 确保cookie有效!!!",color="red")
do_update_textbox("Github地址: https://github.com/ljs-2002/UCASCoursePull",color="blue")
do_update_textbox("在使用过程中发现bug欢迎提出issue或者PR.")
do_update_textbox("在访问完课程评价系统后, 请点击按钮开始填写.")

# 创建滚动条
scrollbar = Scrollbar(window, command=textbox.yview)
scrollbar.grid(row=2, column=1, sticky="ns")  # 使用grid布局管理器并设置sticky参数

# 配置滚动条与文本框的关联
textbox.configure(yscrollcommand=scrollbar.set)

# 设置窗口部件随窗口大小变化而调整大小
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.iconbitmap("favicon.ico")

# 进入主循环
window.mainloop()
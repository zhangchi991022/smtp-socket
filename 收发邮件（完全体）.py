# -*- coding:utf-8 -*-
# Author: CHi Zhang
# 前半部分作为server端接收邮件
# 后半部分作为client端发送邮件
from socket import *
import sys
import time
import datetime
import re
import base64
import ssl


# 写文件函数，保存发送信息：发送时间，发送方，发送信息，接收方
def save_to_file(where_file, contents):
    save_file = open(where_file, 'w')
    save_file.write(contents)
    save_file.close()


# 开始server端的socket
s = socket()
if (s):
    print("server端socket对象创建成功")
else:
    print("创建对象失败。。。")
    s.close()
    sys.exit(0)

# 本地主机名和端口
host = "127.0.0.1"
# port = 465
port = 25

# 绑定端口号
s.bind((host, port))
# 设置等待监听连接数
s.listen(5)

# 建立客户端链接 链接会返回一个新的套接字,并返回连接成功的提示信息
try:
    new_socket, address = s.accept()
    # print("111")
    # server - cilent之间新socket包装
    # new_socket = ssl.wrap_socket(new_socket, server_side=True,certfile="cert.pem", keyfile="key.pem",ssl_version=ssl.PROTOCOL_SSLV23)
    # print("222")
    new_socket.settimeout(10)

    # 返回信息，一定要在尾部加上\r\n不然它不读入，坑死你
    post_msg = ('220 beta.gov Simple Mail Transfer Service ready\r\n')
    print("post_msg=", post_msg)
    new_socket.send(post_msg.encode('utf-8'))
except:
    print("socket connection error. Try again.")
    new_socket.close()
    sys.exit(0)

# 回复对EHLO的250 OK
try:
    helo = new_socket.recv(1024)
    print("get_data= ", helo)
    post_msg = ("250 OK\r\n")
    print("post_msg= ", post_msg)
    new_socket.send(post_msg.encode('utf-8'))
except:
    print('EHLO error. Try again.')
    new_socket.close()
    sys.exit(0)

# 接收它的MAIL FROM<...>,回复250 OK 要有对邮箱字符串的格式检查
mailfrom = new_socket.recv(1024)
mailfrom = str(mailfrom)
print("get_data:", mailfrom)
name_of_mailfrom = mailfrom.replace("b'MAIL FROM: <", "")
name_of_mailfrom = name_of_mailfrom.replace('>\\r\\n\'', '')

print("name_of_mailfrom:", name_of_mailfrom)
mailfrom_check = re.match(r'(^[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*(\.[a-z]{2,})$)',
                          name_of_mailfrom)
if not mailfrom_check:
    mailfrom_error = "550 There's something wrong with your 'mailfrom' name, PLEASE CHECK AGAIN!\r\n"
    new_socket.send(mailfrom_error.encode('utf-8'))
    new_socket.close()
    sys.exit(0)
else:
    post_msg = ("250 OK\r\n")
    print("post_msg= ", post_msg)
    new_socket.send(post_msg.encode('utf-8'))
    username = name_of_mailfrom

# RCPT_TO部分，同样回复250 OK，这里不检查了，因为真正发给谁在后面控制
rcpt_to = []
boolean = True

# 可能多个收件地址
while boolean:
    receipt = new_socket.recv(1024)
    receipt = str(receipt)
    print("get_data=:", receipt)
    # print("receipt[:10]:",receipt[:10])
    if (receipt[:10] == "b'RCPT TO:"):
        name_of_receipt = receipt.replace("b'RCPT TO: <", "")
        name_of_receipt = name_of_receipt.replace('>\\r\\n\'', '')

        print("name_of_receipt:", name_of_receipt)
        post_msg = ("250 OK\r\n")
        rcpt_to.append(name_of_receipt)
        print("post_msg= ", post_msg)
        new_socket.send(post_msg.encode('utf-8'))
    else:
        boolean = False
        continue

# print("len(rcpt_to)",len(rcpt_to))
# 检查收件地址
for i in range(len(rcpt_to)):
    receipt_check = re.match(r'(^[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*(\.[a-z]{2,})$)',
                             rcpt_to[i])
    if not receipt_check:
        print(i + 1, "号邮件地址存在问题")
        rcpt_error = "550  There's something wrong with your 'rcpt_to' name, PLEASE CHECK AGAIN!\r\n"
        new_socket.send(rcpt_error.encode('utf-8'))
        new_socket.close()
        sys.exit(0)

# print("收件地址无问题")
# 接收DATA命令 由于上面循环，已经接受了DATA命令
try:
    # datacmd = new_socket.recv(1024)
    # print("datacmd= ",datacmd)
    post_msg = ('354 Start mail input; end with <CRLF>.<CRLF>\r\n')
    print("post_msg= ", post_msg)
    new_socket.send(post_msg.encode('utf-8'))
except:
    print('DATA error. Try again.')
    new_socket.close()
    sys.exit(0)

# 接收包的计数器
count = 0
# 对错标志
flag = True
# 用于存储foxmail发送的信息的缓存列表
savetext = []
while flag:
    # 接受消息，知道包的长度小于1024了，说明为最后一个包，且由于第一个包一定为配置信息，且不满1024，所以不能考虑他
    # new_socket.settimeout(5)
    try:
        data = new_socket.recv(1024)
        # 收到数据加入列表中
        savetext.append(str(data))
        count += 1
        print("get_data= ", data, "\n")
        print("len_data= ", len(data), "\n")
        # print("count= ",count)
    except:
        continue

    if (len(data) < 1024 and count >= 2):
        post_msg = ("250 OK\r\n")
        print("post_msg= ", post_msg)
        new_socket.send(post_msg.encode('utf-8'))

        quitCmd = new_socket.recv(1024)
        print("quit_get_data= ", quitCmd)
        post_msg = ("221 Bye\r\n")
        # new_socket.send(post_msg.encode('utf-8'))
        flag = False
        break

# server接收数据结束
print("server端结束\n")

# 处理数据，取出邮件信息。制造log文件内容
TEXT = ''.join(savetext)
# print(TEXT)

# 抠出来Sunject
list_subject = re.findall(r"Subject:(.+?)\\r\\n", TEXT)
Subject = ''.join(list_subject)
Subject = Subject.replace(" =?gb2312?B?", '')
Subject = Subject.replace(" =?GB2312?B?", '')
Subject = Subject.replace("?=", '')
print("Subject1:", Subject)
try:
    Subject = base64.b64decode(bytes(Subject, 'gb2312'))
    Subject = Subject.decode('gb2312', 'replace')
except:
    print("Subject2:", Subject)
print("Subject3:", Subject)
# 取出base64下的邮件信息并放在list_content列表里
list_content = re.findall(r"base64\\r\\n\\r\\n(.+?)\\r\\n\\r\\n", TEXT)
# print("list_contest=",type(list_content))
content = ''.join(list_content)
# 将content中的'\r\n'和可能有的开头bytes标志: b' 去掉
content = content.replace("\\r\\n", '')
content = content.replace("b'", '')
print("content=", content, '\n')
# content解码
content = base64.b64decode(bytes(content, 'gb2312'))
content = content.decode('gb2312', 'replace')
print("content=", str(content))

# 发送的邮件信息：msg
msg = "\r\n" + str(content)
print("msg== ", msg)

# client端开始
# username = input("登录邮箱，输入用户名: ")
password = input("请输入邮箱密码: ")
print(rcpt_to)
# 发送列表：
# rcpt_to = ['1399553430@qq.com','@qq.com','dyfsbdhhh@163.com','littlelighter@163.com']

# 循环发送
for i in range(len(rcpt_to)):
    # 创建socket
    try:
        mail_server = 'smtp.163.com'  # 使用的发件服务器
        client_socket = socket()  # 创建socket对象
        # 给客户端socket ssl包装
        # sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # client_socket = sslcontext.wrap_socket(client_socket)
        # client_socket = ssl.wrap_socket(client_socket, server_side=True,certfile="cert.pem", keyfile="key.pem",ssl_version=ssl.PROTOCOL_SSLV23)
        client_socket.connect((mail_server, port))  # 连接服务器
        recv1 = client_socket.recv(1024)
        print("get_connect_recv1= ", recv1, '\n')
    except:
        print('client_socket.connect error. Try again.')
        client_socket.close()
        sys.exit(0)

    # 发送EHLO开始，返回服务器响应
    try:
        hello_command = 'EHLO localhost\r\n'  # 输入命令需要\r
        client_socket.send(hello_command.encode())
        recv1 = client_socket.recv(1024)  # 接受邮件服务器的回复
        print("get_ehlo_recv1= ", recv1, '\n')
    except:
        print('client_socket_ehlo_error. Try again.')
        client_socket.close()
        sys.exit(0)

    # 用户登录并接受响应
    try:
        username_b64 = base64.b64encode(bytes(username, 'utf-8'))  # username的base64格式，需要先转化为字节形式
        username_b64_str = username_b64.decode('utf-8')
        usernameCommand = 'AUTH LOGIN {0}\r\n'.format(username_b64_str)
        client_socket.send(usernameCommand.encode())  # 发送命令
        recv1 = client_socket.recv(1024)
        print("get_username_recv1= ", recv1, '\n')

        password_b64 = base64.b64encode(bytes(password, 'utf-8'))
        password_b64_str = password_b64.decode('utf-8')
        passCommand = password_b64_str + '\r\n'
        client_socket.send(passCommand.encode())  # 默认encode()为utf-8
        recv1 = client_socket.recv(1024)
        print("get_password_recv1= ", recv1, '\n')
    except:
        print('client_socket_password_error. Try again.')
        client_socket.close()
        sys.exit(0)

    # 发送邮件发送端和服务器响应
    try:
        mailAdd = 'MAIL FROM: <{0}>\r\n'.format(username)
        client_socket.send(mailAdd.encode())
        recv1 = client_socket.recv(1024)
        print("get_mail_from_recv1= ", recv1, '\n')
    except:
        print('client_socket_MAIL_FROM_error: Please check Try again.')
        client_socket.close()
        sys.exit(0)

    # 邮件接收端和服务器响应
    try:
        print("这是第", i + 1, "个邮箱：", rcpt_to[i], '\n')
        rcptAdd = 'RCPT TO: <{0}> \r\n'.format(rcpt_to[i])
        client_socket.send(rcptAdd.encode())
        recv1 = client_socket.recv(1024)
        print("get_rcpt_to_recv1= ", recv1, '\n')
    except:
        print('client_socket_RCPT_TO_error. Try again.')
        client_socket.close()
        sys.exit(0)

    # 日志文件内容编辑：
    # 现在时间,类型为字符串
    now_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    log_text = time.asctime(time.localtime(time.time())) + "\n\n这是一个邮件发送记录日志\n\n"
    log_text = log_text + "发件人： " + username + "\n\n"
    log_text = log_text + "收件人： " + rcpt_to[i] + "\n\n"
    log_text = log_text + "邮件内容：\n" + msg
    filename = filename = "Log_Down_" + now_time
    # 调用函数
    # save_to_file('C:/Users/lenovo/Desktop/socket smtp/text/' +filename +'.txt', log_text)
    save_to_file('C:\\Users\\FireFly\\Desktop\\History\\socket smtp\\text\\' + filename + '.txt', log_text)
    # 输入DATA命令行
    try:
        dataCommand = 'DATA\r\n'
        client_socket.send(dataCommand.encode())
        recv1 = client_socket.recv(1024)
        print("get_data_recv1= ", recv1, '\n')

        # 输入From数据
        From = username
        From = "From:" + From + "\r\n"
        client_socket.send(From.encode())
        # 输入To数据
        To = rcpt_to[i]
        To = "To:" + To + "\r\n"
        client_socket.send(To.encode())
        # 输入subject数据
        Subject = "Subject:" + Subject + "\r\n"
        client_socket.send(Subject.encode())

        # 发送主体信息
        print("要发送信息了，msg= ", msg)
        client_socket.send(msg.encode())

        # 命令行中尾部回车，输入'.'并回车来结束
        endmsg = "\r\n.\r\n"
        client_socket.send(endmsg.encode())

        # 输入退出命令
        quitCommand = 'QUIT\r\n'
        client_socket.send(quitCommand.encode())
        recv1 = client_socket.recv(1024)
        print("get_quit_recv1= ", recv1, '\n')
    except:
        print('client_socket_DATA||QUIT_error. Try again.')
        client_socket.close()
        sys.exit(0)

    client_socket.close()

new_socket.close()
s.close()
print("Complete!", '\n')

# smtp-socket
# 一． 项目内容：

使用Socket API编写一个SMTP邮件服务器程序，该程序使用SMTP接收来自邮件客户端（如 foxmail、outlook）的邮件，并使用SMTP转发到实际的接收邮件服务器的用户邮箱（如@163.com、@bupt.edu.cn等）。

# 二． SMTP程序的基本功能：

1.作为SMTP服务器，接收邮件客户端程序的TCP连接请求，接收SMTP命令和邮件数据，将邮件保存在文件中；

2.作为SMTP客户端，建立到实际邮件服务器的TCP连接，发送SMTP命令，将保存的邮件发送给实际邮件服务器；

3.提供邮件差错报告：将实际邮件服务器的差错报告转发给邮件客户端软件；

4.支持一封邮件多个接收者，要求接收者属于不同的域（bupt.edu.cn、163.com、qq.com,…）；

5.提供发件人和收件人 Email 地址格式检查功能，例如下列邮件地址是错误的：chengli，chengli@，bupt.edu.cn ……

6.支持 SSL 安全连接功能

# 三． 实验环境：

使用Python3.8编写程序，使用Foxmail7.2发送邮件。

# 四． 交互过程：

作为服务端：建立socket，与邮件客户端建立SMTP连接，从报文中截取发件内容、主题、发件人、抄送人并将数据暂存，结束连接。

作为客户端：建立socket，与用户邮箱服务端建立SMTP连接，将内容循环发送给多个收件人，记录日志存入本地，结束连接。

**1.运行程序，建立socket套接字，完成服务端初始化，等待客户端发送请求。**
![image](https://github.com/zhangchi991022/smtp-socket/blob/main/image/2.PNG)
**2.打开Foxmail，更改Foxmail发件服务器为本机，给本地服务器发送邮件。**
![image](https://github.com/zhangchi991022/smtp-socket/blob/main/image/1.PNG)
**3.在Foxmail中给另一个邮箱（QQ邮箱）发送邮件**
![image](https://github.com/zhangchi991022/smtp-socket/blob/main/image/3.PNG)
**4.在Python shell可以看到作为服务端对Foxmail客户端请求的处理和作为客户端对目标邮件服务器的请求。**
![image](https://github.com/zhangchi991022/smtp-socket/blob/main/image/4.png)










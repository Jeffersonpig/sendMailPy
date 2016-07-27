#sendmail.ini
------------
###config section:

 `global`

###config fields:

* `sender_config`: 发送邮件服务器与用户的配置文件
* `target_csv`: 保存收件人地址的csv文件
* `mail_subject`: 邮件标题
* `mail_text`: 保存邮件正文文字内容的txt文件
* `mail_attach`: 邮件附件的文件名

###config example:

	[global]
	mail_subject=A Hello Mail
	mail_text=content.txt
	mail_attach=
	csv_file=maillist.csv
	sender_config=senders.ini



#sender配置
------
###config section:
section名相互不同即可，每个section都会被当作一个发送者

###config fields:

* `server_type`: 邮件服务器的类型（其实没啥卵用，只是为了做类型表示）
* `server_host`: 邮件服务器的地址
* `server_port`: 邮件服务器的端口
* `server_auth`: 邮件服务器的认证类型，TLS或NONE
* `sender_addr`: 发送者的email地址，用于用户登录
* `sender_passwd`: 发送者的用户登录密码
* `day_max`: 该发送者单日发送的最大邮件数（暂未实现）

###config example
	[sender_gmail]
	server_type=@gmail.com
	server_host=smtp.gmail.com
	server_port=587
	server_auth=TLS
	sender_addr=someuser@gmail.com
	sender_passwd=userpassword
	day_max=500



#failed.log
---
发送失败的收件人地址会被记录到脚本同目录下failed.log文件中，并标注记录的时间和本次发送失败的收件人数量。
# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

#需要配置分割线 ===================================================================
# 项目配置
project_name = "HyCurrency" #工程名
scheme = "HyCurrency" #scheme
project_type = "-workspace" #工程类型 pod工程 -workspace 普通工程 -project
configuration = "Release" #编译模式 Debug,Release

# git路径配置
git_login_needPassword = 1
git_name = "yuzhongrui"
git_password = "yuzhongrui.com"
git_remote_init_addr = "http://dev.esongbai.xyz/git/AppTeam/ForexIos.git"

# fir
fir_api_token = "3c5adeb462f62ff7dd7d8c2c904a533a" # firm的api token
download_address = "http://fir.im/etonghui" #firm 下载地址

#邮件配置
app_name = "易通汇" #App名
from_name = "余忠瑞"
from_addr = "1101287926@qq.com"
password = "ahwzaqpiugmibaad"
smtp_server = "smtp.qq.com"
to_addr = ['1101287926@qq.com','598005481@qq.com','1194127720@qq.com']

#需要配置分割线 ===================================================================

#拼接仓库地址  git clone http://账号:地址@dev.esongbai.xyz/git/AppTeam/ForexIos.git
def git_remote_addr():
    remote_addr = git_remote_init_addr
    git_password_account = git_name + ":" + git_password + "@"
    if git_login_needPassword:
        # 不包含https
        if remote_addr.find("https://") != -1:
            print "http"
            https = "https://" + git_password_account
            remote_addr = remote_addr.replace("https://",https)
        else :
            print "https"
            http = "http://" + git_password_account
            remote_addr = remote_addr.replace("http://",http)  
    print remote_addr
    return remote_addr
            
# 获取git仓库中的最新代码
def update_project():
    if os.path.exists(git_local_addr()):
        print "从远程仓库中下拉代码"
        os.system("cd %s;git reset --hard;git pull"%git_local_addr())
    else :
        os.system("mkdir %s"%git_local_addr)
        print "git clone 远程仓库"
        os.system ('git clone %s %s'%(git_remote_addr(),git_local_addr())) 

# 获取工程目录
def get_projectPath():
    local_project_path = git_local_addr() + "/" + project_name
    return local_project_path

# 本地仓库clone地址

def git_local_addr():
    git_local = os.getcwd() + "/pack_iOS";
    return git_local

# 清理项目
def clean_project():
    print("** 开始打包 **")
    os.system('cd %s;xcodebuild clean' % get_projectPath()) # clean 项目

# archive项目
def build_project():
    os.system('cd %s;mkdir build' % get_projectPath())
    if project_type == "-workspace" :
        project_suffix_name = "xcworkspace"
    else :
        project_suffix_name = "xcodeproj"
    os.system ('cd %s;xcodebuild archive %s %s.%s -scheme %s -configuration %s -archivePath %s/build/%s || exit' % (get_projectPath(),project_type,project_name,project_suffix_name,scheme,configuration,get_projectPath(),project_name))

# 导出ipa包到自动打包程序所在目录
def exportArchive_ipa():
    global ipa_filename
    ipa_filename = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    ipa_filename = project_name + "_" + ipa_filename;
    os.system ('%s/xcodebuild-safe.sh -exportArchive -archivePath %s/build/%s.xcarchive -exportPath %s/%s -exportOptionsPlist %s/exportOptionsPlist.plist ' %(os.getcwd(),get_projectPath(),project_name,os.getcwd(),ipa_filename,os.getcwd()))

# 删除build目录
def rm_project_build():
    os.system('rm -r %s/build' % get_projectPath())

# 上传fim
def upload_fir():
    result = False
    if os.path.exists("%s/%s" % (os.getcwd(),ipa_filename)):
        # 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
        result = True
        ret = os.system("fir publish '%s/%s/%s.ipa' --token='%s'" % (os.getcwd(),ipa_filename,project_name,fir_api_token))
    else:
        print("没有找到ipa文件")
    return result

# 地址格式化
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发邮件
def send_mail():
    msg = MIMEText(app_name + "iOS有新版本更新，请前往 " + download_address + " 下载测试！如有问题，请联系iOS相关人员或者直接将问题提至禅道，我们会及时解决，谢谢", 'plain', 'utf-8')
    
    msg['From'] = _format_addr('%s''<%s>' % (from_name,from_addr))
    msg['To'] = ",".join(_format_addr('%s' % to_addr))
    msg['Subject'] = Header(app_name + "iOS客户端自动打包程序 打包于:" + time.strftime('%Y年%m月%d日%H:%M:%S',time.localtime(time.time())), 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr,to_addr, msg.as_string())
    server.quit()

# 输出包信息
def ipa_info():
    os.system('fir info %s/%s/%s.ipa' % (os.getcwd(),ipa_filename,project_name))
    print("** 打包结束 **")

def main():
    # 获取项目
    update_project()
    # 清理并创建build目录
    clean_project()
    # 编译目录
    build_project()
    # 导出ipa到机器人所在目录
    exportArchive_ipa()
    # 删除build目录
    rm_project_build()
    # 上传fir
    if upload_fir():
        # 发邮件
        send_mail()
    #输出包信息
    ipa_info()

# 执行
main()

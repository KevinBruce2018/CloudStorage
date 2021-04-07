from django.http import HttpResponse,JsonResponse
from django.http.response import FileResponse
from django.shortcuts import redirect, render
from testapp.models import FileMessage, Log,User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.middleware.csrf import get_token
from django.conf import settings
from . import tools
import hashlib
import os

def getCaptcha(request):
    value,code_str = tools.getVcode()
    request.session['vcode'] = code_str.lower()
    res =  HttpResponse(value,content_type='img/png')
    res['Content-Disposition'] = "attachment; filename=vcode.png"
    return res
def getToken(request):
    token = get_token(request)
    return JsonResponse({'csrfmiddlewaretoken':token})
def index(request):
    return render(request,'index.html')

def login(request):
    data = {'msg':'','result':'fail','code':''}
    if request.method=="GET":
        data['msg'] = 'Method not allowed'
        data['code'] = '101'
        return JsonResponse(data)
    
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    vcode = request.POST.get('vcode','').lower()
    timestamp = request.POST.get('timestamp','')
    sign = request.POST.get('sign','')

    if vcode=='' or request.session.get('vcode','')!=vcode:
        data['msg'] = 'vcode error'
        data['code'] = '102'
    elif username=='' or password=='' or timestamp=='' or sign=='':
        data['msg'] = 'items empty'
        data['code'] = '103'
    elif not tools.checkSign(username,password,vcode,sign,timestamp):
        data['msg'] = 'sign error'
        data['code'] = '104'
    else:
        password = hashlib.sha256((password+settings.SALT).encode()).hexdigest()
        lists = User.objects.filter(username=username,password=password)
        if lists and lists[0].status==1:
            data['code'] = '100'
            data['msg'] = 'success'
            data['result'] = 'success'
            request.session['login'] = '1'
            request.session['username'] = username
        elif lists and lists[0].status!=1:
            data['code'] = '105'
            data['msg'] = 'user locked'
        else:
            data['msg'] = 'username or password error'
            data['code'] = '106'
    res = JsonResponse(data)
    request.session.pop('vcode','')
    if data['code']=='100':
        log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status="正常",operation='登录',result='成功',source='登录'
        )
        log.save()
    else:
        status = data['msg']
        result = '失败'
        if not username:
            username = request.META.get('REMOTE_ADDR')
        log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                status=status,operation='登录',result=result,source='登录'
        )
        log.save()
    return res

def registor(request):
    if request.method=='POST':
        data = {'result':'fail','code':'','msg':''}
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        repeatpass = request.POST.get('repeatpass','')
        vcode = request.POST.get('vcode','').lower()
        email = request.POST.get('email','')
        
        if vcode=='' or request.session.get('vcode','')!=vcode:
            data['code'] = '101'
            data['msg'] = 'vcode error'
        elif username=='' or password=='' or repeatpass=='' or email=='':
            data['code'] = '102'
            data['msg'] = 'items empty'
        elif not tools.checkUsername(username):
            data['code'] = '103'
            data['msg'] = 'username illegal'
        elif not tools.checkPassword(password):
            data['code'] = '104'
            data['msg'] = 'password illegal'
        elif not tools.checkEmail(email):
            data['code'] = '105'
            data['msg'] = 'email illegal'
        elif password!=repeatpass:
            data['code'] = '106'
            data['msg'] = 'password inconsistency'
        else:
            lists = User.objects.filter(username=username)
            if lists:
                data['code'] = '107'
                data['msg'] = 'user exists'
            else:
                tools.sendActivateMail(username,email)
                password = hashlib.sha256((password+settings.SALT).encode()).hexdigest()
                u = User(username=username,password=password,status=3,authority=3)
                u.save()
                data['code'] = '100'
                data['msg'] = 'success'
                data['result'] = 'success'
                log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status="正常",operation='注册',result='成功',source='注册'
                )
                log.save()
        res =  JsonResponse(data)
        request.session.pop('vcode','')
        return res
    else:
        return render(request,'reg.html')
        
def activate(request):
    if token:=request.GET.get('token'):
        user = tools.check_verify_email_token(token)
        if user!=None:
            User.objects.filter(username=user).update(status=1)
            log = Log(username=user,ip_address=request.META.get('REMOTE_ADDR'),
                status='成功',operation='激活',result='成功',source='激活'
            )
            log.save()
            return HttpResponse('success')
        else:
            username = request.META.get('REMOTE_ADDR')
            log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                status='username empty',operation='激活',result='失败',source='激活'
            )
            log.save()
            return HttpResponse('fail')
    return HttpResponse('fail')

def logout(request):
    if request.COOKIES.get('sessionid'):
        request.session.flush()
    return HttpResponse('ok')
def upload(request):
    if request.session.get('login')!='1':
        return redirect(index)
    
    if request.method=='POST':
        files = request.FILES.get('file')
        username = request.session.get('username')
        user_dir = os.path.join(settings.BASE_DIR,'uploads',hashlib.md5(username.encode()).hexdigest())
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
        key = request.POST.get('key')
        iv = request.POST.get('key2')
        hashcode = request.POST.get('hash')
        if not key or not iv or not hashcode:
            return JsonResponse({'result':'fail','code':'101','msg':'empty items'})
        if files:
            name = files.name
            content = files.read()
            files.close()
            path = os.path.join(settings.BASE_DIR,'uploads',user_dir,name)
            if os.path.exists(path):
                return JsonResponse({'result':'fail','code':'102','msg':'file exists'})
            
            if len(name)>128:
                return JsonResponse({'result':'fail','code':'103','msg':'filename too long'})
            #可以修改密文索引 方便密文的检索
            f = FileMessage(name=name,size=files.size,auther=username,
                secret_key_one = key,secret_key_two=iv,secret_index='aaa',
                hashcode=hashcode,path=path
            )
            f.save()
            with open(path,'wb') as f:
                f.write(content)
            log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status="成功",operation='上传',result='成功',source=path
            )
            log.save()
        return JsonResponse({'result':'success','code':'100','msg':'success'})
    else:
        log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="成功",operation='上传',result='成功',source='none'
        )
        log.save()
        return render(request,'upload.html')

def download(request):
    if request.session.get('login')!='1':
        return redirect(index)
    
    name = request.GET.get('filename')
    lists = FileMessage.objects.filter(name=name,auther=request.session.get('username','NULL'))[0]
    if lists and os.path.exists(lists.path):
        path = lists.path
        f = open(path,'rb')
        #res = HttpResponse(content,content_type='img/png')
        response = FileResponse(f,filename=name,as_attachment=True)
        
        response['Content-Type'] = 'application/octet-stream'
        #f.close()
        #如何response的时候也发一个状态码过去
        log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="正常",operation='下载',result='成功',source=path
        )
        log.save()
        return response
    
    else:
        #需要改进一下啊
        log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="fail",operation='下载',result='失败',source=name
        )
        log.save()
        return JsonResponse({'result':'fail','code':'101','msg':'fail'})

def delete(request):
    if request.session.get('login')!='1':
        return HttpResponse(status=403)
    if request.GET.get('filename'):
        filename = request.GET.get('filename')
        #没有的话会不会抛出异常 果然会抛异常 晚上在改这个异常吧
        lists = FileMessage.objects.filter(name=filename,auther=request.session.get('username','NULL'))[0]
        if lists:
            path = lists.path
            if os.path.exists(path):
                os.remove(path)
            files = FileMessage.objects.filter(path=path)
            files.delete()
            log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="成功",operation='删除',result='成功',source=path
            )
            log.save()
            return HttpResponse('ok')
        else:
            log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="成功",operation='删除',result='成功',source='node'
            )
            log.save()
            return HttpResponse('no file exists')
    else:
        return HttpResponse('no filename')
def getkey(request):
    if request.session.get('login')=='1' and request.GET.get('file'):
        name = request.GET.get('file')
        lists = FileMessage.objects.filter(auther=request.session.get('username'),name=name)
        if lists:
            data =  {"key":lists[0].secret_key_one,"key2":lists[0].secret_key_two}
            log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="成功",operation='获取密钥',result='成功',source='密钥'
            )
            log.save()
            return JsonResponse(data)
        else:
            log = Log(username=request.session.get('username'),ip_address=request.META.get('REMOTE_ADDR'),
                    status="no file",operation='获取密钥',result='失败',source='密钥'
            )
            log.save()
            return JsonResponse({"msg":"no file"})
    else:
        return redirect(index)

def fileList(request):
    username = request.session.get('username')
    operation = '获取用户'
    result = '失败'
    status = '成功'
    source = '/filelist'
    data = {"files":[]}
    if username:
        lists = FileMessage.objects.filter(auther=username)
        for f in lists:
            data['files'].append([f.name,f.size,f.date])
        res = JsonResponse(data)
        result = '成功'
    else:
        status = 'user not login'
        res =  HttpResponse(status=403)
    log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                status=status,operation=operation,result=result,source=source
        )
    log.save()
    return res

def share(request):
    if request.session.get('login')!='1':
        return HttpResponse(status=403)
    username = request.session.get('username')
    filename = request.GET.get('filename')
    if not filename:
        return HttpResponse(status=403)
    data = {'username': username, 'filename': filename}
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    token = serializer.dumps(data).decode()
    return HttpResponse(token)

def delUser(request):
    if request.method!='POST':
        return HttpResponse(status=403)
    username = request.session.get('username')
    operation = '删除账号'
    result = '失败'
    status = '成功'
    source = '/deluser'
    user = request.POST.get('user')
    if request.session.get('username') and User.objects.filter(username=username,authority=1):
        if user_exists := User.objects.filter(username=user):
            user_exists.delete()
            files = FileMessage.objects.filter(auther=user)
            for f in files:
                path = f.path
                os.remove(path)
            files.delete()
            res =  JsonResponse({'msg':'ok'})
            result = '成功'
        else:
            status = 'permission denied'
            res = JsonResponse({'msg':'permission denied'})
        log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                status=status,operation=operation,result=result,source=source
        )
        log.save()
        return res
    return HttpResponse(status=403)

def lockUser(request):
    username = request.session.get('username')
    operation = '封号'
    result = '失败'
    status = '成功'
    source = '/lockuser'
    if request.method!='POST':
        return HttpResponse(status=403)
    user = request.POST.get('user')
    if request.session.get('login')=='1' and username:
        if user_exists := User.objects.filter(username=user):
            if User.objects.filter(username=username,authority=1):
                user_exists.update(status=5)
                res =  JsonResponse({'msg':'ok'})
                result = '成功'
            else:
                res =  JsonResponse({'msg':'permission denied'})
                status = 'permission denied'
        else:
            res =  JsonResponse({'msg':'permission denied'})
            status = 'permission denied'
        log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status=status,operation=operation,result=result,source=source
            )
        log.save()
        return res

    return HttpResponse(status=403)

def unlockuser(request):
    username = request.session.get('username')
    operation = '账户解封'
    result = '失败'
    status = '成功'
    source = '/unlockuser'
    if request.method!='POST':
        return HttpResponse(status=403)
    user = request.POST.get('user')
    if request.session.get('login')=='1' and username:
        if user_exists := User.objects.filter(username=user):
            if User.objects.filter(username=username,authority=1):
                user_exists.update(status=1)
                res =  JsonResponse({'msg':'ok'})
                result = '成功'
            else:
                res =  JsonResponse({'msg':'permission denied'})
                status = 'permission denied'
        else:
            res =  JsonResponse({'msg':'permission denied'})
            status = 'permission denied'
        log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status=status,operation=operation,result=result,source=source
            )
        log.save()
        return res

    return HttpResponse(status=403)

def userList(request):
    username = request.session.get('username')
    operation = '获取用户'
    result = '失败'
    status = '成功'
    source = '/userlist'
    if username:
        lists = User.objects.filter(username=username,authority=1)
        if not lists:
            status = 'permission denied'
        else:
            result = '成功'
            lists = User.objects.all()
            data = {"users":[]}
            for f in lists:
                data['users'].append([f.username,f.status,f.authority])
        res =  JsonResponse(data)
    else:
        status = 'user not login'
        username = request.META.get('REMOTE_ADDR')
        res =  HttpResponse(status=403)
    log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status=status,operation=operation,result=result,source=source
            )
    log.save()
    return res

#返回权限数字
def getAuthority(request):
    username = request.session.get('username')
    operation = '获取权限'
    result = '失败'
    status = '成功'
    source = '/getauthority'
    if not username:
        status = 'user not login'
        username = request.META.get('REMOTE_ADDR')
        res =  HttpResponse(status=403)
    else:
        results = User.objects.filter(username=username)
        if not results:
            status = 'user not exists'
            res =  HttpResponse('-1')
        else:
            result = '成功'
            res =  HttpResponse(results[0].authority)
    log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status=status,operation=operation,result=result,source=source
            )
    log.save()
    return res

def getLogList(request):
    username = request.session.get('username')
    operation = '获取日志'
    result = '失败'
    status = '成功'
    source = '/loglist'
    if not username:
        status = 'user not login'
        username = request.META.get('REMOTE_ADDR')
        res =  HttpResponse(status=403)
    else:
        data = {'logs':[]}
        lists = User.objects.filter(username=username,authority=2)
        if not lists:
            status = 'permission denied'
        else:
            logs = Log.objects.all()
            for log in logs:
                data['logs'].append([log.time,log.ip_address,log.username,
                    log.source,log.operation,log.status,log.result])
            result = '成功'
            status = '成功'
        res =  JsonResponse(data)
    log = Log(username=username,ip_address=request.META.get('REMOTE_ADDR'),
                    status=status,operation=operation,result=result,source=source
            )
    log.save()
    return res
    
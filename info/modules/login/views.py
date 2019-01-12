import datetime
import random

from flask import request, jsonify, current_app, make_response, session, g, redirect, render_template
from info import redis_store, db
from info.commen import login_required
from info.libs.yuntongxun import sms
from info.models import User, Area
from info.utils import constants
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
import re
from . import login_blue


@login_blue.route('/api/v1.0/imagecode')
def generate_image_code():
    cur = request.args.get('cur')
    if not cur:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    name, text, image = captcha.generate_captcha()
    try:
        redis_store.setex('ImageCode_' + cur, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    else:
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response



@login_blue.route('/api/v1.0/smscode',methods=['POST'])
def sendSMSCode():
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    if not re.match(r'1[3456789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式不正确')
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取数据失败')
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='数据已失效')
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')
    try:
        user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
    else:
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号码已经注册')
    sms_code = '%06d' % random.randint(0, 999999)
    print(sms_code)
    try:
        redis_store.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据已失效')
    # 使用云通讯发送短信
    try:
        ccp = sms.CCP()
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    if result == 0:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')


@login_blue.route('/api/v1.0/user',methods=['POST'])
def register():
    mobile = request.json.get('mobile')
    phonecode = request.json.get('phonecode')
    password = request.json.get('password')
    if not all([mobile, phonecode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机格式错误')
    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取数据错误')
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')
    if real_sms_code != str(phonecode):
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')
    user = User()
    user.mobile = mobile
    user.name = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['name'] = mobile
    print('1')
    return jsonify(errno=RET.OK, errmsg='OK')



@login_blue.route('/api/v1.0/session',methods=['POST'])
def login():
    mobile=request.json.get('mobile')
    password=request.json.get('password')
    if not all([mobile,password]):
        return jsonify(errno=RET.NODATA,errmsg='该用户不存在')
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.DATAERR,errmsg='手机号码格式错误')
    try:
        user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.errror(e)
        return jsonify(errno=RET.DBERR,errmsg='数据查询失败')
    if not user:
        return jsonify(errno=RET.NODATA,errmsg='该用户不存在')
    try:
        user=User.query.filter(User.mobile==mobile).first()
        print(user.password_hash)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据查询失败')

    if not user or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    session['mobile'] = user.mobile
    print(session['mobile'])
    session['user_id'] = user.id
    print(session['user_id'])
    session['name'] = user.mobile
    return jsonify(errno=RET.OK, errmsg='OK')

# 状态保持
@login_blue.route('/api/v1.0/session')
@login_required
def user_info():
    user=g.user
    print(user)
    if not user:
        return redirect('/static/html/index.html')
    data={
        "name": user.name,
        "user_id": user.id
        }
    # print(data['user'])
    return jsonify(errno=RET.OK,errmsg='OK',data=data)







# 退出
@login_blue.route('/api/v1.0/session',methods=['DELETE'])
def logout():
    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('name',None)
    return jsonify(errno='0',errmsg='OK')


# http://127.0.0.1:5000/static/favicon.ico
@login_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


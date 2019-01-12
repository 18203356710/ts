from flask import request, jsonify, g, current_app, redirect
import re
from info import db
from info.commen import login_required
from info.models import User
from info.utils.response_code import RET
from . import user_blue
from info.utils import constants
from info.utils.image_storage import storage


# 获取个人信息
@user_blue.route('/api/v1.0/user')
@login_required
def info():
    id=g.user.id
    try:
        user=User.query.filter_by(id=id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据查询失败')
    if not user:
        return jsonify(errno=RET.NODATA,errmsg='该用户不存在')
    data={
        "avatar_url": constants.QINIU_DOMIN_PREFIX + user.avatar_url if user.avatar_url else "",
        "mobile": user.mobile,
        "name": user.name
        }
    return jsonify(errno= 0,errmsg='OK',data=data)


# 修改姓名
@user_blue.route('/api/v1.0/user/name',methods=['POST'])
@login_required
def m_name():
    name=request.json.get('name')
    id=g.user.id
    print(id)
    try:
        user=User.query.filter(User.id==id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据查询失败')
    user.name=name
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg='数据保存失败')
    g.name=name
    return jsonify(errno=0,errmsg='OK')


@user_blue.route('/api/v1.0/user/avatar',methods=['POST'])
@login_required
def save_avatar():
    user = g.user
    if not user:
        return redirect('/static/html/index.html')
    if request.method == 'GET':
        data = {
            'avatar_url': user.avatar_url
        }
        return jsonify(errno=RET.OK,errmsg='OK',data=data)
    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    image_data = avatar.read()
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传图片失败')
    user.avatar_url = image_name
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存图片数据失败')
    avatar_url = constants.QINIU_DOMIN_PREFIX + user.avatar_url if user.avatar_url else ""
    data = {
        'avatar_url':avatar_url
    }
    return jsonify(errno=RET.OK,errmsg='OK',data=data)


# 获取实名信息
# @user_blue.route('/api/v1.0/user/auth')
# @login_required
# def real_info():
#     id = g.user.id
#     try:
#         user=User.query.filter_by(id=id).first()
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR,errmsg='数据查询失败')
#     if not user:
#         return jsonify(errno=RET.NODATA,errmsg='该用户不存在')
#     data ={
#         "real_name": user.real_name,
#         "id_card": user.id_card
#     }
#     return jsonify(errno=0, errmsg='OK', data=data)
@user_blue.route('/api/v1.0/user/auth',methods=['GET','POST'])
@login_required
def acquire_auth():
    user = g.user
    if request.method == 'GET':
        data = {
            'real_name':user.real_name,
            'id_card':user.id_card
        }
        return jsonify(errno=RET.OK,errmsg='OK',data=data)
    real_name = request.json.get('real_name')
    id_card = request.json.get('id_card')
    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    if not re.match(r'^[\u4e00-\u9fa5]+(·[\u4e00-\u9fa5]+)*$',real_name):
        return jsonify(errno=RET.PARAMERR,errmsg='姓名格式错误')
    if not re.match(r'^[1-9]\d{5}(19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$',id_card):
        return jsonify(errno=RET.PARAMERR,errmsg='身份证格式错误')
    if user.real_name or user.id_card:
        return jsonify(errno=RET.DATAEXIST,errmsg='数据已存在')
    user.real_name = real_name
    user.id_card = id_card
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存信息失败')
    return jsonify(errno=RET.OK,errmsg='OK')


# 设置实名信息
@user_blue.route('/api/v1.0/user/auth',methods=['POST'])
@login_required
def mreal_info():
    id = g.user.id
    real_name = request.json.get('real_name')
    id_card = request.json.get('id_card')
    try:
        user=User.query.filter_by(id=id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据查询失败')
    if not user:
        return jsonify(errno=RET.NODATA,errmsg='该用户不存在')
    user=User()
    user.real_name=real_name
    user.id_card=id_card
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据保存失败')
    return jsonify(errno=0, errmsg='OK')



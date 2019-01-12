# 导入蓝图
from info.commen import login_required
from . import order_blue

from flask import g, current_app, request, jsonify
from info.utils.response_code import RET
from info.models import House, Order
from info import db
import datetime


# 添加订单
# url:/api/v1.0/orders
@order_blue.route("/api/v1.0/orders", methods=['POST'])
@login_required
def add_order():
    """
    1.检查是否登录　
    2.判断请求方法是否为post
    3.获取参数house_id, start_date, end_date
    4.检查参数的完整性
    5.根据房屋id获取房屋信息
    6.获取创建订单/更新订单时间
    7.use_id,status
    8.将订单信息添加到订单数据表中
    9.返回结果
    :return:
    """
    # 下单
    user_id = g.user.id
    house_id = request.json.get('house_id')
    start_date_str = request.json.get('start_date')
    end_date_str = request.json.get('end_date')
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        assert start_date <= end_date
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='日期格式错误')
    try:
        house_id = int(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg='不能预定自己的房子')
    try:
        order = Order()
        order.user_id = user_id
        order.house_id = house.id
        order.begin_date = start_date
        order.end_date = end_date
        order.days = days
        order.house_price = house.price
        order.amount = order.house_price * order.days
        order.status = "WAIT_ACCEPT"
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='修改数据失败')
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存订单数据错误')
    data = {
               "order_id": order.id,
           }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


# 查询订单
# url:/api/v1.0/orders
@order_blue.route("/api/v1.0/orders", methods=['GET'])
@login_required
def find_order():
    """
    1.检查用户登录状态
    2.判断请求方法是否为get
    3.判断用户类型是否为custom
    4.通过user_id查询订单数据并按照创建时间排列
    5.返回结果
    """
    user_id = g.user.id
    role = request.args.get('role')
    if role not in ['custom', 'landlord']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数范围错误')
    if role == 'custom':
        try:
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.begin_date.desc())
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')
        if not orders:
            return jsonify(errno=RET.NODATA, errmsg='无订单数据')
        order_dict_list = []
        # try:
        for order in orders:
            print(order)
            order_dict_list.append(order.to_dict())

        data = {
            "orders": order_dict_list
        }
        return jsonify(errno=RET.OK, errmsg='OK', data=data)
    if role == 'landlord':
        try:
            houses = House.query.filter(House.user_id == user_id).all()
            house_ids = [house.id for house in houses]
            order = Order.query.filter(Order.house_id.in_(house_ids)).order_by(Order.create_time.desc()).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')
        if not order:
            return jsonify(errno=RET.NODATA, errmsg='无订单数据')
        order_dict_list = []
        try:
            for order_dict in order:
                order_dict_list.append(order_dict.to_dict())
                print(order_dict.status)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='储存订单数据失败')
        data = {
            "orders": order_dict_list
        }
        return jsonify(errno=0, errmsg='OK', data=data)


# 接单拒单
# url:/api/v1.0/orders
@order_blue.route("/api/v1.0/orders", methods=['PUT'])
@login_required
def accept_order():

    # 接单 拒单
    user_id = g.user.id


    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    action = req_data.get('action')
    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    order_id = req_data.get('order_id')
    # 判断参数的类型
    try:
        order_id = int(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数类型错误')

    try:
        #     根据订单号查询订单,并且要求订单处于等待接单状态
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='无法获取订单数据')

    # 确保房东只能修改属于自己的房子的订单
    if not order or house.user_id != user_id:
        return jsonify(errno=RET.REQERR, errmsg='操作无效')

    if action == "accept":
        order.status = "WAIT_COMMENT"
    elif action == "reject":
        #     拒单,要求用户传递拒单原因
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        order.status = 'REJECTED'
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='操作失败')
    return jsonify(errno=RET.OK, errmsg='OK')


# 订单评论
# url:/api/v1.0/orders/comment
@order_blue.route("/api/v1.0/orders/comment", methods=['PUT'])
@login_required
def order_comment():
    """
    1.检查登录
    2.获取参数
    3.检查参数完整性
    4.通过order_id查询订单
    5.写入评论
    6.提交数据库
    7.返回结果
    :return:
    """
    user_id = g.user.id
    comment = request.json.get('comment')
    order_id = request.json.get('order_id')
    if not all([comment, order_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    try:
        order_id = int(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == 'WAIT_COMMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单失败')
    if not order:
        return jsonify(errno=RET.DATAEXIST, errmsg='无订单数据')
    try:
        order.comment = comment
        order.status = 'COMPLETE'
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.SESSIONERR,errmsg='评论失败')
    # 保存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据库失败')
    return jsonify(errno=RET.OK,errmsg='OK')
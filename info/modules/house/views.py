
from info import db
from info.commen import login_required
from info.utils import constants
from . import house_blue
from flask import request, jsonify, current_app, redirect, g, session
from info.utils.response_code import RET
from info.models import House, Area, Facility, HouseImage, User
# 导入七牛云
from info.utils.image_storage import storage



# 3.1
@house_blue.route('/api/v1.0/user/houses')
def house_list():
    # 1、查询模型类获取全部数据
    # 2、判断数据是否存在
    # 3、遍历查询到的结果
    # 4、向前端返回数据

    try:
        alist_0 = House.query.all()

    except Exception as e:

        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询列表错误')
    # 判断结果是否正确
    if not alist_0:

        return jsonify(errno=RET.NODATA,errmsg='无列表数据')

    list_2 = []

    for list3 in alist_0:
        list_2.append(list3.to_basic_dict())

        data = list_2
        return jsonify(errno=RET.OK,errmsg='OK',data=data)


# 3.2
@house_blue.route('/api/v1.0/areas')
def area_houses_list():
    # 1、查询模型类获取全部数据
    # 2、判断数据是否存在
    # 3、遍历查询到的结果
    # 4、向前端返回数据

   #查询城区列表
    # 查询城区列表
    try:
        alist = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询城区列表失败')
    # 判断查询结果是否存在
    if not alist:
        return jsonify(errno=RET.NODATA, errmsg='无城区列表数据')

    # 遍历查询结果
    alist_l = []
    for al in alist:
        alist_l.append(al.to_dict())
    data = alist_l
    return jsonify(errno=RET.OK, errmsg='OK', data=data)



# 3.3
# @house_blue.route('/api/v1.0/houses',methods=['POST'])
# @login_required
# def new_house():
#     '''
#     如果是get请求,返回house页面
#     如果是post请求
#     1判断用户是否登录
#     发布房源
#         获取参数--检查参数--业务处理--返回数据
#     2获取参数
#     3、检查参数的完整性
#     4、转换数据类型
#     5、
#     6、构造模型类对象，保存房源数据
#     7、返回结果
#     :return:
#     '''
#     # 判断用户是否登录
#     user =g.user
#     # 获取参数,表单提交参数，使用request对象的form属性和files属性
#
#     # if request.method == 'GET':
#     #     return redirect('/api/v1.0/houses/index')
#     title = request.json.get('title')
#     price = request.json.get('price')
#     area_id = request.json.get('area_id')
#     address = request.json.get('address')
#     room_count = request.json.get('room_count')
#     acreage = request.json.get('acreage')
#     unit = request.json.get('unit')
#     beds = request.json.get('beds')
#     deposit = request.json.get('deposit')
#     min_days = request.json.get('min_days')
#     max_days = request.json.get('max_days')
#     facilities = request.json.get('facility')
#
#
#     # 检查参数完整性
#     if not all([title,price,area_id,address,room_count,acreage,unit,beds,deposit,min_days,max_days,facilities ]):
#         return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
#
#
#
#
# #     构造模型类对象,保存数据到数据库
#     new_house=House()
#     new_house.user_id =user.id
#     new_house.title = title
#     new_house.price = price
#     new_house.area_id= area_id
#     new_house.address = address
#     new_house.room_count = room_count
#     new_house.acreage = acreage
#     new_house.unit = unit
#     new_house.beds = beds
#     new_house.deposit = deposit
#     new_house.min_days = min_days
#     new_house.max_days = max_days
#
#     # 提交数据到mysql
#     try:
#         db.session.add(new_house)
#         db.session.commit()
#     except Exception as e:
#         current_app.logger.error(e)
#         db.session.rollback()
#         return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
#
#     data={
#         'house_id':new_house.id
#     }
#     print(data)
#
#     # 返回结果
#     return jsonify(errno=RET.OK, errmsg='OK',data=data)

@house_blue.route('/api/v1.0/houses',methods=['POST'])
@login_required
def new_house():
    '''
    如果是get请求,返回house页面
    如果是post请求
    1判断用户是否登录
    发布房源
        获取参数--检查参数--业务处理--返回数据
    2获取参数
    3、检查参数的完整性
    4、转换数据类型
    5、
    6、构造模型类对象，保存房源数据
    7、返回结果
    :return:
    '''
    # 判断用户是否登录
    user =g.user
    # 获取参数,表单提交参数，使用request对象的form属性和files属性

    # if request.method == 'GET':
    #     return redirect('/api/v1.0/houses/index')
    title = request.json.get('title')
    price = request.json.get('price')
    area_id = request.json.get('area_id')
    address = request.json.get('address')
    room_count = request.json.get('room_count')
    acreage = request.json.get('acreage')
    unit = request.json.get('unit')
    beds = request.json.get('beds')
    deposit = request.json.get('deposit')
    min_days = request.json.get('min_days')
    max_days = request.json.get('max_days')
    facilities = request.json.get('facility')


    # 检查参数完整性
    if not all([title,price,area_id,address,room_count,acreage,unit,beds,deposit,min_days,max_days,facilities ]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')




#     构造模型类对象,保存数据到数据库
    new_house=House()
    new_house.user_id =user.id
    new_house.title = title
    new_house.price = price
    new_house.area_id= area_id
    new_house.address = address
    new_house.room_count = room_count
    new_house.acreage = acreage
    new_house.unit = unit
    new_house.beds = beds
    new_house.deposit = deposit
    new_house.min_days = min_days
    new_house.max_days = max_days

    # 提交数据到mysql
    try:
        db.session.add(new_house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    data={
        'house_id':new_house.id
    }
    print(data)

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK',data=data)

# 3.4
@house_blue.route('/api/v1.0/houses/<int:house_id>/images',methods=['POST'])
@login_required
def push_images(house_id):
    '''
    判断是否登录
    判断房屋id
    获取参数,调用第三方软件,返回图片地址给前端


    :return:
    '''
    # user = g.user
    image_file = request.files.get('house_image')


    # 检查参数
    if not all([house_id,image_file]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺少')
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库失败")
    if house is None:
        return jsonify(errno=RET.DBERR, errmsg="没有房屋信息")
    # 读取图片数据
    try:
        house_image_data = image_file.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据读取错误')
    # 调用七牛云，获取七牛云返回的图片名称
    try:
        house_image_url = storage(house_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片异常')
    if not house.index_image_url:
        house.index_image_url = house_image_url
        db.session.add(house)

    # # 构造模型类对象,保存数据
    house_image = HouseImage()
    house_image.url = house_image_url
    house_image.house_id = house_id
    # # 保存图片地址到mysql数据库
    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存图片数据失败')

    # 拼接字符串 返回给前端
    url = constants.QINIU_DOMIN_PREFIX + house_image_url
    # 定义字典数据
    data = {
        'url': url
    }
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


# 3.5
@house_blue.route('/api/v1.0/houses/<int:house_id>')

def houses_detail(house_id):

    user_id = session.get('user_id')

    user = None
    if user_id:
        try:
            user = User.query.filter_by(id=user_id).first()

        except Exception as e:

            current_app.logger.error(e)
            user = None

            return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')

    #根据房屋id取出房屋数据,查询房屋所有者信息
    try:
        house = House.query.get(house_id)
        house_owner = User.query.get(house.user.id)

    except Exception as e:

        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')

    # 构建返回数据
    data = {
        "house": {
            "acreage": house.acreage,
            "address": house.address,
            "beds": house.beds,
            "capacity": house.capacity,
            "comments": house.to_full_dict().get("comments"),
            "deposit": house.deposit,
            "facilities": house.to_full_dict().get("facilities"),
            "hid": house.id,
            "img_urls": house.to_full_dict().get("img_urls"),
            "max_days": house.max_days,
            "min_days": house.min_days,
            "price": house.price,
            "room_count": house.room_count,
            "title": house.title,
            "unit": house.unit,
            "user_avatar": house_owner.to_dict().get("avatar_url"),
            "user_id": house_owner.id,
            "user_name": house_owner.name
        },

        "user_id": user.id if user else -1

    }

    return jsonify(errno=RET.OK,errmsg = "OK",data=data)


# 3.6
@house_blue.route('/api/v1.0/houses/index')
@login_required
def recommend_houses():
    '''
    从数据库获取数据,拿到数据返回给前端

    :return:
    '''
    houses = House.query.order_by(House.order_count.desc()).limit(4)
    data =[]
    for house in houses:
        data.append(house.to_index_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=data)




# 3.7
# 导入蓝图文件
from . import house_blue
# 导入内置对象
from flask import request, current_app, jsonify
# 导入模型类
from info.models import House, Order
# 导入自定义状态码
from info.utils.response_code import RET
# 导入日期对象
from datetime import datetime, timedelta


@house_blue.route('/api/v1.0/houses')
def house_search():
    # ####房屋搜索思路####
    # 获取参数
    aid = request.args.get('aid', '')
    start_date = request.args.get('sd', '')
    end_date = request.args.get('ed', '')
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('p', '1')

    # 如果区域id不为空,转换数据类型
    try:
        if aid:
            aid = int(aid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='区域类型转换失败')

    # 转换时间类型
    try:
        # 把日期字符串，转成日期对象
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        # 把日期字符串，转成日期对象
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='日期类型转换失败')

    # 转换页数类型
    try:
        if page:
            page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='页码类型转换失败')

    # 判断sort_key的值
    if sort_key == 'booking':
        sort_key = House.order_count.desc()
    elif sort_key == 'price-inc':
        sort_key = House.price.asc()
    elif sort_key == 'new':
        sort_key = House.create_time.desc()
    else:
        sort_key = House.price.desc()

    # 根据条件查询数据
    try:
        # 查询全部房屋
        house = House.query
        # 实例化订单对象
        order = Order()
        # 判断是否传入aid,如果没有查询全部数据

        if aid:
            house = house.filter(House.area_id == aid)

        # 判断是否传入开始时间,如果没有,查询全部,如果存在,查询不在订单结束时间大于开始时间的状态不在已取消,已拒单的所有数据
        # (查询的房子的开始时间大于订单结束时间)
        if start_date:
            # 订单结束时间大于等于开始时间
            order_list = order.query.filter(Order.end_date >= start_date, Order.status.notin_(['CANCELED','REJECTED'])).all()
            # 查询房子不在订单列表中的数据
            house = house.filter(House.id.notin_([str(i.house_id) for i in order_list]))

        # 判断是否传入结束日期,如果没有,查询全部,如果存在,查询不在订单开始时间小于结束时间的状态不在已取消,已拒单的所有数据
        # (查询的房子的结束时间小于订单开始时间)
        if end_date:
            # 订单开始日期小于等于结束日期,并且状态不在已取消,已拒单
            order_list = order.query.filter(Order.begin_date <= end_date, Order.status.notin_(['CANCELED','REJECTED'])).all()
            # 查询房子不在订单列表中
            house = house.filter(House.id.notin_([str(i.house_id) for i in order_list]))

        # 判断是否传入日期区间,如果没有,查询全部,如果存在,查询时间区间不在订单的时间区间的状态不在已取消,已拒单的所有数据
        if start_date and end_date:
            # 查询订单在某一时间区间内,并且状态不在已取消,已拒单
            order_list = order.query.filter(Order.begin_date >= start_date, Order.end_date <= end_date,Order.status.notin_(['CANCELED', 'REJECTED'])).all()
            # 查询房子不在订单列表中
            house = house.filter(House.id.notin_([str(i.house_id) for i in order_list]))

        # 通过上述查询结果,对结果进行分页查询
        paginate = house.order_by(sort_key).paginate(page, 5, False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='查询数据失败')

    # 查出来是一个房屋对象列表
    houses = paginate.items
    # 查出数据总页数
    total_page = paginate.pages

    # 定义一个列表保存房屋数据
    house_list = []

    # 遍历房屋对象列表
    for house in houses:
        # 把每一个房屋信息添加到列表中
        house_list.append(house.to_basic_dict())

    data = {
        'houses': house_list,
        'total_page': total_page
    }

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='查询成功', data=data)


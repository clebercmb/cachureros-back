import os, datetime 
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_script import Manager 
from flask_migrate import Migrate, MigrateCommand
from models import db, Product, UserStore, Login, User, Department, Category, Size, ProductState, Cart, CartProduct, WeightUnit, Region, Follow, MessageType, MessageStatus, UserMessage, Order, OrderProduct, OrderStatus, PaymentOption
from flask_cors import CORS
from utils import APIException, generate_sitemap, allowed_file
from graphene import ObjectType, String, Schema
from sqlalchemy import event
from sqlalchemy.event import listen
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.url_map.strict_slashes = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = "./static"
ALLOWED_EXTENSIONS_IMGS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_FILES = {'pdf', 'png', 'jpg', 'jpeg'}
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = THIS_FOLDER + "\\static\\images\\"

app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

CORS(app)
jwt = JWTManager(app)
Migrate(app,db)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

products = []

# Login
@app.route('/login-all', methods=['GET'])
def getLoginAll():
    print("** getLogin **")
    logins = Login.query.all()
    loginsList = list(map( lambda login: login.serialize(), logins ))
    return jsonify(loginsList), 200

@app.route('/login', methods=['POST'])
def login():
    print("** getLogin **")
    print(request.json)    

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    print('email=', email, 'password=', password)

    login = Login.get_login_by_email(email)

    if not login:
        return jsonify({"msg":"Login not found"}), 404

    print('login=', login)

    expires = datetime.timedelta(days=3)

    data = {
        "access_token": create_access_token(identity=login.email, expires_delta=expires),
        "user": login.user.serialize_with_userStore()
    }

    print('login.data=', data)

    return jsonify({"success": "Log In succesfully!", "data": data}), 200

# User Messages
@app.route("/message", methods=['POST'])  
def saveUserMessage():
    print('***saveUserMessage***')
    print(request.json)    

    senderId = request.json.get('senderId',None)
    receiverId = request.json.get('receiverId',None)
    messageTypeId = request.json.get('messageTypeId',None)
    messageStatusId = request.json.get('messageStatusId',None)
    message = request.json.get('message',None)
    link = request.json.get('link',None)


    print('>>>>saveUserMessage>> senderId=', senderId, 'receiverId=', receiverId, 'messageTypeId=', messageTypeId, 'messageStatusId=', messageStatusId, 'message=', message, 'link=', link)

    if not senderId:
        return jsonify({"msg":"senderId is required"}), 422

    if not receiverId:
        return jsonify({"msg":"receiverId is required"}), 422

    if not messageTypeId:
        return jsonify({"msg":"messageTypeId is required"}), 422
    
    if not messageStatusId:
        return jsonify({"msg":"messageStatusId is required"}), 422
    
    if not message:
        return jsonify({"msg":"message is required"}), 422

    userMessage = UserMessage(senderId=senderId, receiverId=receiverId, messageTypeId=messageTypeId, messageStatusId=messageStatusId, message=message, link=link)

    userMessage.save()
    print('>>>>>userMessage.__dict__.keys()=', userMessage.__dict__.keys())

    return jsonify(userMessage.serialize()),201

@app.route("/message/<int:id>", methods=['DELETE'])  
def deleteUserMessage(id):
    print('***deleteUserMessage: id:', id)
    #print(request.json)    

    userMessage = UserMessage.getOneBy(id)

    if not userMessage:
        return jsonify({"msg":"Message {0} not found!".format(id)}), 404

    print('***>>deleteUserMessage=', userMessage.serialize())

    userMessage.delete()
    print('***>>deleteUserMessage (after delete)=', userMessage)

    user = userMessage.receiver
    print('###deleteUserMessage.user.senders=', user.senders)

    userMessagesList = list(map( lambda userMessage: userMessage.serialize(),  user.senders ))

    return jsonify(userMessagesList),200

@app.route("/message/<int:id>", methods=['GET'])  
def getUserMessage(id):
    print('***getUserMessage: id:', id)
    print(request.json)    

    userMessage = UserMessage.getOneBy(id)

    if not userMessage:
        return jsonify({"msg":"Message {0} not found!".format(id)}), 404

    print('***>>getUserMessage.userMessage=', userMessage.serialize())

    return jsonify(userMessage.serialize()),200


@app.route("/message/", methods=['GET'])  
def getAllUsersMessages():
    print('***getAllUsersMessages')
    print(request.json)    

    userMessages = UserMessage.getAll()

    print('***>>getAllUsersMessages.userMessages=', userMessages)

    userMessagesList = list(map( lambda userMessage: userMessage.serialize(), userMessages ))

    return jsonify(userMessagesList),200


@app.route("/user/<int:id>/message/", methods=['GET'])  
def getUserMessageByReceivedId(id):
    print('***getUserMessageByReceivedId: id:', id)
    print(request.json)    

    userMessages = UserMessage.getAllByReceivedId(id)

    print('getUserMessageByUseriD.userMessages=', userMessages)

    userMessagesList = list(map( lambda userMessage: userMessage.serialize(), userMessages ))

    return jsonify(userMessagesList),200


# Register New User
@app.route('/register', methods=['POST'])
def register():
    print("** register **")
    print(request.json)    

    name = request.json.get('name', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    print('>>>app.register>>', 'name=', name,'email=', email, 'password=', password)

    login = Login(email=email, password=password)
    login.save()

    user = User(name=name, loginId=login.id, photoUrl='user.png', active=True, birthDate=None, nationalId=None, phone=None, address=None)
    user.save()

    cart = Cart(userId=user.id)
    cart.save()

    userStore = UserStore(name=name, userId=user.id, regionId=None, bio='', url='', photoUrl='tendita.png')
    userStore.save()
    print('login=', login)

    expires = datetime.timedelta(days=3)

    data = {
        "access_token": create_access_token(identity=login.email, expires_delta=expires),
        "user": login.user.serialize_with_userStore()
    }

    print('login.data=', data)

    return jsonify({"success": "Log In succesfully!", "data": data}), 200


# User
@app.route('/user', methods=['GET'])
def getAllUsers():
    print("** getAllUsers **")
    users = User.query.all()
    usersList = list(map( lambda user: user.serialize(), users ))
    print('usersList=', usersList)
    return jsonify(usersList), 200

@app.route('/user/<int:id>', methods=['GET'])
def getUser(id):
    print("** getUser **")
    user = User.getOneById(id)
    print('>>>user=', user)

    print('>>>user.followeds=', user.getFolloweds())
    print('>>>user.followers=', user.getFollowers())

    if user:
        return jsonify(user.serialize()), 200
    else:
        return jsonify({"msg":"User not found"}), 404


@app.route('/user-follow', methods=['GET'])
def getUserFollow():
    print("** getUser **")
    users = User.query.all()
    usersList = list(map( lambda user: user.serialize_with_follow(), users ))
    print('usersList=', usersList)
    return jsonify(usersList), 200

@app.route('/user/<int:id>/followeds', methods=['GET'])
def getFolloweds(id):
    print("** getFolloweds **")
    followeds = User.get_followeds_by_id(id)
    usersList = list(map( lambda user: user.serialize(), followeds ))
    print('usersList=', usersList)
    return jsonify(usersList), 200

@app.route('/user/<int:id>/followers', methods=['GET'])
def getFollowers(id):
    print("** getFollowers **")
    followers = User.get_followers_by_id(id)
    usersList = list(map( lambda user: user.serialize(), followers ))
    print('usersList=', usersList)
    return jsonify(usersList), 200


@app.route("/user", methods=['POST'])  
def addUser():
    print('***addUser***')
    print(request.json)    

    name = request.json.get('name',None)
    loginId = request.json.get('loginId',None)

    print('name=', name, 'loginId', loginId)

    if not name:
        return jsonify({"msg":"user name is required"}), 422

    user = User()
    user.name = name
    user.loginId = loginId
    
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()),201

#User Store
@app.route('/user-store', methods=['GET'])
def getUserStore():
    print("** getUserStore.request.method===>" +  request.method)
    userStoreList = UserStore.getAllUserStores()
    return jsonify(userStoreList), 200


@app.route('/user-store/<string:url>', methods=['GET'])
def getUserStoreByUrl(url):
    print("** appy.getUserStoreByUrl(id).request.method===>" ,  request.method)
    userStore = UserStore.getOneUserStoreByUrl(url)
    print("** appy.getUserStoreByUrl.url=",url) 
    print("** appy.getUserStoreByUrl.userStore=",userStore) 

    if userStore:
        return jsonify(userStore.serialize_with_product()), 200
    else:
        return jsonify({"msg":"UserStore not found"}), 404

@app.route("/user-store", methods=['POST'])  
def addUserStoreId():
    print('***addUserStoreId***')
    data = request.json
    print(data)    

    name = request.json.get('name',None)
    userId = request.json.get('userId',None)
    regionId = request.json.get('regionId', None)
    bio = request.json.get('regionId', None)
    url = request.json.get('url', None)
    photoUrl = request.json.get('photoUrl', None)

    print('name=', name, 'userId=', userId)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    if not userId:
        return jsonify({"msg":"userId is required"}), 422

    if not regionId:
        return jsonify({"msg":"regionId is required"}), 422

    userStore = UserStore(name=name, userId=userId, regionId=regionId, bio=bio, url=url, photoUrl=photoUrl)
    #userStore.name = name
    #userStore.userId = userId
    #userStore.regionId = regionId
    
    userStore.save()

    return jsonify(userStore.serialize()),201

@app.route('/my-store/<int:id>', methods=['GET'])
def getUserStoreById(id):
    print("** appy.getUserStoreById(id).request.method===>" ,  request.method)
    print("** appy.getUserStoreById.id=",id) 
    userStore = UserStore.getOneUserStoreById(id)
    print("** appy.getUserStoreById.userStore=",userStore) 

    if userStore:
        return jsonify(userStore.serialize_with_product()), 200
    else:
        return jsonify({"msg":"UserStore not found"}), 404


@app.route('/my-store/<int:id>', methods=['PUT'])
def saveUserStoreById(id):
    print("** appy.saveUserStoreById(id).request.method===>" ,  request.method)
    print("** appy.saveUserStoreById(id).request===>" ,  request)
    print("** appy.saveUserStoreById(id).request.files===>" ,  request.files)

    print("** appy.saveUserStoreById.id=",id) 
    userStore = UserStore.getOneUserStoreById(id)

    if not userStore:
        return jsonify({"msg":"UserStore not found"}), 404

    print("** appy.saveUserStoreById.userStore=",userStore) 

    email = request.form.get("email", None)
    password = request.form.get("password", None)
    userName = request.form.get("userName", None)
    birthDate = request.form.get("birthDate", None)
    nationalId= request.form.get("nationalId", None)
    phone = request.form.get("phone", None)
    address = request.form.get("address", None)
    userStoreName = request.form.get("userStoreName", None)
    regionId = request.form.get("regionId", None)
    bio = request.form.get("bio", None)
    url = request.form.get("url", None)
    userStorePhotoUrl = request.form.get("userStorePhotoUrl", None)
    hasUserStorePhotoUrl = request.form.get("hasUserStorePhotoUrl") != 'false'
    userPhotoUrl = request.form.get("userPhoto", None)
    hasUserPhotoUrl = request.form.get("hasUserPhotoUrl") != 'false'

    print('>>>birthDate=', birthDate, type(birthDate))
    birthDateFormated= ''
    try:
        birthDateFormated = datetime.datetime.strptime(str(birthDate), '%d/%m/%Y').date()
    except ValueError as ve:
        print('########saveUserStoreById.invalid date:, ', ve)
        return jsonify({"msg":"invalid birthdate"}), 422

    birthDate = birthDateFormated

    print('<<<saveUserStoreById>>> email=', email, ', password=', password, ', userName=', userName, ', birthDate=', birthDate, ', nationalId=', nationalId, ', phone=', phone, ', userStoreName=', userStoreName, ', regionId=', regionId, ', bio=', bio, ', url=', url,  ', userStorePhotoUrl=', userStorePhotoUrl, userStorePhotoUrl == None, ', hasUserStorePhotoUrl=', hasUserStorePhotoUrl, ', userPhotoUrl=', userPhotoUrl, ', hasUserPhotoUrl=', hasUserPhotoUrl)

    if not userStore:
        return jsonify({"msg":"UserStore not found"}), 404

    if not request.form.get("email", None):
        return jsonify({"msg":"email is required"}), 422

    if not request.form.get("password", None):
        return jsonify({"msg":"password is required"}), 422

    if not request.form.get("userName", None):
        return jsonify({"msg":"userName is required"}), 422

    if not request.form.get("birthDate", None):
        return jsonify({"msg":"birthDate is required"}), 422

    if not request.form.get("nationalId", None):
        return jsonify({"msg":"nationalId is required"}), 422

    if not request.form.get("phone", None):
        return jsonify({"msg":"phone is required"}), 422

    if not request.form.get("address", None):
        return jsonify({"msg":"address is required"}), 422

    if not request.form.get("userStoreName", None):
        return jsonify({"msg":"userStoreName is required"}), 422

    if not request.form.get("regionId", None):
        return jsonify({"msg":"regionId is required"}), 422

    if not request.form.get("url", None):
        return jsonify({"msg":"url is required"}), 422


    userPhotoFileName = userStore.user.photoUrl
    if hasUserPhotoUrl: 
        print('>>&&&&&-hasUserPhotoUrl')

        if 'userPhotoUrl' not in request.files:
            return jsonify({"msg": "userPhoto is required"}), 400

        file = request.files['userPhotoUrl']
        print('>>>$$$ filename=', file.filename)
        if not (file and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMGS)):
            msg = "User photo image {0} not allowed!".format('userPhotoUrl')
            return jsonify({msg}), 400

        userPhotoFileName = saveImageFile(fileKey='userPhotoUrl', request=request, fileType="UserProfile", email=email)

    userStorePhotoFileName= userStore.photoUrl
    if hasUserStorePhotoUrl:
        print('>>&&&&&-hasUserStorePhotoUrl')

        if 'userStorePhotoUrl' not in request.files:
            return jsonify({"msg": "userStorePhotoUrl is required"}), 400

        if not isFileAllowed(fileKey='userStorePhotoUrl', request=request):
            msg = "UserStore photo image {0} not allowed!".format('userStorePhotoUrl')
            return jsonify({msg}), 400
        userStorePhotoFileName = saveImageFile(fileKey='userStorePhotoUrl', request=request, fileType="UserStore", email=email)

    login = Login.getOneById(userStore.user.login.id)
    login.email = email
    login.password = password
    login.update()

    user = User.getOneById(userStore.user.id)
    user.name = userName
    user.birthDate = birthDate
    user.nationalId = nationalId
    user.phone = phone
    user.address = address
    user.photoUrl = userPhotoFileName
    userStore.name = userStoreName
    userStore.regionId = regionId
    userStore.bio = bio
    userStore.url = url
    userStore.photoUrl = userStorePhotoFileName

    userStore.save()

    print('saveUserStoreById.userStore (after save):', userStore.serialize())
    return jsonify(userStore.serialize()),200


def isFileAllowed(fileKey, request):
    print('>>>>>>>isFileAllowed.fileKey=', fileKey)
    print('****isFileAllowed.request.files=', request.files[fileKey])
    file = request.files[fileKey]
    print('>>>>>>>isFileAllowed.file.filename=', file.filename)
    if not (file and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMGS)):
        return False
    return True


def saveImageFile(fileKey, request, fileType, email):
    print('>>>saveImageFile=>')
    
    file = request.files[fileKey]

    login = Login.query.filter_by(email=email).first()
    filename = secure_filename(file.filename)
    filename = fileKey+"_" + str(login.id) + "_" + filename
    print('saveImageFile.filename=',filename)
    print('saveImageFile.filename.os=',os.path.join(app.config['UPLOAD_FOLDER']+"/images"))
    
    file.save(os.path.join(IMAGES_FOLDER, filename))
    return filename



#Follower
@app.route('/followed/<int:id>', methods=['GET'])
def getFollowedByUserId(id):
    print("** getFollowedByUserId(id).request.method===>" ,  request.method)
    followed = Follow.getAllFollower()
    print("** getFollowedByUserId(id).followed=",followed) 

    #if userStore:
    #    return jsonify(userStore.serialize_with_product()), 200
    #else:
    #    return jsonify({"msg":"UserStore not found"}), 404

@app.route("/follower", methods=['POST'])  
def addFollower():
    print('***addFollower***')
    data = request.json
    print(data)    

    followerId = request.json.get('followerId',None)
    followedId = request.json.get('followedId',None)

    print('followerId=', followerId, 'followedId=', followedId)

    if not followerId:
        return jsonify({"msg":"followerId is required"}), 422

    if not followedId:
        return jsonify({"msg":"followedId is required"}), 422

    follow = Follow(followerId, followedId)
    
    follow.save()

    return jsonify(follow.serialize()),201


# Department
@app.route('/department', methods=['GET'])
def getDepartment():
    print("** getDepartment **")
    departments = Department.query.all()
    departmentsList = list(map( lambda department: department.serialize(), departments ))
    return jsonify(departmentsList), 200


@app.route("/department", methods=['POST'])  
def addDepartment():
    print('***addDepartment***')
    print(request.json)    

    name = request.json.get('name',None)

    print('name=', name)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    department = Department()
    department.name = name
    
    db.session.add(department)
    db.session.commit()
    return jsonify(department.serialize()),201

# Category
@app.route('/category', methods=['GET'])
def getCategory():
    print("** getCategrory **")
    categories = Category.query.all()
    categoriesList = list(map( lambda category: category.serialize(), categories ))
    return jsonify(categoriesList), 200


@app.route("/category", methods=['POST'])  
def addCategory():
    print('***addCategory***')
    print(request.json)    

    name = request.json.get('name',None)

    print('name=', name)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    category = Category()
    category.name = name
    
    db.session.add(category)
    db.session.commit()
    return jsonify(category.serialize()),201

# SubCategory
@app.route('/sub-category', methods=['GET'])
def getSubCategory():
    print("** getSubCategrory **")
    subCategories = SubCategory.query.all()
    subCategoriesList = list(map( lambda subCategory: subCategory.serialize(), subCategories ))
    return jsonify(subCategoriesList), 200


@app.route("/sub-category", methods=['POST'])  
def addSubCategory():
    print('***addSubCategory***')
    print(request.json)    

    name = request.json.get('name',None)
    categoryId = request.json.get('categoryId',None)

    print('name=', name, 'categoryId=', categoryId)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    if not categoryId:
        return jsonify({"msg":"categoryId is required"}), 422

    subCategory = SubCategory()
    subCategory.name = name
    subCategory.categoryId = categoryId
    
    db.session.add(subCategory)
    db.session.commit()
    return jsonify(subCategory.serialize()),201

# Size
@app.route('/size', methods=['GET'])
def getSize():
    print("** getSize **")
    sizes = Size.query.all()
    sizesList = list(map( lambda size: size.serialize(), sizes ))
    return jsonify(sizesList), 200


@app.route("/size", methods=['POST'])  
def addSize():
    print('***addSize***')
    print(request.json)    

    name = request.json.get('name',None)

    print('name=', name)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    size = Size()
    size.name = name
    
    db.session.add(size)
    db.session.commit()
    return jsonify(size.serialize()),201


# ProductState
@app.route('/product-state', methods=['GET'])
def getProductState():
    print("** getProductState **")
    productStates = ProductState.query.all()
    productStatesList = list(map( lambda productState: productState.serialize(), productStates ))
    return jsonify(productStatesList), 200


@app.route("/product-state", methods=['POST'])  
def addProductState():
    print('***addProductState***')
    print(request.json)    

    name = request.json.get('name',None)

    print('name=', name)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    productState = ProductState()
    productState.name = name
    
    db.session.add(productState)
    db.session.commit()
    return jsonify(productState.serialize()),201

# Region
@app.route('/region', methods=['GET'])
def getRegion():
    print("** getRegion **")
    regions = Region.query.all()
    regionsList = list(map( lambda region: region.serialize(), regions ))
    return jsonify(regionsList), 200


@app.route("/region", methods=['POST'])  
def addRegion():
    print('***addRegion***')
    print(request.json)    

    code = request.json.get('code',None)
    name = request.json.get('name',None)

    print('name=', name, 'code=',code)

    if not code:
        return jsonify({"msg":"code is required"}), 422

    if not name:
        return jsonify({"msg":"name is required"}), 422

    region = Region()
    region.code = code
    region.name = name
    
    db.session.add(region)
    db.session.commit()
    return jsonify(region.serialize()),201


# WeightUnit
@app.route('/weightunit', methods=['GET'])
def getWeightUnit():
    print("** getWeightUnit **")
    weightUnits = WeightUnit.query.all()
    weightUnitsList = list(map( lambda weightUnit: weightUnit.serialize(), weightUnits ))
    return jsonify(weightUnitsList), 200


@app.route("/weightunit", methods=['POST'])  
def addWeightUnit():
    print('***addWeightUnit***')
    print(request.json)    

    name = request.json.get('name',None)

    print('name=', name)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    weightUnit = WeightUnit()
    weightUnit.name = name
    
    db.session.add(weightUnit)
    db.session.commit()
    return jsonify(weightUnit.serialize()),201


# Product
@app.route('/product/', methods=['GET'])
def getAllProducts():
    print("** request.method===>" +  request.method)
    products = Product.getAll()
    print("***** getAllProducts.products===>",  products)

    productsList = list(map( lambda product: product.serialize(), products ))
    return jsonify(productsList), 200


@app.route('/product/<int:user_id>/<int:id>', methods=['GET'])
def getProductsFromUserStore(user_id:None, id:None):
    return  'Hello World:' + str(user_id) + ' ' + str(id)

@app.route('/product/<int:id>', methods=['GET'])
def getProduct(id=None):
    print("** request.method===>" +  request.method)
    product = Product.getOneById(id)
    #productsList = list(map( lambda product: product.serialize(), products ))
    if product:
        return jsonify(product.serialize()), 200
    else:
        return jsonify({"msg":"Product not found"}), 404


@app.route("/product", methods=["GET", "POST"])
@app.route("/product/<int:id>", methods=["PUT"])  
def saveProduct(id=None):
    print('***saveProductt *** => ', request.method)
    print('saveProduct.request.files=',request.files)
    print('saveProduct.request.form=',request.form)
    print('request.files.len=', len(request.files))

    if id and not request.form.get("userStoreId"):
        return jsonify({"msg":"userStoreId is required"}), 422

    if not request.form.get("name"):
        return jsonify({"msg":"name is required"}), 422

    if not request.form.get("brand"):
        return jsonify({"msg":"brand is required"}), 422

    if not request.form.get("model"):
        return jsonify({"msg":"model is required"}), 422

    if not request.form.get("color"):
        return jsonify({"msg":"color is required"}), 422

    if not request.form.get("hasBrand"):
        return jsonify({"msg":"hasBrand is required"}), 422

    if not request.form.get("price"):
        return jsonify({"msg":"price is required"}), 422

    if not request.form.get("originalPrice"):
        return jsonify({"msg":"originalPrice is required"}), 422

    if not request.form.get("qty"):
        return jsonify({"msg":"qty is required"}), 422

    if request.form.get("weight") is None:
        return jsonify({"msg":"weight is required"}), 422   

    if not request.form.get("departmentId"):
        return jsonify({"msg":"departmentId is required"}), 422   

    if not request.form.get("categoryId"):
        return jsonify({"msg":"categoryId is required"}), 422
    
    if not request.form.get("sizeId"):
        return jsonify({"msg":"sizeId is required"}), 422

    if not request.form.get("productStateId"):
        return jsonify({"msg":"productStateId is required"}), 422

    if not request.form.get("weightUnitId"):
        return jsonify({"msg":"weightUnitId is required"}), 422

    if len(request.files) == 0 and request.method == 'POST':
        return jsonify({"msg": "Not Selected File"}), 400  

    if not request.form.get("flete"):
        return jsonify({"msg":"flete is required"}), 422

    if not request.form.get("hasUpLoadPhotos"):
        return jsonify({"msg":"hasUpLoadPhotos is required"}), 422

    hasUpLoadPhotos = request.form.get("hasUpLoadPhotos").split(',')
    print('>>>saveProduct.hasUpLoadPhotos=',hasUpLoadPhotos)
    print('>>>saveProduct.len(hasUpLoadPhotos)=',len(hasUpLoadPhotos))
    for i in range(len(hasUpLoadPhotos)):
        hasUpLoadPhotos[i] = bool(hasUpLoadPhotos[i] !='false' )    

    print('>>>saveProduct.hasUpLoadPhotos (after)=', hasUpLoadPhotos)

    hasBrand = False
    if hasBrand == 'true':
        hasBrand = True
    print('>>>saveProduct.hasUpLoadPhotos.len(request.files)=', len(request.files))
    for i in range(len(request.files)):
        print('#####saveProduct.hasUpLoadPhotos[i]=', i, hasUpLoadPhotos[i])

        if not hasUpLoadPhotos[i]:
            continue
        photo = 'photo'+str(i)
        if photo not in request.files:
            msg = "{0} is required!".format(photo)
            return jsonify({"msg": msg}), 400 
        file = request.files[photo]
        if len(file.filename) == 0:
            continue
            #return jsonify({"msg": "Not Selected File"}), 400    
        if not (file and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMGS)):
            msg = "Image {0} not allowed!".format(photo)
            return jsonify({msg}), 400


    photosUrl = []    
    for i in range(len(hasUpLoadPhotos)):
        if not hasUpLoadPhotos[i]:
            continue
        photo = 'photo'+str(i)
        print('*********photo=', photo)
        file = request.files[photo]

        login = Login.query.filter_by(email='camila@gmail.com').first()
        filename = secure_filename(file.filename)
        filename = "userStore_" + str(login.id) + "_" + filename
        print('saveProduct.filename=',filename)
        print('saveProduct.filename.os=',os.path.join(app.config['UPLOAD_FOLDER']+"/images"))
        
        file.save(os.path.join(IMAGES_FOLDER, filename))
        print('>>>>i=', i)
        hasUpLoadPhotos[i]=filename
        photosUrl.append(filename)

    print('saveProduct.photosUrl=', photosUrl)
    print('saveProduct.request.form=', request.form)
    print('saveProduct.flete=',request.form.get("flete"))

    userStoreId = request.form.get("userStoreId")
    name = request.form.get("name")
    brand = request.form.get("brand")
    model = request.form.get("model")
    color = request.form.get("color")
    hasBrand = bool(request.form.get("hasBrand"))
    price = float(request.form.get("price"))
    originalPrice = float(request.form.get("originalPrice"))
    qty = int(request.form.get("qty"))
    weight = int(request.form.get("weight"))
    flete = float(request.form.get("flete"))

    departmentId = int(request.form.get("departmentId"))
    categoryId = int(request.form.get("categoryId"))
    sizeId = int(request.form.get("sizeId"))
    productStateId = int(request.form.get("productStateId"))
    weightUnitId = int(request.form.get("weightUnitId"))

    print('>>>>>>Product','userStoreId=', userStoreId, ', name=', name, ', brand=', brand, ', model=', model, ', color=', color, ', hasBrand=', hasBrand,', price=', price, ', originalPrice=', originalPrice, ', qty=', qty, ', weight=', weight, ', flete=', flete,', photosUrl=', photosUrl, ', userStoreId=', userStoreId, ', departmentId=', departmentId, ', categoryId=', categoryId, ', sizeId=',sizeId, ', productStateId=', productStateId, ', weightUnitId=', weightUnitId)

    product= None
    if request.method == 'POST':
        product = Product(name=name, price=price, originalPrice=originalPrice, hasBrand=hasBrand, brand=brand, color=color, model=model, weight=weight, flete=flete, qty=qty, photosUrl=photosUrl, departmentId=departmentId, categoryId=categoryId, sizeId=sizeId, productStateId=productStateId, weightUnitId=weightUnitId, userStoreId=userStoreId)
        product.save()
    else:
        product = Product.getOneById(id)    
        if not product:
            return jsonify({"msg":"Product not found"}), 404
        print('>>>saveProduct.photosUrl=>>>', photosUrl)
        photosToBeSave = []
        product.update(name=name, price=price, originalPrice=originalPrice, hasBrand=hasBrand, brand=brand, color=color, model=model, weight=weight, flete=flete, qty=qty, photosUrl=hasUpLoadPhotos, departmentId=departmentId, categoryId=categoryId, sizeId=sizeId, productStateId=productStateId, weightUnitId=weightUnitId, userStoreId=userStoreId)
        print('>>>saveProduct.product (after save)=', product)
    
    return jsonify(product.serialize()), 201


@app.route('/images/<filename>')
def image_profile(filename):
    return send_from_directory(IMAGES_FOLDER,filename)


# Cart
@app.route('/cart/<int:userId>', methods=['GET'])
def getCart(userId):
    print("** getCart **")
    cart = Cart.getOneById(userId)

    if not cart:
        return jsonify({"msg":"Cart not found"}), 404

    return jsonify(cart.serialize()), 200

@app.route('/cart-with-products/<int:userId>', methods=['GET'])
def getCartWithProducts(userId):
    print("** getCartWithProducts **")
    cart = Cart.getOneById(userId)

    if not cart:
        return jsonify({"msg":"Cart not found"}), 404

    return jsonify(cart.serialize_with_products()), 200


@app.route("/cart/<int:userId>", methods=['POST'])  
def addCart(userId):
    print('***addCart***')
    print(request.json)    

    print('userId=', userId)

    if not userId:
        return jsonify({"msg":"userId is required"}), 422

    cart = Cart(user.id)
    cart.userId = userId
    
    db.session.add(cart)
    db.session.commit()
    return jsonify(cart.serialize()),201

# CartProduct
@app.route('/cart-product/<int:id>', methods=['GET'])
def getCartProduct(id):
    print("** getCartProduct **")
    cartProduct = CartProduct.getOneById(id)
    return jsonify(cartProduct.serialize()), 200

@app.route('/cart-product/<int:user_id>', methods=['GET'])
def getCartProductByUserId(user_id):
    print("** getCartProductByUserId **")
    cartsproduct = CartProduct.query.all()
    cartsList = list(map( lambda cartProduct: cartProduct.serialize(), cartsproduct ))
    return jsonify(cartsList), 200

@app.route("/cart-product/<int:id>", methods=['PUT'])  
@app.route("/cart-product/", methods=['POST'])  
def addCartProduct(id=None):
    print('***addCartProduct***')
    print(request.json)    

    cartId = request.json.get('cartId',None)
    price = request.json.get('price',None)
    amount = request.json.get('amount',None)
    productId = request.json.get('productId',None)

    print('***addCartProduct => cartId=', cartId, 'price=', price, 'amount=', amount, 'productId=', productId)

    if not cartId:
        return jsonify({"msg":"cartId is required"}), 422

    if not price:
        return jsonify({"msg":"price is required"}), 422

    if not amount:
        return jsonify({"msg":"amount is required"}), 422

    if not productId:
        return jsonify({"msg":"productId is required"}), 422

    cart = Cart.getOneById(cartId)
    product = Product.getOneById(productId)

    if not cart:
        return jsonify({"msg":"Cart not found"}), 404

    if not product:
        return jsonify({"msg":"Product not found"}), 404

    cartproduct=None
    if id:
        cartproduct = CartProduct.getOneById(id)
        if not cartproduct:
            return jsonify({"msg":"CartProduct not found"}), 404
        cartproduct.price = price
        cartproduct.amount = amount
        cartproduct.update()
    else:        
        cartproduct = CartProduct(cart=cart, price=price, amount=amount, product=product)
        cartproduct.save()

    return jsonify(cartproduct.serialize()),201


# PaymentOption
@app.route('/payment-option', methods=['GET'])
def getPaymentOption():
    print("** getPaymentOption **")
    paymentOptions = PaymentOption.getAll()
    paymentOptionsList = list(map( lambda paymentOption: paymentOption.serialize(), paymentOptions ))
    return jsonify(paymentOptionsList), 200

@app.route('/payment-option/<int:id>', methods=['GET'])
def getPaymentOptionById(id):
    print("** getPaymentOption **")
    paymentOption= PaymentOption.getOneById(id)

    if not paymentOption:
        return jsonify({"msg":"PaymentOption not found"}), 404

    return jsonify(paymentOption.serialize()), 200



# Order
@app.route('/order/<int:id>', methods=['GET'])
def getOrder(id):
    print("** getOrder **")
    order = Order.getOneById(id)

    if not order:
        return jsonify({"msg":"Order not found"}), 404

    return jsonify(order.serialize()), 200

@app.route('/order/user/<int:id>', methods=['GET'])
def getOrderByUserId(id):
    print("** getOrderByUserId **")
    orders = Order.getAllByUserId(id)

    ordersList = list(map( lambda order: order.serialize(), orders ))
    return jsonify(ordersList), 200


@app.route('/order/<int:id>', methods=['DELETE'])
def deleteOrder(id):
    print("** getOrder **")
    order = Order.getOneById(id)

    if not order:
        return jsonify({"msg":"Order not found"}), 404

    #print('>>deleteOrder.order=', order.serialize())
    order.delete()

    return jsonify(order.serialize()),200


@app.route('/order/<int:id>/products', methods=['GET'])
def getOrdertWithProducts(id):
    print("** getOrdertWithProducts **")
    order = Order.getOneById(id)

    if not order:
        return jsonify({"msg":"Order not found"}), 404

    print('>>>getOrdertWithProducts.len(order.products):', len(order.products) )

    return jsonify(order.serialize_with_products()), 200

@app.route("/order/", methods=['POST'])  
def addOrder():
    print('***addOrder***')
    print(request.json)    

    userId = request.json.get('userId',None)
    regionId = request.json.get('regionId', None)
    products = request.json.get('products', None)
    flete = request.json.get('flete', None)
    address = request.json.get('address', None)
    phone = request.json.get('phone', None)
    paymentOptionId = request.json.get('paymentOptionId', None)

    if not userId:
        return jsonify({"msg":"userId is required"}), 422

    if not regionId:
        return jsonify({"msg":"regionId is required"}), 422

    if not products:
        return jsonify({"msg":"products is required"}), 422

    if not flete:
        return jsonify({"msg":"flete is required"}), 422

    if not address:
        return jsonify({"msg":"address is required"}), 422

    if not phone:
        return jsonify({"msg":"phone is required"}), 422

    if not paymentOptionId:
        return jsonify({"msg":"paymentOptionId is required"}), 422


    user = User.getOneById(userId)
    region = Region.getOneById(regionId)
    orderStatus = OrderStatus.getOneById(1)
    paymentOption = PaymentOption.getOneById(paymentOptionId)

    print('>>addOrder.user=', user)
    print('>>addOrder.region=', region)
    print('>>addOrder.orderStatus=', orderStatus)
    print('>>addOrder.paymentOption=', paymentOption)

    if not user:
        return jsonify({"msg":"User not found"}), 404

    if not region:
        return jsonify({"msg":"Region not found"}), 404

    if not orderStatus:
        return jsonify({"msg":"OrderStatus not found"}), 404

    if not paymentOption:
        return jsonify({"msg":"PaymentOption not found"}), 404

    order = Order(user=user, region=region, orderStatus=orderStatus, paymentOption=paymentOption, totalPrice=2000, flete=flete, address=address, phone=phone)

    receivers={}
    for orderProduct in products:
        print('>>>orderProduct=', orderProduct)
        product = Product.getOneById(orderProduct['productId'])
        if not product:
            return jsonify({"msg":"Product {0} not found!".format(orderProduct['productId'])}), 404

        newProduct = OrderProduct(order=order, product=product, price=orderProduct['price'], amount=orderProduct['amount'])
        order.products.append(newProduct)

        receivers[product.userStore.userId] = product.userStore.userId 

    order.save()

    print('>>>receivers:', receivers.keys())
    for receiver in receivers.keys():
        messageSender =  UserMessage(senderId=user.id, receiverId=receiver, messageTypeId=3, messageStatusId=1, message="Solicitud de Compra. Pedido numero: "+str(order.id), link=str(order.id))
        messageSender.save()
        
        messageReceiver =  UserMessage(senderId=receiver, receiverId=user.id,messageTypeId=3, messageStatusId=1, message="Solicitud de Compra. Pedido numero: "+str(order.id), link=str(order.id))
        messageReceiver.save()

        print(">>>UserMessage id={0}, senderId={1}, senderId={2}".format(order.id, user.id, receiver))

    return jsonify(order.serialize()),201

# OrderProduct
@app.route('/order-product/<int:id>', methods=['GET'])
def getOrderProduct(id):
    print("** getOrderProduct **")
    orderProduct = OrderProduct.getOneById(id)
    return jsonify(orderProduct.serialize()), 200


@app.route('/user-store/<int:userStoreId>/sells', methods=['GET'])
def getProductsSold(userStoreId):
    print("***** getOrderProduct **")
    productsSold = OrderProduct.getAllByUserStoreId(userStoreId)
    print('>>>getProductsSold.productsSold=', productsSold)
    
    #productsSoldList = list(map( lambda product: product.serialize(), productsSold ))
    return jsonify(productsSold), 200

@app.route("/order-product/<int:id>", methods=['PUT'])  
@app.route("/order-product/", methods=['POST'])  
def addOrderProduct(id=None):
    print('***addOrderProduct***')
    print(request.json)    

    orderId = request.json.get('orderId',None)
    price = request.json.get('price',None)
    amount = request.json.get('amount',None)
    productId = request.json.get('productId',None)

    print('***addOrderProduct => orderId=', orderId, 'price=', price, 'amount=', amount, 'productId=', productId)

    if not orderId:
        return jsonify({"msg":"orderId is required"}), 422

    if not price:
        return jsonify({"msg":"price is required"}), 422

    if not amount:
        return jsonify({"msg":"amount is required"}), 422

    if not productId:
        return jsonify({"msg":"productId is required"}), 422

    order = Order.getOneById(orderId)
    product = Product.getOneById(productId)

    if not order:
        return jsonify({"msg":"Order not found"}), 404

    if not product:
        return jsonify({"msg":"Product not found"}), 404

    orderproduct=None
    if id:
        orderproduct = OrderProduct.getOneById(id)
        if not orderproduct:
            return jsonify({"msg":"OrderProduct not found"}), 404
        orderproduct.price = price
        orderproduct.amount = amount
        orderproduct.update()
    else:        
        orderproduct = OrderProduct(order=order, price=price, amount=amount, product=product)
        orderproduct.save()

    return jsonify(orderproduct.serialize()),201


# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    region1 = Region(code='01', name='Tarapac\u00e1')
    region2 = Region(code='02', name='Antofagasta')
    region3 = Region(code='03', name='Atacama')
    region4 = Region(code='04', name='Coquimbo')
    region5 = Region(code='05', name='Valparaíso')
    region6 = Region(code='06', name='O\u2019Higgins')
    region7 = Region(code='07', name='Maule')
    region8 = Region(code='08', name='Biob\u00edo')
    region9 = Region(code='09', name='Araucan\u00eda')
    region10 = Region(code='10', name='Los Lagos')
    region11 = Region(code='11', name='Ays\u00e9n')
    region12 = Region(code='12', name='Magallanes')
    region13 = Region(code='13', name='Metropolitana de Santiago')
    region14 = Region(code='14', name='Los R\u00edos')
    region15 = Region(code='15', name='Arica y Parinacota')
    region16 = Region(code='16', name='\u00d1uble')

    region1.save()
    region2.save()
    region3.save()
    region4.save()
    region5.save()
    region6.save()
    region7.save()
    region8.save()
    region9.save()
    region10.save()
    region11.save()
    region12.save()
    region13.save()
    region14.save()
    region15.save()
    region16.save()

    #Department
    department1 = Department(name='Hogar')
    department2 = Department(name='Ropa')
    department3 = Department(name='Calzado')
    department4 = Department(name='Informática')
    department5 = Department(name='Electrodomésticos')
    department6 = Department(name='Etc y Tal')

    department1.save()
    department2.save()
    department3.save()
    department4.save()
    department5.save()
    department6.save()

    #MessageType
    messageType1 = MessageType(name='duda')
    messageType2 = MessageType(name='oferta')
    messageType3 = MessageType(name='pedido')
    
    messageType1.save()
    messageType2.save()
    messageType3.save()

    #MessageStatus
    messageStatus1 = MessageStatus(name='nueva')
    messageStatus2 = MessageStatus(name='leido')
    messageStatus1.save()
    messageStatus2.save()

    #Login 1
    login1 = Login(email='juanita@gmail.com', password='1234')
    user1 = User(name='User 1', loginId=1, photoUrl='user1.png', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23167223k', phone='+56 982838393', address='Direccion 1')
    cart1 = Cart(1)
    userStore1 = UserStore(name='UserStore 1', regionId=13, userId=1, bio='Bio', url='juanita', photoUrl='tendita.png')

    login1.save()
    user1.save()
    cart1.save()
    userStore1.save()

    #Login 2
    login2 = Login(email='juan@gmail.com', password='1234')
    user2 = User(name='User 2', loginId=2, photoUrl='user2.png', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23167223k', phone='+56 983838393', address='Direccion 2')
    cart2 = Cart(2)
    userStore2 = UserStore(name='UserStore 2', regionId=13, userId=2, bio='Bio', url='juan', photoUrl='tendita.png')

    login2.save()
    user2.save()
    cart2.save()
    userStore2.save()

    #Login 3
    login3 = Login(email='pablo@gmail.com', password='1234')
    user3 = User(name='User 3', loginId=3, photoUrl='user3.png', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23163523k', phone='+56 945838393', address='Direccion 3')
    cart3 = Cart(3)
    userStore3 = UserStore(name='UserStore 3', regionId=13, userId=3, bio='Bio', url='pablo', photoUrl='tendita.png')  

    login3.save()
    user3.save()
    cart3.save()
    userStore3.save()

    #Login 4
    login4 = Login(email='camila@gmail.com', password='1234')
    user4 = User(name='User 4', loginId=4, photoUrl='user4.png', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23112323k', phone='+56 983818493', address='Direccion 4')
    cart4 = Cart(4)
    userStore4 = UserStore(name='UserStore 4', regionId=13, userId=4, bio='Bio', url='camila', photoUrl='tendita.png')  

    login4.save()
    user4.save()
    cart4.save()
    userStore4.save()

    # Follows
    user1.follow(user2)
    user1.follow(user3)
    user3.follow(user2)
    #db.session.add(Follower(followerId=1, followedId=4))  
    #db.session.add(Follower(followerId=1, followedId=5))

    db.session.add(Category(name='Chicos'))
    db.session.add(Category(name='Chicas'))
    
    db.session.add(Size(name='P'))
    db.session.add(Size(name='M'))
    db.session.add(Size(name='G'))

    db.session.add(ProductState(name='Nuevo'))
    db.session.add(ProductState(name='Usado'))

    db.session.add(WeightUnit(name='KG'))
    db.session.add(WeightUnit(name='gm'))

    db.session.commit()

    #Products
    product1 = Product(name="Product 1", price=13000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=1)
    product1.save()

    product2 = Product(name="Product 2", price=23000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=2)
    product2.save()

    product3 = Product(name="Product 3", price=33000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=4)
    product3.save()    

    product4 = Product(name="Product 4", price=43000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=4)
    product4.save()

    cartProduct1 = CartProduct(cart1, price=10000, amount=1, product=product1)
    cartProduct2 = CartProduct(cart1, price=10000, amount=1, product=product2)
    cartProduct3 = CartProduct(cart2, price=10000, amount=1, product=product1)

    cartProduct1.save()
    cartProduct2.save()
    cartProduct3.save()

    orderStatus1 = OrderStatus(name='Pendiente Pago')
    orderStatus2 = OrderStatus(name='Pendiente Entrega')
    orderStatus3 = OrderStatus(name='En evaluacion del pago')
    orderStatus4 = OrderStatus(name='Entregue')

    orderStatus1.save()
    orderStatus2.save()
    orderStatus3.save()
    orderStatus4.save()

    paymentOption1 = PaymentOption(name='TRANSFERENCIA BANCARIA')
    paymentOption2 = PaymentOption(name='PayPal')
    paymentOption3 = PaymentOption(name='khipu')
    paymentOption1.save()
    paymentOption2.save()
    paymentOption3.save()


    order1 = Order(user=user1, orderStatus=orderStatus1, region=region1, paymentOption=paymentOption1, totalPrice=2000, flete=1000, address='Addresses 1', phone='981888996')
    order1.save()

    orderProduct1 = OrderProduct(order=order1, product=product1, price=2000, amount=3)
    orderProduct1.save()

    userMessage1 =  UserMessage(senderId=1, receiverId=2, messageTypeId=1, messageStatusId=1, message="Message 1", link='Link1')

    userMessage2 =  UserMessage(senderId=1, receiverId=2, messageTypeId=1, messageStatusId=1, message="Message 2", link='Link2')

    userMessage3 =  UserMessage(senderId=2, receiverId=3, messageTypeId=1, messageStatusId=1, message="Message 3", link='Link2')

    userMessage1.save()
    userMessage2.save()
    userMessage3.save()


    return 'Tables filled'

#if __name__ == '__main__':
#    app.run(port=3245, debug=True)

# second solution
#def insert_initial_values(*args, **kwargs):
#    db.session.add(Region(code='01', name='low'))
#    db.session.commit()




if __name__ == "__main__":
    manager.run()


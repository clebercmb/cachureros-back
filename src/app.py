import os, datetime 
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_script import Manager 
from flask_migrate import Migrate, MigrateCommand
from models import db, Product, UserStore, Login, User, Department, Category, Size, ProductState, Cart, CartProduct, WeightUnit, Region, Follow
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

products = [

]

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

    user = User(name=name, loginId=login.id, photoUrl=None, active=True, birthDate=None, nationalId=None, phone=None)
    user.save()

    userStore = UserStore(name=name, userId=user.id, regionId=None, bio='', url='', photoUrl=None)
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
    user = User.getOneBy(id)
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
    print("** appy.saveUserStoreById.userStore=",userStore) 

    email = request.form.get("email", None)
    password = request.form.get("password", None)
    userName = request.form.get("userName", None)
    birthDate = request.form.get("birthDate", None)
    nationalId= request.form.get("nationalId", None)
    phone = request.form.get("phone", None)
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

    if not request.form.get("userStoreName", None):
        return jsonify({"msg":"userStoreName is required"}), 422

    if not request.form.get("regionId", None):
        return jsonify({"msg":"regionId is required"}), 422

    if not request.form.get("url", None):
        return jsonify({"msg":"url is required"}), 422

    if hasUserStorePhotoUrl and len(userStorePhotoUrl) == 0:
        return jsonify({"msg":"userStorePhotoUrl is required"}), 422


    if hasUserPhotoUrl: 
        print('&&&&&isFileAllowed')

        if 'userPhoto' not in request.files:
            return jsonify({"msg": "userPhoto is required"}), 400


        if not isFileAllowed('userPhotoUrl', userPhotoUrl):
            msg = "User photo image {0} not allowed!".format('userPhotoUrl')
            return jsonify({msg}), 400
        saveImageFile(fileKey='userPhotoUrl', request=request, fileType="UserProfile", email=email)


    if hasUserStorePhotoUrl:
        if not isFileAllowed(fileKey='userStorePhotoUrl', request=request):
            msg = "UserStore photo image {0} not allowed!".format('userStorePhotoUrl')
            return jsonify({msg}), 400
        saveImageFile(fileKey='userStorePhotoUrl', request=request, fileType="UserStore", email=email)

    login = Login.getOneById(userStore.user.login.id)
    login.email = email
    login.password = password
    login.update()

    user = User.getOneBy(userStore.user.id)
    user.name = userName
    user.birthDate = birthDate
    user.nationalId = nationalId
    user.phone = phone

    userStore.name = userStoreName
    userStore.regionId = regionId
    userStore.bio = bio
    userStore.url = url

    userStore.save()

    print('saveUserStoreById.userStore (after save):', userStore.serialize())
    return jsonify(userStore.serialize()),200


def isFileAllowed(fileKey, request):
    print('>>>>>>>isFileAllowed.fileKey=', fileKey)
    print('****isFileAllowed.request.files=', request.files[''])
    file = request.files[fileKey]
    print('>>>>>>>isFileAllowed.file.filename=', file.filename)
    if not (file and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMGS)):
        return False
    return True


def saveImageFile(fileKey, request, fileType, email):
    
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
    followed = Follower.getAllFollower()
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

    follower = Follower(followerId, followedId)
    
    follower.save()

    return jsonify(follower.serialize()),201


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

    if not request.form.get("userStoreId"):
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
@app.route('/cart/<int:user_id>', methods=['GET'])
def getCart(user_id):
    print("** getCart **")
    carts = Cart.query.all()
    cartsList = list(map( lambda cart: cart.serialize(), carts ))
    return jsonify(cartsList), 200


@app.route("/cart/<int:user_id>", methods=['POST'])  
def addCart(user_id):
    print('***addCart***')
    print(request.json)    

    userId = user_id


    print('userId=', userId)


    if not userId:
        return jsonify({"msg":"userId is required"}), 422



    cart = Cart()
    cart.userId = userId
    
    db.session.add(cart)
    db.session.commit()
    return jsonify(cart.serialize()),201

# CartProduct
@app.route('/cartproduct/<int:user_id>', methods=['GET'])
def getCartProduct(user_id):
    print("** getCartProduct **")
    cartsproduct = CartProduct.query.all()
    cartsList = list(map( lambda cartProduct: cartProduct.serialize(), cartsproduct ))
    return jsonify(cartsList), 200


@app.route("/cartproduct/<int:user_id>", methods=['POST'])  
def addCartProduct(user_id):
    print('***addCartProduct***')
    print(request.json)    

    price = request.json.get('price',None)
    amount = request.json.get('amount',None)
    productId = request.json.get('productId',None)
    cartId = request.json.get('cartId',None)


    print('price=', price, 'amount=', amount, 'productId=', productId, 'cartId=', cartId)

    if not price:
        return jsonify({"msg":"price is required"}), 422

    if not amount:
        return jsonify({"msg":"amount is required"}), 422

    if not productId:
        return jsonify({"msg":"productId is required"}), 422

    if not cartId:
        return jsonify({"msg":"cartId is required"}), 422

    cartproduct = CartProduct()
    cartproduct.price = price
    cartproduct.amount = amount
    cartproduct.productId = productId
    cartproduct.cartId = cartId
    
    db.session.add(cartproduct)
    db.session.commit()
    return jsonify(cartproduct.serialize()),201


# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    db.session.add(Region(code='01', name='Tarapac\u00e1'))
    db.session.add(Region(code='02', name='Antofagasta'))
    db.session.add(Region(code='03', name='Atacama'))
    db.session.add(Region(code='04', name='Coquimbo'))
    db.session.add(Region(code='05', name='Valparaíso'))
    db.session.add(Region(code='06', name='O\u2019Higgins'))
    db.session.add(Region(code='07', name='Maule'))
    db.session.add(Region(code='08', name='Biob\u00edo'))
    db.session.add(Region(code='09', name='Araucan\u00eda'))
    db.session.add(Region(code='10', name='Los Lagos'))
    db.session.add(Region(code='11', name='Ays\u00e9n'))
    db.session.add(Region(code='12', name='Magallanes'))
    db.session.add(Region(code='13', name='Metropolitana de Santiago'))
    db.session.add(Region(code='14', name='Los R\u00edos'))
    db.session.add(Region(code='15', name='Arica y Parinacota'))
    db.session.add(Region(code='16', name='\u00d1uble'))

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

    #Login 1
    login1 = Login(email='juanita@gmail.com', password='1234')
    user1 = User(name='User 1', loginId=1, photoUrl='juanita.jpg', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23167223k', phone='+56 982838393')
    userStore1 = UserStore(name='UserStore 1', regionId=13, userId=1, bio='Bio', url='juanita', photoUrl='tendita.png')

    login1.save()
    user1.save()
    userStore1.save()

    #Login 2
    login2 = Login(email='juan@gmail.com', password='1234')
    user2 = User(name='User 2', loginId=2, photoUrl='juanita.jpg', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23167223k', phone='+56 983838393')
    userStore2 = UserStore(name='UserStore 2', regionId=13, userId=2, bio='Bio', url='juan', photoUrl='tendita.png')

    login2.save()
    user2.save() 
    userStore2.save()

    #Login 3
    login3 = Login(email='pablo@gmail.com', password='1234')
    user3 = User(name='User 3', loginId=3, photoUrl='juanita.jpg', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23163523k', phone='+56 945838393')
    userStore3 = UserStore(name='UserStore 3', regionId=13, userId=3, bio='Bio', url='pablo', photoUrl='tendita.png')  

    login3.save()
    user3.save()
    userStore3.save()

    #Login 4
    login4 = Login(email='camila@gmail.com', password='1234')
    user4 = User(name='User 4', loginId=4, photoUrl='juanita.jpg', active=True, birthDate=datetime.datetime.utcnow(), nationalId='23112323k', phone='+56 983818493')
    userStore4 = UserStore(name='UserStore 4', regionId=13, userId=4, bio='Bio', url='camila', photoUrl='tendita.png')  

    login4.save()
    user4.save()
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
    product1 = Product(name="Product 1", price=23000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=1)
    product1.save()

    product2 = Product(name="Product 2", price=23000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=2)
    product2.save()

    product3 = Product(name="Product 3", price=23000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=4)
    product3.save()    

    product4 = Product(name="Product 4", price=23000.00, originalPrice=40000.00, hasBrand=False,brand="Ruko", color="Verde Amerillo", model="Deportiva", weight=1, flete=10, qty=1, photosUrl=["image_0.png", "image_1.png","image_2.png","image_3.png","image_4.png"],departmentId=1,categoryId=1, sizeId=1, productStateId=1, weightUnitId=1, userStoreId=4)
    product4.save()

    return 'Tables filled'

#if __name__ == '__main__':
#    app.run(port=3245, debug=True)

# second solution
#def insert_initial_values(*args, **kwargs):
#    db.session.add(Region(code='01', name='low'))
#    db.session.commit()




if __name__ == "__main__":
    manager.run()


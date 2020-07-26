import os
from flask import Flask, request, jsonify, url_for
from flask_script import Manager 
from flask_migrate import Migrate, MigrateCommand
from models import db, Product, UserStore, Login, User, Department, Category, Size, ProductState, WeightUnit
from flask_cors import CORS
from utils import APIException, generate_sitemap
from graphene import ObjectType, String, Schema


app = Flask(__name__)
app.url_map.strict_slashes = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

CORS(app)
Migrate(app,db)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

products = [

]

# Login
@app.route('/login', methods=['GET'])
def getLogin():
    print("** getLogin **")
    logins = Login.query.all()
    loginsList = list(map( lambda login: login.serialize(), logins ))
    return jsonify(loginsList), 200


@app.route("/login", methods=['POST'])  
def addLogin():
    print('***addLogin***')
    print(request.json)    

    name = request.json.get('name',None)

    print('name=', name)

    if not name:
        return jsonify({"msg":"login name is required"}), 422

    login = Login()
    login.name = name
    
    db.session.add(login)
    db.session.commit()
    return jsonify(login.serialize()),201


# User
@app.route('/user', methods=['GET'])
def getUser():
    print("** getUser **")
    users = User.query.all()
    usersList = list(map( lambda user: user.serialize(), users ))
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
    userStores = UserStore.query.all()
    userStoresList = list(map( lambda userStore: userStore.serialize(), userStores ))
    return jsonify(userStoresList), 200


@app.route("/user-store", methods=['POST'])  
def addUserStoreId():
    print('***addUserStoreId***')
    print(request.json)    

    name = request.json.get('name',None)
    userId = request.json.get('userId',None)
 

    print('name=', name, 'userId=', userId)

    if not name:
        return jsonify({"msg":"name is required"}), 422

    if not userId:
        return jsonify({"msg":"userId is required"}), 422

    userStore = UserStore()
    userStore.name = name
    userStore.userId = userId
    
    db.session.add(userStore)
    db.session.commit()
    return jsonify(userStore.serialize()),201

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
@app.route('/product/<int:user_id>/<int:id>', methods=['GET'])
def getProduct(user_id:None, id:None):
    return  'Hello World:' + str(user_id) + ' ' + str(id)

@app.route('/product/<int:user_id>', methods=['GET'])
def getProductsFromUserStore(user_id=None):
    print("** request.method===>" +  request.method)
    products = Product.query.all()
    productsList = list(map( lambda product: product.serialize(), products ))
    return jsonify(productsList), 200


@app.route("/product/<int:user_id>", methods=['POST'])  
def product_9post(user_id=None):
    print('***product_post***')
    print(request.json)    

    userStoreId = user_id
    name = request.json.get('name',None)
    brand = request.json.get('brand',None)
    model = request.json.get('model',None)
    color = request.json.get('brand',None)
    hasBrand = request.json.get('hasBrand',None)
    price = request.json.get('price',None)
    originalPrice = request.json.get('originalPrice',None)
    qty = request.json.get('qty',None)
    weight = request.json.get('weight',None)
    photos = request.json.get('photos',None)
    urlPhoto1 = photos[0]
    urlPhoto2 = photos[1]
    urlPhoto3 = photos[2]
    urlPhoto4 = photos[3]
    urlPhoto5 = photos[4]

    departmentId = request.json.get('departmentId')
    categoryId = request.json.get('categoryId')
    sizeId = request.json.get('sizeId')
    productStateId = request.json.get('productStateId')
    weightUnitId = request.json.get('weightUnitId')

    print('userStoreId=', userStoreId, 'name=', name, 'brand=', brand, 'model=', model, 'color=', color, 'hasBrand=', hasBrand,'price=', price, 'originalPrice=', originalPrice, 'qty=', qty,  'weight=', weight, 'urlPhoto1=', urlPhoto1, 'urlPhoto2=', urlPhoto2, 'urlPhoto3=', urlPhoto3, 'urlPhoto4=', urlPhoto4, 'urlPhoto5=', urlPhoto5, 'userStoreId=', userStoreId, 'departmentId=', departmentId, 'categoryId=', categoryId, 'sizeId=',sizeId, 'productStateId=', productStateId, 'weightUnitId=', weightUnitId)

    if not userStoreId:
        return jsonify({"msg":"userStoreId is required"}), 422

    if not name:
        return jsonify({"msg":"name is required"}), 422

    if not brand:
        return jsonify({"msg":"brand is required"}), 422

    if not model:
        return jsonify({"msg":"model is required"}), 422

    if not color:
        return jsonify({"msg":"color is required"}), 422

    if not price:
        return jsonify({"msg":"price is required"}), 422

    if not originalPrice:
        return jsonify({"msg":"originalPrice is required"}), 422

    if not qty:
        return jsonify({"msg":"qty is required"}), 422

    if not weight:
        return jsonify({"msg":"weight is required"}), 422   

    if not urlPhoto1:
        return jsonify({"msg":"urlPhoto1 is required"}), 422   
                    
    if not urlPhoto2:
        return jsonify({"msg":"urlPhoto2 is required"}), 422   

    if not urlPhoto3:
        return jsonify({"msg":"urlPhoto3 is required"}), 422   

    if not urlPhoto4:
        return jsonify({"msg":"urlPhoto4 is required"}), 422   

    if not urlPhoto5:
        return jsonify({"msg":"urlPhoto5 is required"}), 422   

    if not departmentId:
        return jsonify({"msg":"departmentId is required"}), 422   

    if not categoryId:
        return jsonify({"msg":"categoryId is required"}), 422
    
    if not sizeId:
        return jsonify({"msg":"sizeId is required"}), 422

    if not productStateId:
        return jsonify({"msg":"productStateId is required"}), 422

    if not weightUnitId:
        return jsonify({"msg":"weightUnitId is required"}), 422

    product = Product()
    product.userStoreId = userStoreId
    product.name = name
    product.brand = brand
    product.model = model
    product.color = color
    product.hasBrand = hasBrand
    product.price = price
    product.originalPrice = originalPrice
    product.qty = qty
    product.weight = weight
    product.photos = photos
    product.urlPhoto1 = urlPhoto1
    product.urlPhoto2 = urlPhoto2
    product.urlPhoto3 = urlPhoto3
    product.urlPhoto4 = urlPhoto4
    product.urlPhoto5 = urlPhoto5
    
    product.departmentId = departmentId
    product.categoryId = categoryId
    product.sizeId = sizeId
    product.productStateId = productStateId
    product.weightUnitId = weightUnitId

    db.session.add(product)
    db.session.commit()
    return jsonify(product.serialize()), 201


# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#if __name__ == '__main__':
#    app.run(port=3245, debug=True)

if __name__ == "__main__":
    manager.run()



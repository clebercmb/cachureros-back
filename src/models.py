from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, event, DateTime

from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import datetime

db = SQLAlchemy()

class Login(db.Model):
    __tablename__ = 'Login'
    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True)
    password = Column(String(128), nullable = False)

    user = db.relationship("User", backref="Login", lazy=True, uselist=False)

    createdAt = Column(DateTime)
    modifiedAt  = Column(DateTime)

    # class constructor
    def __init__(self, email, password):
        """
        Class constructor
        """
        self.email = email
        self.password = password
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()


    def __rep__(self):
        return "Login %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt 
        } 
    def serialize_with_user(self):
        print('****Login.serialize_with_user:', self.user)
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'user': self.user.serialize(),
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt 
        }  
 

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_one_login(id):
        return Login.query.get(id)

    @staticmethod
    def get_all_login():
        return Login.query.all()

    @staticmethod
    def get_login_by_email(email):
        login = Login.query.filter_by(email=email).first()
        return login 



class Follow(db.Model):
    __tablename__ = 'Follow'

    followerId = Column(Integer, ForeignKey('User.id'), primary_key = True )   
    followedId = Column(Integer, ForeignKey('User.id'), primary_key = True)    

    createdAt = Column(DateTime)
    modifiedAt  = Column(DateTime)

    # class constructor
    def __init__(self, follower, followed):
        """
        Class constructor
        """
        self.followerId = follower.id
        self.followedId = followed.id

        follower = db.relationship("User", foreign_keys=[Follow.followerId])
        followed = db.relationship("User", foreign_keys=[Follow.followedId])

        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "Follower %r>" % self.id

    def serialize(self):
        return {
            'followerId': self.followerId,
            'followedId': self.followedId,
            'follower': self.follower.serialize(),
            'followed': self.followed.serialize(),
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt 
        }        

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAllFollower():
        followers = list(map(lambda follower: follower.serialize(), Follow.query.all() ))
        print('****models.Follower.followers=',followers)
        return followers


class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)

    loginId = Column(Integer, ForeignKey('Login.id'))    
    login = relationship(Login)
    photoUrl=Column(String(100), default = '/images/tendita.png')

    #followedList = db.relationship("Follower", backref="User", lazy=True, uselist=False)
    #followerList = db.relationship("Follower", backref="User", lazy=True, uselist=False)

    #followedList = relationship("Follower", backref="User", lazy=True, uselist=False, secondary="Follower")
    followeds = db.relationship(Follow, foreign_keys=[Follow.followerId], backref=db.backref('follower', lazy='joined'),lazy='dynamic', cascade='all, delete-orphan')
    
    followers = db.relationship(Follow, foreign_keys=[Follow.followedId], backref=db.backref('followed', lazy='joined'),lazy='dynamic', cascade='all, delete-orphan')

    userStore = db.relationship("UserStore", backref="User", lazy=True, uselist=False)

    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)
    active = db.Column(Boolean, default=True)

    # class constructor
    def __init__(self, name, loginId, photoUrl, active):
        """
        Class constructor
        """
        self.name = name
        self.loginId = loginId
        self.photoUrl = photoUrl
        self.active = active
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "User %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize(),
            'photoUrl': self.photoUrl,
            'active': self.active,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        } 

    def serialize_with_userStore(self):
        print('****Login.serialize_with_user:', self.userStore)
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize(),
            'photoUrl': self.photoUrl,
            'active': self.active,
            'userStore': self.userStore.serialize(),
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        }         

    def serialize_with_follow(self):
        print('****User.serialize_with_follow.self.followeds:', self.followeds.all())
        print('****User.serialize_with_follow.self.followers:', self.followers.all())
        followeds = list(map(lambda followed: followed.serialize(), self.followeds.all()))
        followers = list(map(lambda follower: follower.serialize(), self.followers.all()))
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize(),
            'photoUrl': self.photoUrl,
            'followeds': followeds,
            'followers': followers,
            'active': self.active,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        }    

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            f.save()

    def unfollow(self, user):
        f = self.followeds.filter_by(followedId=user.id).first()
        if f:
            f.delete()

    def is_following(self, user):
        return self.followeds.filter_by(followedId=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(followerId=user.id).first() is not None    

    def get_followers_by_user(self, user):
        return self.followers.filter_by(followerId=user.id).first() is not None

    def getFolloweds(self):
        followeds = list(map(lambda followed: followed.followed, self.followeds.all()))
        return  followeds

    def getFollowers(self):
        followers = list(map(lambda follower: follower.follower, self.followers.all()))
        return  followers

    @staticmethod
    def getOneBy(id):
        return User.query.get(id)

    @staticmethod
    def get_followeds_by_id(id):
        print('****User.get_followeds_by_user.id:', id)
        user = User.get_one_user(id)
        followeds = list(map(lambda followed: followed.followed, user.followeds.all()))

        print('****User.get_followeds_by_id.followeds:', followeds)

        return followeds  

    @staticmethod
    def get_followers_by_id(id):
        print('****User.get_followers_by_id.id:', id)
        user = User.get_one_user(id)
        followers = list(map(lambda follower: follower.follower, user.followers.all()))

        print('****User.get_followers_by_id.followers:', followers)

        return followers  

class Region(db.Model):
    __tablename__ = 'Region'
    id = Column(Integer, primary_key=True)
    code = Column(String(2), nullable = False)
    name = Column(String(100), nullable = False)

    def __rep__(self):
        return "Region %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }        


class UserStore(db.Model):
    __tablename__ = 'UserStore'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)
    
    userId = Column(Integer, ForeignKey('User.id'))
    user = relationship(User)

    regionId = Column(Integer, ForeignKey('Region.id'))
    region = relationship(Region)

    likes = Column(Integer, default=0)
    title = Column(String(100), nullable = False)
    bio = Column(String(200), nullable = False)
    url = Column(String(100), nullable = False, unique=True)
    photoUrl = Column(String(100)) 
    solds = Column(Integer, default=0)
    sells = Column(Integer, default=0) 

    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)

    #products = relationship("Product", backref="UserStore", lazy=True, uselist=False)
    products = relationship("Product", backref="UserStore", lazy=True)

    # class constructor
    def __init__(self, name, userId, regionId, title, bio, url, photoUrl):
        """
        Class constructor
        """
        self.name = name
        self.userId = userId
        self.regionId = regionId
        self.title = title
        self.bio = bio
        self.url = url
        self.photoUrl = photoUrl
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "UserStore %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name ,
            'user': self.user.serialize(),
            'region': self.region.serialize(),
            'likes': self.likes,
            'title': self.title,
            'bio': self.bio,
            'url': self.url,
            'photoUrl': self.photoUrl,
            'solds': self.solds,
            'sells': self.sells,
            'followers': self.user.followers.count(),
            'followeds': self.user.followeds.count(),
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        }  

    def serialize_with_product(self):
        print('****UserStore.serialize_with_product.products:', self.products)
        products = list(map(lambda product: product.serialize(), self.products))
        return {
            'id': self.id,
            'name': self.name ,
            'user': self.user.serialize(),
            'region': self.region.serialize(),
            'likes': self.likes,
            'title': self.title,
            'bio': self.bio,
            'url': self.url,
            'photoUrl': self.photoUrl,
            'solds': self.solds,
            'sells': self.sells,
            'followers': self.user.followers.count(),
            'followeds': self.user.followeds.count(),
            'products':products,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        }  

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAllUserStores():
        userStores = list(map(lambda userStore: userStore.serialize(), UserStore.query.all() ))
        print('****models.userStores=',userStores)
        return userStores

    @staticmethod
    def getOneUserStoreById(id):
        return UserStore.query.get(id)

    @staticmethod
    def getOneUserStoreByUrl(url):
        userStore = UserStore.query.filter_by(url=url).first()
        return userStore    
    



class Department(db.Model):
    __tablename__ = 'Department'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), unique=True)

    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)

    # class constructor
    def __init__(self, name):
        """
        Class constructor
        """
        self.name = name
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()


    def __rep__(self):
        return "Department %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt  
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAll():
        departments = list(map(lambda department: department.serialize(), Department.query.all() ))
        print('****models.Department.getAll=',departments)
        return departments

    @staticmethod
    def getOneById(id):
        return Department.query.get(id)


class Category(db.Model):
    __tablename__ = 'Category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __rep__(self):
        return "Category %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name    
        }   

class Size(db.Model):
    __tablename__ = 'Size'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __rep__(self):
        return "Size %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name    
        }   

class ProductState(db.Model):
    __tablename__ = 'ProductState'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __rep__(self):
        return "Size %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name    
        }   

class WeightUnit(db.Model):
    __tablename__ = 'WeightUnit'
    id = Column(Integer, primary_key=True)
    name = Column(String(2), unique=True)

    def __rep__(self):
        return "WeightUnit %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name    
        }   

class Product(db.Model):
    __tablename__= 'Product'
    id = db.Column(Integer, primary_key=True)

    name = db.Column(String(50), nullable = False)
    price = db.Column(Float,nullable = False)
    originalPrice = db.Column(Float, nullable = False)
    flete = db.Column(Float, nullable = False)
    hasBrand = db.Column(Boolean, nullable = False)
    brand = db.Column(String(50))
    color = db.Column(String(50))
    model = db.Column(String(50))
    weight = db.Column(Float, nullable = False)

    qty = db.Column(Integer, nullable=False)
    urlPhoto1 = db.Column(String(150))
    urlPhoto2 = db.Column(String(150))
    urlPhoto3 = db.Column(String(150))
    urlPhoto4 = db.Column(String(150))
    urlPhoto5 = db.Column(String(150))

    userStoreId = db.Column(Integer, ForeignKey('UserStore.id'))
    userStore = db.relationship(UserStore) 

    departmentId = db.Column(Integer, ForeignKey('Department.id'))
    department = db.relationship(Department) 

    categoryId = db.Column(Integer, ForeignKey('Category.id'))
    category = db.relationship(Category) 

    sizeId = db.Column(Integer, ForeignKey('Size.id'))
    size = db.relationship(Size) 

    productStateId = db.Column(Integer, ForeignKey('ProductState.id'))
    productState = db.relationship(ProductState) 

    weightUnitId = db.Column(Integer, ForeignKey('WeightUnit.id'))
    weightUnit = db.relationship(WeightUnit) 

    # class constructor
    def __init__(self, name, price, originalPrice, flete, hasBrand, brand, color, model, weight, qty, photosUrl, userStoreId, departmentId, categoryId, sizeId, productStateId, weightUnitId):
        """
        Class constructor
        """
        self.name = name
        self.price = price
        self.originalPrice = originalPrice
        self.flete = flete
        self.hasBrand = hasBrand
        self.brand = brand
        self.color = color
        self.model = model
        self.weight = weight
        self.qty = qty
        self.urlPhoto1 = photosUrl[0]
        self.urlPhoto2 = photosUrl[1]
        self.urlPhoto3 = photosUrl[2]
        self.urlPhoto4 = photosUrl[3]
        self.urlPhoto5 = photosUrl[4]

        self.userStoreId = userStoreId 
        self.departmentId = departmentId 
        self.categoryId = categoryId
        self.sizeId = sizeId 
        self.productStateId = productStateId
        self.weightUnitId = weightUnitId 


    def __rep__(self):
        return "Product %r>" % self.name

    def serialize(self):
        return {
            'id':self.id,
            'name': self.name,
            'price': self.price,
            'originalPrice': self.originalPrice,
            'hasBrand': self.hasBrand,
            'brand': self.brand,
            'color': self.color,
            'model': self.model,
            'weight': self.weight,
            'qty': self.qty,
            'flete': self.flete,
            'photos': [self.urlPhoto1,self.urlPhoto2,self.urlPhoto3,self.urlPhoto4,self.urlPhoto5],
            'category': self.category.serialize(),
            'userStore': self.userStore.serialize(),
            'department': self.department.serialize(),
            'size': self.size.serialize(),
            'productState': self.productState.serialize(),
            'weightUnit': self.weightUnit.serialize()

        }   

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAll():
        return Product.query.all()

    @staticmethod
    def getOneById(id):
        return Product.query.get(id)


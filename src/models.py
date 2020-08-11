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
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getOneById(id):
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

    followerId = db.Column(Integer, ForeignKey('User.id'), primary_key = True )   
    followedId = db.Column(Integer, ForeignKey('User.id'), primary_key = True)    

    createdAt = db.Column(DateTime)
    modifiedAt = db.Column(DateTime)

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
        db.session.committ()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAllFollower():
        followers = list(map(lambda follower: follower.serialize(), Follow.query.all() ))
        print('****models.Follower.followers=',followers)
        return followers

# MessageType
class MessageType(db.Model):
    __tablename__ = 'MessageType'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    createdAt = Column(DateTime)
    modifiedAt  = Column(DateTime)

    # class constructor
    def __init__(self, name):
        """
        Class constructor
        """
        self.name = name
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "MessageType %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt 
        } 

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getOneById(id):
        return MessageType.query.get(id)

    @staticmethod
    def getAll(userId):
        messageTypes = MessageType.query.all()
        return messageTypes

# MessageStatus
class MessageStatus(db.Model):
    __tablename__ = 'MessageStatus'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    createdAt = Column(DateTime)
    modifiedAt  = Column(DateTime)

    # class constructor
    def __init__(self, name):
        """
        Class constructor
        """
        self.name = name
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "MessageStatus %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt 
        } 

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getOneById(id):
        return MessageStatus.query.get(id)

    @staticmethod
    def getAll(userId):
        messageStatus = MessageStatus.query.all()
        return messageTypes



class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)

    loginId = Column(Integer, ForeignKey('Login.id'))    
    login = relationship(Login)
    photoUrl=Column(String(100), default = 'tendita.png')

    followeds = db.relationship(Follow, foreign_keys=[Follow.followerId], backref=db.backref('follower', lazy='joined'),lazy='dynamic', cascade='all, delete-orphan')
    
    followers = db.relationship(Follow, foreign_keys=[Follow.followedId], backref=db.backref('followed', lazy='joined'),lazy='dynamic', cascade='all, delete-orphan')

    receivers = db.relationship("UserMessage", foreign_keys="UserMessage.senderId", backref=db.backref('senderUser', lazy='joined'),lazy='subquery', cascade='all, delete-orphan')
        
    senders = db.relationship("UserMessage", foreign_keys="UserMessage.receiverId", backref=db.backref('receiverUser', lazy='joined'),lazy='subquery', cascade='all, delete-orphan')


    userStore = db.relationship("UserStore", backref="User", lazy=True, uselist=False)

    birthDate = db.Column(DateTime)
    nationalId = db.Column(String(9)) #, unique=True)
    phone = db.Column(String(20))
    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)
    active = db.Column(Boolean, default=True)

    # class constructor
    def __init__(self, name, loginId, photoUrl, active, birthDate, phone, nationalId):
        """
        Class constructor
        """
        self.name = name
        self.loginId = loginId
        self.photoUrl = photoUrl
        self.active = active
        self.birthDate = birthDate
        self.nationalId = nationalId
        self.phone = phone
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "User %r>" % self.name

    def serialize(self):
        birthDate = self.birthDate
        if birthDate == None:
            birthDate=''
        else:
            birthDate = birthDate.strftime('%d/%m/%Y')

        nationalId = self.nationalId
        if nationalId == None:
            nationalId=''

        phone = self.phone
        if phone == None:
            phone = ''    

        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize(),
            'photoUrl': self.photoUrl,
            'active': self.active,
            'birthDate': birthDate,
            'nationalId': nationalId,
            'phone': phone,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        } 

    def serialize_with_userStore(self):
        print('****Login.serialize_with_user:', self.userStore)
        birthDate = self.birthDate
        if birthDate == None:
            birthDate=''

        nationalId = self.nationalId
        if nationalId == None:
            nationalId=''

        phone = self.phone
        if phone == None:
            phone = '' 

        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize(),
            'photoUrl': self.photoUrl,
            'active': self.active,
            'birthDate': birthDate,
            'nationalId': nationalId,
            'phone': phone,
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
            'birthDate': self.birthDate,
            'nationalId': self.nationalId,
            'phone': self.phone,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        }    

    def serialize_with_userMessages(self):
        print('****User.serialize_with_userMessages.self.receivers:', self.receivers.all())
        print('****User.serialize_with_userMessages.self.senders:', self.senders.all())
        receivers = list(map(lambda receiver: receiver.serialize(), self.receivers.all()))
        senders = list(map(lambda sender: sender.serialize(), self.senders.all()))
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize(),
            'photoUrl': self.photoUrl,
            'receivers': receivers,
            'senders': senders,
            'active': self.active,
            'birthDate': self.birthDate,
            'nationalId': self.nationalId,
            'phone': self.phone,
            'createdAt': self.createdAt,
            'modifiedAt': self.modifiedAt
        }    

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.session.committ()

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


# UserMessage
class UserMessage(db.Model):
    __tablename__ = 'UserMessage'
    id = Column(Integer, primary_key=True)
    senderId = db.Column(Integer, ForeignKey(User.id), nullable = False)   
    receiverId = db.Column(Integer, ForeignKey(User.id), nullable = False)    
    messageTypeId = db.Column(Integer, ForeignKey(MessageType.id), nullable = False)    
    messageStatusId = db.Column(Integer, ForeignKey(MessageStatus.id), nullable = False)

    messageType = relationship(MessageType, lazy='select')
    messageStatus = relationship(MessageStatus, lazy='select')

    message = db.Column(String(250), nullable = False)
    link = db.Column(String(250))

    sender = db.relationship("User", foreign_keys=[senderId])
    receiver = db.relationship("User", foreign_keys=[receiverId])


    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)


    # class constructor
    def __init__(self, senderId, receiverId, messageTypeId, messageStatusId, message, link):
        """
        Class constructor
        """
        self.senderId = senderId
        self.receiverId = receiverId
        self.messageTypeId = messageTypeId
        self.messageStatusId = messageStatusId
        self.message = message
        self.link = link
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()
#        self.sender = db.relationship("User", foreign_keys=[UserMessage.senderId])
#        self.receiver = db.relationship("User", foreign_keys=[UserMessage.receiverId])


    def __rep__(self):
        return "UserMessage %r>" % self.id

    def serialize(self):
        createdAt = self.createdAt
        if createdAt == None:
            createdAt=''
        else:
            createdAt = createdAt.strftime('%d/%m/%Y %H:%M:%S')

        return {
            'id': self.id,
            'senderId': self.senderId,
            'receiverId': self.receiverId,
            'sender': self.sender.serialize(),
            'receiver': self.receiver.serialize(),
            'messageType': self.messageType.serialize(),
            'messageStatus': self.messageStatus.serialize(),
            'message': self.message,
            'link': self.link,
            'createdAt': createdAt,
            'modifiedAt': self.modifiedAt             
        }        

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.session.committ()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def getOneBy(id):
        return UserMessage.query.get(id)

    @staticmethod
    def getAllByReceivedId(userId):
        userMessages = UserMessage.query.filter_by(receiverId=userId).all()
        return userMessages

    @staticmethod
    def getAll():
        userMessages = UserMessage.query.all()
        return userMessages



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

    regionId = Column(Integer, ForeignKey('Region.id'), nullable = True)
    region = relationship(Region)

    likes = Column(Integer, default=0)
    title = Column(String(100))
    bio = Column(String(200))
    url = Column(String(100))
    photoUrl = Column(String(100), default = 'tendita.png') 
    solds = Column(Integer, default=0)
    sells = Column(Integer, default=0) 

    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)

    #products = relationship("Product", backref="UserStore", lazy=True, uselist=False)
    products = relationship("Product", backref="UserStore", lazy=True)

    # class constructor
    def __init__(self, name, userId, regionId, bio, url, photoUrl):
        """
        Class constructor
        """
        self.name = name
        self.userId = userId
        self.regionId = regionId
        self.bio = bio
        self.url = url
        self.photoUrl = photoUrl
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()

    def __rep__(self):
        return "UserStore %r>" % self.name

    def serialize(self):
        region = ''
        if self.region != None:
            region=self.region.serialize()

        return {
            'id': self.id,
            'name': self.name ,
            'user': self.user.serialize(),
            'region': region,
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
        region=''
        if self.region != None:
            region=self.region.serialize()
        return {
            'id': self.id,
            'name': self.name ,
            'user': self.user.serialize(),
            'region': region,
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
        db.session.committ()

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
        db.session.committ()

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

    createdAt = db.Column(DateTime)
    modifiedAt  = db.Column(DateTime)

    # class constructor
    def __init__(self, name, price, originalPrice, flete, hasBrand, brand, color, model, weight, qty, photosUrl, userStoreId, departmentId, categoryId, sizeId, productStateId, weightUnitId):
        """
        Class constructor
        """
        print('#####Product.__init__','userStoreId=', userStoreId, ', name=', name, ', brand=', brand, ', model=', model, ', color=', color, ', hasBrand=', hasBrand,', price=', price, ', originalPrice=', originalPrice, ', qty=', qty, ', weight=', weight, ', flete=', flete,', photosUrl=', photosUrl, ', userStoreId=', userStoreId, ', departmentId=', departmentId, ', categoryId=', categoryId, ', sizeId=',sizeId, ', productStateId=', productStateId, ', weightUnitId=', weightUnitId)


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
        self.createdAt = datetime.datetime.utcnow()
        self.modifiedAt = datetime.datetime.utcnow()


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
            'categoryId': self.category.id,
            'userStoreId': self.userStore.id,
            'departmentId': self.department.id,
            'sizeId': self.size.id,
            'productStateId': self.productState.id,
            'weightUnitId': self.weightUnit.id,            
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

    def update(self, name, price, originalPrice, flete, hasBrand, brand, color, model, weight, qty, photosUrl, userStoreId, departmentId, categoryId, sizeId, productStateId, weightUnitId):
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
        self.userStoreId = userStoreId 
        self.departmentId = departmentId 
        self.categoryId = categoryId
        self.sizeId = sizeId 
        self.productStateId = productStateId
        self.weightUnitId = weightUnitId 
        self.modifiedAt = datetime.datetime.utcnow()

        if photosUrl[0]:
            self.urlPhoto1 = photosUrl[0]
        if photosUrl[1]:
            self.urlPhoto2 = photosUrl[1]
        if photosUrl[2]:    
            self.urlPhoto3 = photosUrl[2]
        if photosUrl[3]:
            self.urlPhoto4 = photosUrl[3]
        if photosUrl[4]:
            self.urlPhoto5 = photosUrl[4]

        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAll():
        return Product.query.all()

    @staticmethod
    def getOneById(id):
        print('models.Product.getOneById.id=', id)
        product = Product.query.get(id)
        print('models.Product.getOneById.product=', product)
        return product


class Cart(db.Model):
    __tablename__ = 'Cart'
    id = Column(Integer, primary_key=True)

    userId = Column(Integer, ForeignKey('User.id'))
    user = relationship(User)

    def __rep__(self):
        return "Cart %r>" % self.id

    def serialize(self):
        return {
            "id": self.id,
            "User": self.user.serialize()
        }   

class CartProduct(db.Model):
    __tablename__ = 'CartProduct'
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    amount = Column(Integer)

    cartId = Column(Integer, ForeignKey('Cart.id'))
    cart = relationship(Cart)

    productId = Column(Integer, ForeignKey('Product.id'))
    product = relationship(Product)

    def __rep__(self):
        return "CartProduct %r>" % self.id

    def serialize(self):
        return {
            "id": self.id,
            "price": self.price,
            "amount": self.amount,
            "Cart": self.cart.serialize(),
            "Product": self.product.serialize(),
            'productState': self.productState.serialize(),
            'weightUnit': self.weightUnit.serialize()
        }   

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.modifiedAt = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def getAll():
        return Product.query.all()

    @staticmethod
    def getOneById(id):
        return Product.query.get(id)


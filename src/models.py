from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, event

from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

db = SQLAlchemy()

class Login(db.Model):
    __tablename__ = 'Login'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(50), unique=True)

    def __rep__(self):
        return "Login %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email    
        }        


class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)

    loginId = Column(Integer, ForeignKey('Login.id'))    
    login = relationship(Login)

    def __rep__(self):
        return "User %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login.serialize()  
        }        

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

    def __rep__(self):
        return "UserStore %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name ,
            'user': self.user.serialize(),
            'region': self.region.serialize()
        }        

class Department(db.Model):
    __tablename__ = 'Department'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __rep__(self):
        return "Department %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name    
        }   

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
    id = Column(Integer, primary_key=True)

    name = Column(String(50), nullable = False)
    price = Column(Float,nullable = False)
    originalPrice = Column(Float, nullable = False)
    flete = Column(Float, nullable = False)
    hasBrand = Column(Boolean, nullable = False)
    brand = Column(String(50))
    color = Column(String(50))
    model = Column(String(50))
    weight = Column(Float, nullable = False)

    qty = Column(Integer, nullable=False)
    urlPhoto1 = Column(String(150))
    urlPhoto2 = Column(String(150))
    urlPhoto3 = Column(String(150))
    urlPhoto4 = Column(String(150))
    urlPhoto5 = Column(String(150))

    userStoreId = Column(Integer, ForeignKey('UserStore.id'))
    userStore = relationship(UserStore) 

    departmentId = Column(Integer, ForeignKey('Department.id'))
    department = relationship(Department) 

    categoryId = Column(Integer, ForeignKey('Category.id'))
    category = relationship(Category) 

    sizeId = Column(Integer, ForeignKey('Size.id'))
    size = relationship(Size) 

    productStateId = Column(Integer, ForeignKey('ProductState.id'))
    productState = relationship(ProductState) 

    weightUnitId = Column(Integer, ForeignKey('WeightUnit.id'))
    weightUnit = relationship(WeightUnit) 

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


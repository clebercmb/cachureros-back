from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean

from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

db = SQLAlchemy()

class Login(db.Model):
    __tablename__ = 'Login'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __rep__(self):
        return "Login %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "login": self.name    
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

class UserStore(db.Model):
    __tablename__ = 'UserStore'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)
    
    userId = Column(Integer, ForeignKey('User.id'))
    user = relationship(User)
    def __rep__(self):
        return "UserStore %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name ,
            'user': self.user.serialize() 
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
        return "Categoria %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name    
        }   


class SubCategory(db.Model):
    __tablename__ = 'SubCategory'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    categoryId = Column(Integer, ForeignKey('Category.id'))
    category = relationship(Category)

    def __rep__(self):
        return "SubCategoria %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "Category": self.category.serialize()
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

class Product(db.Model):
    __tablename__= 'Product'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable = False)
    brand = Column(String(50))
    model = Column(String(50))
    color = Column(String(50))
    hasBrand = Column(Boolean, nullable = False)
    price = Column(Float,nullable = False)

    condition = Column(Integer, nullable=False)
    originalPrice = Column(Float, nullable = False)
    qty = Column(Integer, nullable=False)
    weight = Column(Float, nullable = False)
    weightUnit = Column(String(2), nullable = False)
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

    subCategoryId = Column(Integer, ForeignKey('SubCategory.id'))
    subCategory = relationship(SubCategory)

    sizeId = Column(Integer, ForeignKey('Size.id'))
    size = relationship(Size)

    productStateId = Column(Integer, ForeignKey('ProductState.id'))
    productState = relationship(ProductState)

    def __rep__(self):
        return "Product %r>" % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'hasBrand': self.hasBrand,
            'price': self.price,
            'size': self.size,
            'condition': self.condition,
            'originalPrice': self.originalPrice,
            'qty': self.qty,
            'weight': self.weight,
            'weightUnit': self.weightUnit,
            'photos': [self.urlPhoto1,self.urlPhoto2,self.urlPhoto3,self.urlPhoto4,self.urlPhoto5],
            'userStore': self.userStore.serialize(),
            'department': self.department.serialize(), 
            'category': self.category.serialize(),
            'subCategory': self.subCategory.serialize(),
            'size': self.size.serialize(),
            'productState': self.productState.serialize()
        }        

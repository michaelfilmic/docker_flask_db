import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app=Flask(__name__)
app.run(debug=True)

# 配置数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:michael1226@database:5432/Face_Wallet_1'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:michael1226@localhost:5432/Face_Wallet_1'
# 跟踪数据库修改，不建议开启，消耗性能 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db=SQLAlchemy(app)
db.init_app(app)
# 数据库模型需要继承db.Model
class Customer(db.Model):
   # 定以表名
   __tablename__= 'test_docker'
   # 定以字段
   # db.Column表示一个字段
   id = db.Column(db.String(50),primary_key=True)
   first_name = db.Column(db.String(50),nullable=False)
   last_name=db.Column(db.String(50),nullable=False)
   phone_number=db.Column(db.String(15),nullable=False,unique=True)
   account_number=db.Column(db.String(16),nullable=False)
   account_cvv=db.Column(db.String(3),nullable=False)
   account_date=db.Column(db.String(4),nullable=False)
   email=db.Column(db.String(50),unique=True,nullable=True)

@app.route('/')
def index():
   db.drop_all()
   db.create_all()
   # 添加用户
   customer1=Customer(id='400065323',first_name='Bohui',last_name='Yu',phone_number='6479365120',account_number='1234123412341234',account_cvv='123',account_date='0922',email='yub14@mcmaster.ca')
   customer2=Customer(id='400050636',first_name='Weike',last_name='Shi',phone_number='647936666',account_number='1234123412341234',account_cvv='456',account_date='0922',email='shiw14@mcmaster.ca')
   customer3=Customer(id='1',first_name='HMichael',last_name='Ma',phone_number='6479365555',account_number='1234123412341234',account_cvv='123',account_date='0922',email='mah16@mcmaster.ca')
   customer4=Customer(id='400104626',first_name='Yunan',last_name='Zhou',phone_number='6479365111',account_number='1234123412341234',account_cvv='123',account_date='0922',email='zhouy142@mcmaster.ca')
   db.session.add_all([customer1,customer2,customer3,customer4])
   db.session.commit()
   #cust1 = Customer.query.get(1)
   show_compare = []
   cust2 = Customer.query.filter().all()
   for item in cust2:
      show_compare.append(item.id)
   cust1 = Customer.query.count()
   print(cust1)
   return 'san' + str(cust1) + str(show_compare)
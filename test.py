# from faker import Faker
# from data.users import User
# from data import db_session
# db_session.global_init('db/db.sqlite')
# db = db_session.create_session()
#
# f = Faker('RU')
# for i in range(10):
# 	user = User()
# 	user.name = f.name()
# 	user.email = f.email()
# 	user.status = 'Учащийся'
# 	user.about = ''
# 	user.set_password(f.password())
# 	db.add(user)
# 	db.commit()

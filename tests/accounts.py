from . import fake

super_admin_2 = {"email": fake.email(), "password": fake.text(),
                 "user_type": "super-admin"}
admin_one = {"email": fake.email(), "password": fake.text(),
             "user_type": "admin"}
user_one = {"email": fake.email(), "password": fake.text(),
            "user_type": "user"}

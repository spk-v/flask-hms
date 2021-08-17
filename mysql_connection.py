import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
    database = "webapp"
)
mycursor = mydb.cursor()
sql3 = "select date from doctor_patient_relation"
mycursor.execute(sql3)
myresult3 = mycursor.fetchall()
print(myresult3)
print(mydb)
# mycursor = mydb.cursor()
# # # mycursor.execute("CREATE TABLE IF NOT EXISTS customers1 (name VARCHAR(255), address VARCHAR(255))")
# # # mycursor.execute("CREATE TABLE IF NOT EXISTS Patient_details (name VARCHAR(255),username VARCHAR(255),mobile NUMBER,email VARCHAR(255), age number,password VARCHAR(255))")
# # # mycursor.execute("CREATE DATABASE mydatabase")
# # # sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# # # val = ("am", "Highway 3")
# # # mycursor.execute(sql, val)
# # #
# # # mydb.commit()
# # #
# # # print(mycursor.rowcount, "record inserted.")
# # name = "John"
# # sql = "SELECT * FROM customers "
# # mycursor.execute(sql)
# #
# # myresult = mycursor.fetchall()
# # print(len(myresult))
# # for x in myresult:
# #     x1 = list(x)
# #
# #     print(x1)
# #
# # # sql = "SELECT * FROM customers ORDER BY name"
# # #
# # # mycursor.execute(sql)
# # #
# # # myresult = mycursor.fetchall()
# # #
# # # for x in myresult:
# # #   print(x)
#
# from cryptography.fernet import Fernet
#
# # we will be encryting the below string.
# message = "hello geeks"
#
# # generate a key for encryptio and decryption
# # You can use fernet to generate
# # the key or use random key generator
# # here I'm using fernet to generate key
#
# key = Fernet.generate_key()
# key2 = Fernet.generate_key()
# # Instance the Fernet class with the key
# fernet2 = Fernet(key2)
#
# fernet = Fernet(key)
#
# # then use the Fernet class instance
# # to encrypt the string string must must
# # be encoded to byte string before encryption
# encMessage = fernet2.encrypt(message.encode())
# print("Key  ", key)
# print("Key  ", key2)
# print("original string: ", message)
# print("encrypted string: ", encMessage)
#
# # decrypt the encrypted string with the
# # Fernet instance of the key,
# # that was used for encrypting the string
# # encoded byte string is returned by decrypt method,
# # so decode it to string with decode methos
# decMessage = fernet2.decrypt(encMessage).decode()
#
# print("decrypted string: ", decMessage)
# from passlib.hash import sha256_crypt
#
# password = sha256_crypt.encrypt("password257")
# password2 = sha256_crypt.encrypt("password")
#
# print(password)
# print(password2)
#
# print(sha256_crypt.verify("password", password))
# import hashlib
# import os
#
# import hmac
#
# # password = "!Example secure password!"
# # password = password.encode()
# # salt = os.urandom(16)
# # password_hash = hashlib.pbkdf2_hmac("sha256", password, salt, 100000)
# #
# # print(password_hash)
# # correct_password = "!Example secure password!25"
# # encoded_correct_password = hashlib.pbkdf2_hmac("sha256", correct_password.encode(), salt, 100000)
# # print(hmac.compare_digest(password_hash, encoded_correct_password))
# #
# password2 = "!Example secure password!"
# password2 = password2.encode()
# salt2 = os.urandom(28)
# print("salt2 ",salt2)
# password_hash2 = hashlib.pbkdf2_hmac("sha256", password2, salt2, 100000)
#
# print(password_hash2)
# correct_password2 = "!Example secure password!"
# salt3 = os.urandom(28)
# string = str(salt3)
# salt3 = bytes(salt3)
# print("salt3 ",type(salt3))
# encoded_correct_password2 = hashlib.pbkdf2_hmac("sha256", correct_password2.encode(), salt3, 100000)
# print(hmac.compare_digest(password_hash2, encoded_correct_password2))
#
#
# # correct_password = password
# # sql2 = "select pat_salt_key from pat_hash where pat_email = '"+email+"'"
# # mycursor.execute(sql2)
# # myresult1 = mycursor.fetchall()
# # salt_key_get = myresult1[0][0]
# # print(salt_key_get)
# # print(type(salt_key))
# # sql3 = "select password from patient_details where email = '" + email + "'"
# # mycursor.execute(sql3)
# # myresult3 = mycursor.fetchall()
# # password_hashed = myresult3[0][0]
# # encoded_correct_password = hashlib.pbkdf2_hmac("sha256", correct_password.encode(),salt_key_get, 100000)
# # print(" true or false",hmac.compare_digest(password_hashed, encoded_correct_password))
# import json
# import random
# import string
# from pathlib import Path

# class Bank:
#     database = Path(__file__).parent / "data.json"
#     data = []

#     try:
#         if Path(database).exists():
#             with open(database) as fs:
#                 data = json.load(fs.read())
#         else:
#             print("No such file exists")

#     except Exception  as e:
#         print(f"An error occured as {e}")

#     @classmethod
#     def __update(cls):
#         with open(cls.database, 'w') as fs:
#             fs.write(json.dumps(Bank.data))

#     @classmethod
#     def __accountgenerate(cls):
#         alpha = random.choices(string.ascii_letters,k = 3)
#         num = random.choices(string.digits,k = 3)
#         spchar = random.choices("!@#%^&*",k = 1)
#         id = alpha + num + spchar
#         random.shuffle(id)
#         return "".join(id)

        

#     def Createaccount(self):
#         info = {
#             "name" : input("Tell your good name:-"),
#             "age" : int(input("Tell your age:-")),
#             "email" : input("Enter your personal email:-"),
#             "pin" : int(input("Enter your 4 number pin:-")),
#             "accountNo." : Bank.__accountgenerate(),
#             "balance" : 0
#         }

#         if info['age'] < 18 or len(str(info['pin'])) != 4:
#             print("You can't create anccount")

#         else:
#             print("Account has been created successfully")

#             for i in info:
#                 print(f"{i} : {info[i]}")
#             print("Please note down your account number")

#             Bank.data.append(info)
#             Bank.__update()


#     def depositmoney(self):
#         accnumber = input("Tell your account number:- ")
#         pin = int(input("Please tell your pin:- "))

#         userdata = [i for i in Bank.data if i['accountNo.'] == 'accnumber' and i['pin'] == 'pin']

#         if userdata == False:
#             print("Sorry no data found")

#         else:
#             amount = int(input("Enter the amount you want to deposit:- "))
#             if amount > 10000 or amount < 100:
#                 print("Sorry we can't deposit that much amount you can deposit less then 10000 and above than 100. ")

#             else:
                
#                 userdata[0]['balance'] += amount
#                 Bank.__update()
#                 print("Amount deposited successfully")


#     def withdrawmoney(self):
#             accnumber = input("Tell your account number:- ")
#             pin = int(input("Please tell your pin:- "))
    
#             userdata = [i for i in Bank.data if i['accountNo.'] == 'accnumber' and i['pin'] == 'pin']
    
#             if userdata == False:
#                 print("Sorry no data found")
    
#             else:
#                 amount = int(input("Enter the amount you want to withdraw:- "))
#                 if userdata[0]['balance'] < amount :
#                     print("Sorry You don't have that much money.")
    
#                 else:
                    
#                     userdata[0]['balance'] -= amount
#                     Bank.__update()
#                     print("Amount withdrew successfully")


#     def details(self):
#         accnumber = input("Enter your account number:-")
#         pin = int(input("Please enter your pin:-"))

#         userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] ==  pin]
#         print("Your information are\n\n\n")

#         for i in userdata[0]:
#             print(f"{i} : {userdata[0][i]}")


#     def updatedetails(self):
#         accnumber = input("Enter your account number:-")
#         pin = int(input("Please enter your pin:-"))

#         userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

#         if userdata == False:
#             print("No user data found")

#         else:
#             print("You can't change age,, account number and balance")

#             print("Fill the details for change or leave it empty if no change")

#             newdata = {
#                 "name" : input("Please enter new name or press enter:- "),
#                 "email" : input("Please enter new email:- "),
#                 "pin" :input("Please enter new pin or press enter  to skip")
#             }

#             if newdata["name"] == "":
#                 newdata["name"] = userdata[0]["name"]

#             if newdata["email"] == "":
#                 newdata["email"] = userdata[0]["email"]

#             if newdata["pin"] == "":
#                 newdata["pin"] = userdata[0]["pin"]


#             newdata['age'] = userdata[0]['age']
#             newdata['accountNo.'] = userdata[0]['accountNo.']
#             newdata['balance'] = userdata[0]['balance']

#             if type(newdata['pin']) == str:
#                 newdata['pin'] = int(newdata['pin'])


#             for i in newdata:
#                 if newdata[i] == userdata[0][i]:
#                     continue

#                 else:
#                     userdata[0][i] = newdata[i]

#             Bank.__update()
#             print("Data updated successfully")


#     def delete(self):
#         accnumber = input("Enter your account number:-")
#         pin = int(input("Please enter your pin:-"))

#         userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

#         if userdata == False:
#             print("Sorry no such data found")

#         else:
#             check = input("Press y if you want delete account or press n:- ")

#             if check == 'n' or check == 'N':
#                 print("Bypassed")

#             else:
#                 index = Bank.data.index(userdata[0])
#                 Bank.data.pop(index)
#                 print("Account deleted successfully")

#                 Bank.__update()
        


 
# user = Bank()
# print("Press 1 to create an account")
# print("Press 2 to deposit money in the bank")
# print("Press 3 to withdraw money")
# print("Press 4 for details")
# print("Press 5 for updating the files")
# print("Press 6 for deleting your account")

# check = int(input("Enter your response:"))

# if check == 1:
#     user.Createaccount()

# if check == 2:
#     user.depositmoney()

# if check == 3:
#     user.withdrawmoney()

# if check == 4:
#     user.details()

# if check == 5:
#     user.updatedetails()

# if check == 6:
#     user.delete()

import json 
import random
import string 
from pathlib import Path 


class Bank:
    database = Path(__file__).parent /'data.json'
    data = []
    
    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            print("no such file exist ")
    except Exception as err:
        print(f"an exception occured as {err}")
    
    @classmethod
    def __update(cls):
        with open(cls.database,'w') as fs:
            fs.write(json.dumps(Bank.data))

    @classmethod
    def __accountgenerate(cls):
        alpha = random.choices(string.ascii_letters,k = 3)
        num = random.choices(string.digits,k= 3)
        spchar = random.choices("!@#$%^&*",k = 1)
        id = alpha + num + spchar
        random.shuffle(id)
        return "".join(id)



    def Createaccount(self):
        info = {
            "name": input("Tell your name :- "),
            "age" : int(input("tell your age :- ")),
            "email": input("tell your email :- "),
            "pin": int(input("tell your 4 number pin :- ")),
            "accountNo." : Bank.__accountgenerate(),
            "balance" : 0
        }
        if info['age'] < 18  or len(str(info['pin'])) != 4:
            print("sorry you cannot create your account")
        else:
            print("account has been created successfully")
            for i in info:
                print(f"{i} : {info[i]}")
            print("please note down your account number")

            Bank.data.append(info)

            Bank.__update()
        
    def depositmoney(self):
        accnumber = input("please tell your account number ")
        pin = int(input("please tell your pin aswell "))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

        if userdata == False:
            print("soory no data found")
        
        else:
            amount = int(input("how much you want to depoit "))
            if amount  > 10000 or amount < 0:
                print("sorry the amount is too much you can deposit below 10000 and above 0")

            else:
                userdata[0]['balance'] += amount
                Bank.__update()
                print("Amount deposited successfully ")
    

    def withdrawmoney(self):
        accnumber = input("please tell your account number ")
        pin = int(input("please tell your pin aswell "))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

        if userdata == False:
            print("soory no data found")
        
        else:
            amount = int(input("how much you want to withdraw "))
            if userdata[0]['balance']  < amount:
                print("soory you dont have that much money")
              
            else:
                
                userdata[0]['balance'] -= amount
                Bank.__update()
                print("Amount withdrew successfully ")


    def showdetails(self):

        accnumber = input("please tell your account number ")
        pin = int(input("please tell your pin aswell "))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]
        print("your information are \n\n\n")
        for i in userdata[0]:
            print(f"{i} : {userdata[0][i]}")



    def updatedetails(self):
        accnumber = input("please tell your account number ")
        pin = int(input("please tell your pin aswell "))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

        if userdata == False:
            print("no such user found ")
        
        else:
            print("you cannot change the age, account number, balance")

            print("Fill the details for change or leave it empty if no change")

            newdata = {
                "name": input("please tell new name or press enter : "),
                "email":input("please tell your new Email or press enter to skip :"),
                "pin": input("enter new Pin or press enter to skip: ")
            }

            if newdata["name"] == "":
                newdata["name"] = userdata[0]['name']
            if newdata["email"] == "":
                newdata["email"] = userdata[0]['email']
            if newdata["pin"] == "":
                newdata["pin"] = userdata[0]['pin']
            
            newdata['age'] = userdata[0]['age']

            newdata['accountNo.'] = userdata[0]['accountNo.']
            newdata['balance'] = userdata[0]['balance']
            
            if type(newdata['pin']) == str:
                newdata['pin'] = int(newdata['pin'])
            

            for i in newdata:
                 if newdata[i] == userdata[0][i]:
                     continue
                 else:
                     userdata[0][i] = newdata[i]

            Bank.__update()
            print("details updated successfully")


    def Delete(self):
        accnumber = input("please tell your account number ")
        pin = int(input("please tell your pin aswell "))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

        if userdata == False:
            print("sorry no such data exist ")
        else:
            check = input("press y if you actually want to delete the account or press n")
            if check == 'n' or check == "N":
                print("bypassed")
            else:
                index = Bank.data.index(userdata[0])
                Bank.data.pop(index)
                print("account deleted successfully ")
                Bank.__update()

            

user = Bank()
print("press 1 for creating an account")
print("press 2 for Deposititing the money in the bank ")
print("press 3 for withdrawing the money ")
print("press 4 for details ")
print("press 5 for updating the details")
print("press 6 for deleting your account")

check = int(input("tell your response :- "))

if check == 1:
    user.Createaccount()

if check == 2:
    user.depositmoney()

if check == 3:
    user.withdrawmoney()

if check == 4:
    user.showdetails()

if check == 5:
    user.updatedetails()

if check == 6:
    user.Delete()
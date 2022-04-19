from requests import post

print(post("http://127.0.0.1:5000/neriuulf7vw9da4dp316cmlq/users", json={
    "name": "Danila-admin",
    "link": "bc9im1uqxldsada",
    "id": "1000",
    "email": "silnovdanila7@gmail.com",
    "authentication": True,
    "admin": "2",
    "password": "66786nbv",
    "avatar": "ONe"
}).json())

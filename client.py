from digicubes.testclient import DigiCubeServer, UserProxy

if __name__ == '__main__':    
    DigiCubeServer.init('http://localhost:5042')
    org = DigiCubeServer.Org

    """
    user = org.get_user(2031055, links=True) #links=False, filtered_fields=('login','firstName')
    if user is not None:
        user.firstName = 'Meister'
        user.delete()
    """
    user = org.new_user()
    user.login="klaasie.002"
    user.firstName = 'Gabi'
    user.lastName = 'Köster'
    user.create()
    user.delete()

    for user in org.get_users():
        print(user)
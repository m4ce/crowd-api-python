# Atlassian Crowd Python API
This is a simple Python API that allows to interact with the Crowd REST API.

The API currently supports the following:

* Create users
* Create groups
* Add users to groups
* Manage users attributes
* Retrieve user details
* Retrieve user groups

Pull requests to add additional API features (as documented at https://developer.atlassian.com/display/CROWDDEV/Crowd+REST+Resources) are very welcome. I only implemented what I needed.

## Usage
```
from crowd import CrowdAPI
crowd = CrowdAPI(api_url = "https://<uri>/crowd/rest/usermanagement/latest", app_name = "crowd", app_password = "secure")

# If the password attribute is not specified, a random one will be generated and returned by create_user()
req = crowd.create_user(name = "foobar", "first-name" = "Foo", "last-name" = "Bar", "display-name" = "Foo Bar", "email" = "foo@bar.com")
if req['status']:
  print "Created, password is " + req['password']

req = crowd.get_user(username = "foobar")
if req['status']:
  print req['user']

req = crowd.set_user_attribute(username = "foobar", attribute_name = "custom", attribute_value = "great!")
if req['status']:
  print "Attribute created"

req = crowd.create_group(name = "users", description = "All users")
if req['status']:
  print "Group created"

req = crowd.add_user_to_group(username = "foorbar", groupname = "users")
if req['status']:
  print "Added!"

req = crowd.get_user_groups(username = "foobar")
if req['status']:
  print "Groups are " + req['groups']
```

## Examples
Under the examples directory, there's an example which implements bulk users creation.

## Contact
Matteo Cerutti - matteo.cerutti@hotmail.co.uk

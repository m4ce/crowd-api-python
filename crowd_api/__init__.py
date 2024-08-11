#
# crowd.py
#
# Author: Matteo Cerutti <matteo.cerutti@hotmail.co.uk>
#

import requests
import json
import random
import string
from urllib.parse import urlencode


class CrowdAPI:
    def __init__(self, **kwargs):
        if 'api_url' not in kwargs:
            raise ValueError("Crowd API URL must be given")

        self.api_url = kwargs['api_url']

        if 'app_name' not in kwargs:
            raise ValueError("Crowd API application name must be given")

        if 'app_password' not in kwargs:
            raise ValueError("Crowd API application password must be given")

        self.auth = (kwargs['app_name'], kwargs['app_password'])

        if 'verify_ssl' not in kwargs:
            self.verify_ssl = False
        else:
            self.verify_ssl = kwargs['verify_ssl']

        if 'timeout' not in kwargs:
            self.timeout = 10
        else:
            self.timeout = kwargs['timeout']

    def api_get(self, query):
        req = requests.get(self.api_url + query, headers={"Content-Type": "application/json",
                                                          "Accept": "application/json"}, auth=self.auth, verify=self.verify_ssl, timeout=self.timeout)
        return req

    def api_post(self, query, data):
        req = requests.post(self.api_url + query, headers={"Content-Type": "application/json", "Accept": "application/json"},
                            auth=self.auth, data=json.dumps(data), verify=self.verify_ssl, timeout=self.timeout)
        return req
    
    def api_put(self, query, data):
        req = requests.put(self.api_url + query, headers={"Content-Type": "application/json", "Accept": "application/json"},
                            auth=self.auth, data=json.dumps(data), verify=self.verify_ssl, timeout=self.timeout)
        return req

    def api_delete(self, query, data):
        req = requests.delete(self.api_url + query, headers={"Content-Type": "application/json", "Accept": "application/json"},
                              auth=self.auth, data=json.dumps(data), verify=self.verify_ssl, timeout=self.timeout)
        return req

    def get_user(self, **kwargs):
        if "username" not in kwargs:
            raise ValueError("Must pass username")

        req = self.api_get(
            "/user?username={}&expand=attributes".format(kwargs['username']))
        if req.status_code == 200:
            return {"status": True, "user": req.json()}
        if req.status_code == 404:
            return {"status": False, "user": None}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_user_attributes(self, **kwargs):
        if "username" not in kwargs:
            raise ValueError("Must pass username")

        req = self.api_get("/user/attribute?username={}".format(kwargs['username']))
        if req.status_code == 200:
            return {"status": True, "Attributes": req.content}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_user_groups(self, **kwargs):
        groups = []

        if "username" not in kwargs:
            raise ValueError("Must pass username")

        req = self.api_get("/user/group/direct?username={}&max-results={}&start-index={}".format(
            kwargs['username'], kwargs.get('max_results', 1000), kwargs.get('start_index', 0)))
        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])

            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_nested_user_groups(self, **kwargs) -> dict:
        """Retrieve the group that the user is a nested member of."""
        endpoint = "/user/group/nested"

        if "username" not in kwargs:
            raise ValueError("Must pass username")

        params = {'username': kwargs['username']}

        if kwargs.get('max_results') is not None:
            params['max-results'] = kwargs.get('max_results')
        if kwargs.get('start_index') is not None:
            params['start-index'] = kwargs.get('start_index')

        query = f"{endpoint}?{urlencode(params)}"

        req = self.crowd.api_get(query)

        groups = []

        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])
            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_group_users(self, **kwargs):
        users = []

        if "groupname" not in kwargs:
            raise ValueError("Must pass username")

        req = self.api_get("/group/user/direct?groupname={}&max-results={}&start-index={}".format(
            kwargs['groupname'], kwargs.get('max_results', 1000), kwargs.get('start_index', 0)))
        if req.status_code == 200:
            for user in req.json()['users']:
                users.append(user['name'])

            return {"status": True, "users": users}
        if req.status_code == 404:
            return {"status": False, "users": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_nested_group_users(self, **kwargs):
        users = []

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        req = self.api_get(
            "/group/user/nested?groupname={}".format(kwargs['groupname']))
        if req.status_code == 200:
            for user in req.json()['users']:
                users.append(user['name'])

            return {"status": True, "users": users}
        if req.status_code == 404:
            return {"status": False, "users": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_parent_groups(self, **kwargs):
        pgroups = []

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        req = self.api_get(
            "/group/parent-group/direct?groupname={}".format(kwargs['groupname']))
        if req.status_code == 200:
            for pgroup in req.json()['groups']:
                pgroups.append(pgroup['name'])

            return {"status": True, "pgroups": pgroups}
        if req.status_code == 404:
            return {"status": False, "pgroups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_parent_groupsv2(self, **kwargs):
        groups = []

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        req = self.api_get(
            "/group/parent-group/direct?groupname={}".format(kwargs['groupname']))
        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])

            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_nested_parent_groups(self, **kwargs) -> dict:
        """Retrieve the groups that are nested parents of the specified group."""
        endpoint = "/group/parent-group/nested"

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        params = {'groupname': kwargs['groupname']}

        if kwargs.get('max_results') is not None:
            params['max-results'] = kwargs.get('max_results')
        if kwargs.get('start_index') is not None:
            params['start-index'] = kwargs.get('start_index')

        query = f"{endpoint}?{urlencode(params)}"

        req = self.crowd.api_get(query)

        groups = []
        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])
            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_direct_children_of_group(self, **kwargs) -> dict:
        """Retrieve the groups that are direct children of the specified group."""
        endpoint = "/group/child-group/direct"

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        params = {'groupname': kwargs['groupname']}

        if kwargs.get('max_results') is not None:
            params['max-results'] = kwargs.get('max_results')
        if kwargs.get('start_index') is not None:
            params['start-index'] = kwargs.get('start_index')

        query = f"{endpoint}?{urlencode(params)}"

        req = self.crowd.api_get(query)

        groups = []

        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])
            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_nested_children_of_group(self, **kwargs) -> dict:
        """Retrieve nested children of the specified group."""
        endpoint = "/group/child-group/nested"

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        params = {'groupname': kwargs['groupname']}

        if kwargs.get('max_results') is not None:
            params['max-results'] = kwargs.get('max_results')
        if kwargs.get('start_index') is not None:
            params['start-index'] = kwargs.get('start_index')

        query = f"{endpoint}?{urlencode(params)}"

        req = self.crowd.api_get(query)

        groups = []

        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])
            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_all_groups(self, **kwargs):
        groups = []

        req = self.api_get(
            "/search?entity-type=group&max-results={}&start-index={}".format(
                kwargs.get('max_results', 1000), kwargs.get('start_index', 0)))

        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])

            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def search_group(self, **kwargs):
        groups = []

        if 'restriction' not in kwargs:
            raise ValueError("You need to define a certian restriction")

        req = self.api_get(
            "/search?entity-type=group&restriction={}&max-results={}&start-index={}".format(
                kwargs['restriction'], kwargs.get('max_results', 1000), kwargs.get('start_index', 0)))

        if req.status_code == 200:
            for group in req.json()['groups']:
                groups.append(group['name'])

            return {"status": True, "groups": groups}
        if req.status_code == 404:
            return {"status": False, "groups": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_all_users(self, **kwargs):
        users = []

        req = self.api_get(
            "/search?entity-type=user&max-results={}&start-index={}".format(
                kwargs.get('max_results', 1000), kwargs.get('start_index', 0)))
        if req.status_code == 200:
            for user in req.json()['users']:
                users.append(user['name'])

            return {"status": True, "users": users}
        if req.status_code == 404:
            return {"status": False, "users": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def search_user(self, **kwargs):
        users = []

        if 'restriction' not in kwargs:
            raise ValueError("You need to define a certain restriction")

        req = self.api_get(
            "/search?entity-type=user&restriction={}&max-results={}&start-index={}".format(
                kwargs['restriction'], kwargs.get('max_results', 1000), kwargs.get('start_index', 0)))
        if req.status_code == 200:
            for user in req.json()['users']:
                users.append(user['name'])

            return {"status": True, "users": users}
        if req.status_code == 404:
            return {"status": False, "users": []}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def set_user_attribute(self, **kwargs):
        if "username" not in kwargs:
            raise ValueError("Must pass username")

        if "attribute_name" not in kwargs:
            raise ValueError("Must pass attribute_name")

        if "attribute_value" not in kwargs:
            raise ValueError("Must pass attribute_value")
        else:
            if not isinstance(kwargs['attribute_value'], list):
                kwargs['attribute_value'] = [kwargs['attribute_value']]

        req = self.api_post("/user/attribute?username={}".format(kwargs['username']), {
                            "attributes": [{"name": kwargs['attribute_name'], "values": kwargs['attribute_value']}]})
        if req.status_code == 204:
            return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def set_user_activity(self, **kwargs):
        if "username" not in kwargs:
            raise ValueError("Must pass username")

        if "active" not in kwargs:
            raise ValueError("Must pass active (true/false)")

        # fetch current user document
        user_document = self.api_get(
            "/user?username={}".format(kwargs['username'])).json()

        # set to active true/false
        user_document["active"] = kwargs['active']

        # update user object
        req = self.api_put("/user?username={}".format(kwargs['username']), user_document )
        if req.status_code == 204:
            return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def create_user(self, **kwargs):
        user = {}

        for k, v in kwargs.items():
            user[k.replace('_', '-')] = v

        if 'password' not in kwargs:
            user['password'] = {}
            user['password']['value'] = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(8))
            req_password_change = True
        else:
            req_password_change = False

        user['active'] = True

        req = self.api_post("/user", user)
        if req.status_code == 201:
            # user should change the password at their next login
            if req_password_change:
                self.set_user_attribute(
                    username=user['name'], attribute_name="requiresPasswordChange", attribute_value=True)
                return {"status": True, "password": user['password']['value']}
            else:
                return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def create_group(self, **kwargs):
        req = self.api_post(
            "/group", {"name": kwargs['name'], "type": "GROUP", "description": kwargs['description'], "active": True})
        if req.status_code == 201:
            return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def delete_group(self, **kwargs):

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        req = self.api_delete(
            "/group?groupname={}".format(kwargs['groupname']), data={})
        if req.status_code == 204:
            return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def add_user_to_group(self, **kwargs):

        if "username" not in kwargs:
            raise ValueError("Must pass username")

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        req = self.api_post(
            "/user/group/direct?username={}".format(kwargs['username']), {"name": kwargs['groupname']})
        if req.status_code == 201:
            return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def remove_user_from_group(self, **kwargs):

        if "username" not in kwargs:
            raise ValueError("Must pass username")

        if "groupname" not in kwargs:
            raise ValueError("Must pass groupname")

        req = self.api_delete(
            "/user/group/direct?username={}&groupname={}".format(kwargs['username'], kwargs['groupname']), data={})
        if req.status_code == 204:
            return {"status": True}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

    def get_group(self, **kwargs):
        req = self.api_get(
            "/group?groupname={}&expand=attributes".format(kwargs['name']))
        if req.status_code == 200:
            return {"status": True, "group": req.json()}
        else:
            return {"status": False, "code": req.status_code, "reason": req.content}

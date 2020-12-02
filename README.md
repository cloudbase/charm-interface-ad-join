# Overview

This charm interface layer allows you to request Active Directory credentials from an AD charm. These credentials can then be used to join a computer to active directory, or use those credentials to access systems which are joined to the AD forest.

# Usage

The credentials request is a dictionary of the following format:

```python
users = {
    "desired_username": [
        "desired AD group",
    ]
}
```

A practical example:

```python
@reactive.when('ad-join.connected')
def request_credentials(creds):
    with charm.provide_charm_instance() as wsgate_charm:
        creds.request_credentials(wsgate_charm.ad_users)
        wsgate_charm.assess_status()

```

And the ```ad_users``` propery is defined as:

```python
@property
def ad_users(self):
    cfg_groups = self.config["ad-groups"]
    groups = []
    if not cfg_groups:
        groups.append("Users")
    else:
        for group in cfg_groups.split(','):
            groups.append(group.strip())

    user = self.config["ad-user"] or self.name
    users = {
        user: groups
    }
    return users
```

The response from AD can be obtained like so:

```python
import charms.reactive as reactive

def credentials():
    ad_join = reactive.endpoint_from_flag(
        'ad-join.available')
    if ad_join:
        return ad_join.credentials()
    return None
```

The return value is of the following format:

```python
[
    {
        "full_username": "example@example.local",
        "username": "example",
        "password": "super secret password",
        "domain": "example.local",
        "netbios_name": "example",
    }
]
```

Where ```username``` will match the requested username by the charm.

# Copyright 2020 Cloudbase Solutions SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import yaml

import charmhelpers.core.hookenv as hookenv

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class ADCredentialsRequires(RelationBase):
    scope = scopes.GLOBAL

    # These remote data fields will be automatically mapped to accessors
    # with a basic documentation string provided.

    auto_accessors = [
        'adcredentials', 'ca-certificate-name', 'domainName',
        'netbiosname', 'password', 'username', 'suffix', 'address']

    @hook('{requires:ad-join}-relation-joined')
    def joined(self):
        self.set_state('{relation_name}.connected')
        self.update_state()

    def update_state(self):
        if self.data_complete():
            self.remove_state('{relation_name}.departed')
            self.set_state('{relation_name}.available')
        else:
            self.remove_state('{relation_name}.available')

    def credentials(self):
        ad_creds = self.adcredentials()

        if not ad_creds:
            return None
        creds = base64.b64decode(ad_creds.encode()).decode('utf-16-le')
        obj = yaml.safe_load(creds)

        if not len(obj):
            return None

        ret = []
        for user in obj:
            ret.append(
                {
                    "full_username": "%s@%s" % (user, self.domainName()),
                    "username": user,
                    "password": obj[user],
                    "domain": self.domainName(),
                    "netbios_name": self.netbiosname(),
                }
            )
        return ret

    def request_credentials(self, users):
        if type(users) is not dict:
            raise ValueError("users object must be dict containing user: [greoups]")
        encoded = base64.b64encode(
            yaml.dump(users).encode('utf-16-le')).decode()
        relation_info = {
            "users": encoded,
        }
        self.set_remote(**relation_info)
        # self.set_local(**relation_info)

    @hook('{requires:ad-join}-relation-changed')
    def changed(self):
        self.update_state()

    @hook('{requires:ad-join}-relation-{broken,departed}')
    def departed(self):
        self.remove_state('{relation_name}.available')
        self.set_state('{relation_name}.departed')

    def data_complete(self):
        data = {
            "adcredentials": self.adcredentials(),
            "domain": self.domainName(),
            "address": self.address()
        }
        return all(data.values())

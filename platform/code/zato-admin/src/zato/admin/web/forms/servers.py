# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms
from django.forms.util import ErrorList

# Zato
from zato.common.odb.model import Server

class RegisterServerForm(forms.Form):
    name = forms.CharField(min_length=1)
    address = forms.URLField(min_length=1)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        server = Server.objects.filter(name__exact=name)

        # Edit form will have the server_id populated
        if "server_id" in self.cleaned_data:
            server = server.exclude(id=server)

        if server:
            raise forms.ValidationError("Name is not unique.")

        return name

    def clean_address(self):
        address = self.cleaned_data["address"].strip().replace("https://", "").replace("http://", "").replace("/", "")
        server = Server.objects.filter(address__exact=address)

        # Edit form will have the server_id populated
        if "server_id" in self.cleaned_data:
            server = server.exclude(id=server)

        if server:
            raise forms.ValidationError("Address is not unique.")

        return address

class EditServerForm(forms.Form):
    name = forms.CharField(min_length=1, error_messages={"required": "Server's name is required"})
    address = forms.URLField(min_length=1, error_messages={"required": "Server's address is required", "invalid":"Enter a valid address"})
    server_id = forms.CharField(widget=forms.HiddenInput)

    def clean(self):

        if not "name" in self.cleaned_data:
            raise forms.ValidationError("The name entered was invalid")

        if not "address" in self.cleaned_data:
            raise forms.ValidationError("The address entered was invalid")

        server_id = self.cleaned_data["server_id"]

        name = self.cleaned_data["name"].strip()
        server = Server.objects.filter(name__exact=name).exclude(id=server_id)

        if server:
            text = "Name [%s] is not unique" % name
            self._errors["name"] = ErrorList([text])
            del self.cleaned_data["name"]

        address = self.cleaned_data["address"].strip().replace("https://", "").replace("http://", "").replace("/", "")
        server = Server.objects.filter(address__exact=address).exclude(id=server_id)

        if server:
            text = "Address [%s] is not unique" % address
            self._errors["address"] = ErrorList([text])
            del self.cleaned_data["address"]

        return self.cleaned_data

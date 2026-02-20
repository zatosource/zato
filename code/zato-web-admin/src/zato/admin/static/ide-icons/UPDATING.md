# Updating via VSCE

You have to use VSCE to update this theme in the VS marketplace.

First, to install VSCE globally onto the machine:

	npm install -g vsce

You'll need to create a Visual Studio Team Services account to publish via VSCE if you haven't already.  See here for more information: https://code.visualstudio.com/docs/tools/vscecli

Once that's done, create a publisher using:

	> vsce create-publisher [username]
	Publisher human-friendly name: [human-friendly-name]
	E-mail: [email-address]
	Personal Access Token: [PAT-created-in-VSTS-web-UI]

^ Note that the PAT needs to have Accounts set to "All accessible accounts" and Authorized Scopes set to "All scopes"

Then, each time you want to publish, use:

	> vsce publish

Note that various pieces of information from `package.json` will be used when publishing, such as the version number specified by `version`, and the icon to display in the Visual Studio Marketplace specified by `icon`.

Note that you don't actually need any Team Projects set up in Visual Studio Team Services for the publish process to work; just an account there.  The published theme should go straight into the Marketplace and should be available at:
https://marketplace.visualstudio.com/items?itemName=jez9999.vsclassic-icon-theme

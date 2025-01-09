system uses redis to cache blacklisted tokens and logged out tokens
views consist of two major blueprint with prefix of auth_views and app_views
auth_views handle auth end points and the app_view blueprints handles the general app_views
all the views can be found in \api\v1\src\views
main app entery point can be found in the api\v1\app.py
api routes -
blueprint are created in the api\v1\src\views\__init__.py file

 for a quick start 
 run make sure you have python installed 
 pip install virtual-env
 python3 -m venv  alumni-venv
 pip install --no-cache-dir -r requirements.txt
 redis-server to start redis


create a .env file and put in the smtp email data for gmail
MAIL_USERNAME=<mail name>
MAIL_PASSWORD=<mail app password>

api routes
Check the API status                          /alumni/api/v1/status                           GET, OPTIONS, HEAD   app_views.status
Index route                                   /alumni/api/v1/                                 GET, OPTIONS, HEAD   app_views.index
Return counts of all classes in storage       /alumni/api/v1/stats                            GET, OPTIONS, HEAD   app_views.storage_counts

Retrieve all users                            /alumni/api/v1/users                            GET, OPTIONS, HEAD   app_views.get_users
Retrieve a user by ID                         /alumni/api/v1/users/<user_id>                  GET, OPTIONS, HEAD   app_views.get_user
Delete a user by ID                           /alumni/api/v1/users/<user_id>                  OPTIONS, DELETE      app_views.delete_user
Create a new user                             /alumni/api/v1/users                            OPTIONS, POST        app_views.post_user
Update a user by ID                           /alumni/api/v1/users/<user_id>                  PUT, OPTIONS         app_views.update_user
Reset a user's password                       /alumni/api/v1/users/reset_password/<user_id>   PUT, OPTIONS         app_views.reset_user_password
Retrieve a user's profile                     /alumni/api/v1/users/my_profile/<user_id>       GET, OPTIONS, HEAD   app_views.get_user_profile
Calculate user's profile completion           /alumni/api/v1/users/user_profile_completion/<user_id> GET, OPTIONS, HEAD   app_views.get_user_profile_completion

Generate an invite code for group             /alumni/api/v1/alumni_groups/<group_id>/invite_code OPTIONS, POST        app_views.generate_group_invite
Retrieve user's alumni groups                 /alumni/api/v1/alumni_groups/my_groups/<user_id> GET, OPTIONS, HEAD   app_views.get_user_alumni_groups
Retrieve all alumni groups                    /alumni/api/v1/alumni_groups                    GET, OPTIONS, HEAD   app_views.get_all_alumni_groups
Retrieve an alumni group by ID                /alumni/api/v1/alumni_groups/<group_id>         GET, OPTIONS, HEAD   app_views.get_alumni_group
Create a new alumni group                     /alumni/api/v1/alumni_groups                    OPTIONS, POST        app_views.create_alumni_group
Update an alumni group by ID                  /alumni/api/v1/alumni_groups/<group_id>         PUT, OPTIONS         app_views.update_alumni_group
Delete an alumni group by ID                  /alumni/api/v1/alumni_groups/<group_id>         OPTIONS, DELETE      app_views.delete_alumni_group

Retrieve user's group memberships             /alumni/api/v1/group_members/my_groups_memberships/<user_id> GET, OPTIONS, HEAD   app_views.get_user_group_memberships
Retrieve all group members                    /alumni/api/v1/group_members                    GET, OPTIONS, HEAD   app_views.get_all_group_members
Retrieve a group member by ID                 /alumni/api/v1/group_members/<member_id>        GET, OPTIONS, HEAD   app_views.get_group_member
Retrieve all members of a group               /alumni/api/v1/alumni_groups/<group_id>/members GET, OPTIONS, HEAD   app_views.get_members_of_group
Create a new group member                     /alumni/api/v1/alumni_groups/<group_id>/members OPTIONS, POST        app_views.create_group_member

Check if a member is in a group               /alumni/api/v1/group_members/<group_id>/check/<member_id> GET, OPTIONS, HEAD   app_views.check_group_member
Update a group member by ID                   /alumni/api/v1/group_members/<member_id>        PUT, OPTIONS         app_views.update_group_member
Delete a group member by ID                   /alumni/api/v1/group_members/<member_id>        OPTIONS, DELETE      app_views.delete_group_member
Retrieve all amendments                       /alumni/api/v1/amendments                       GET, OPTIONS, HEAD   app_views.get_all_amendments

Retrieve an amendment by ID                   /alumni/api/v1/amendments/<amendment_id>        GET, OPTIONS, HEAD   app_views.get_amendment
Create a new amendment                        /alumni/api/v1/amendments                       OPTIONS, POST        app_views.create_amendment
Update an amendment by ID                     /alumni/api/v1/amendments/<amendment_id>        PUT, OPTIONS         app_views.update_amendment
Delete an amendment by ID                     /alumni/api/v1/amendments/<amendment_id>        OPTIONS, DELETE      app_views.delete_amendment

Retrieve all contract members                 /alumni/api/v1/contract_members                 GET, OPTIONS, HEAD   app_views.get_all_contract_members
Retrieve a contract member by ID              /alumni/api/v1/contract_members/<member_id>     GET, OPTIONS, HEAD   app_views.get_contract_member
Create a new contract member                  /alumni/api/v1/contract_members                 OPTIONS, POST        app_views.create_contract_member
Update a contract member by ID                /alumni/api/v1/contract_members/<member_id>     PUT, OPTIONS         app_views.update_contract_member
Delete a contract member by ID                /alumni/api/v1/contract_members/<member_id>     OPTIONS, DELETE      app_views.delete_contract_member

Retrieve all insurance packages               /alumni/api/v1/insurance_packages               GET, OPTIONS, HEAD   app_views.get_all_insurance_packages
Retrieve an insurance package by ID           /alumni/api/v1/insurance_packages/<package_id>  GET, OPTIONS, HEAD   app_views.get_insurance_package_by_id
Create a new insurance package                /alumni/api/v1/insurance_packages               OPTIONS, POST        app_views.create_insurance_package
Update an insurance package by ID             /alumni/api/v1/insurance_packages/<package_id>  PUT, OPTIONS         app_views.update_insurance_package
Delete an insurance package by ID             /alumni/api/v1/insurance_packages/<package_id>  OPTIONS, DELETE      app_views.delete_insurance_package

Retrieve all payments by user                 /alumni/api/v1/payments/users_payments/<user_id> GET, OPTIONS, HEAD   app_views.get_users_payments
Retrieve all payments                         /alumni/api/v1/payments                         GET, OPTIONS, HEAD   app_views.get_all_payments
Retrieve a payment by ID                      /alumni/api/v1/payments/<payment_id>            GET, OPTIONS, HEAD   app_views.get_payment
Create a new payment                          /alumni/api/v1/payments                         OPTIONS, POST        app_views.create_payment
Update a payment by ID                        /alumni/api/v1/payments/<payment_id>            PUT, OPTIONS         app_views.update_payment
Delete a payment by ID                        /alumni/api/v1/payments/<payment_id>            OPTIONS, DELETE      app_views.delete_payment
Serve a previously uploaded file              /alumni/api/v1/uploads/<filename>               GET, OPTIONS, HEAD   app_views.serve_file
Delete a previously uploaded file             /alumni/api/v1/uploads/<id>/<filename>          OPTIONS, DELETE      app_views.delete_file
Download a file                               /alumni/api/v1/download/<filename>              GET, OPTIONS, HEAD   app_views.download_file

Retrieve all payment methods                  /alumni/api/v1/payment_methods                  GET, OPTIONS, HEAD   app_views.get_all_payment_methods
Retrieve a payment method by ID               /alumni/api/v1/payment_methods/<payment_method_id> GET, OPTIONS, HEAD   app_views.get_payment_method
Create a new payment method                   /alumni/api/v1/payment_methods                  OPTIONS, POST        app_views.create_payment_method
Update a payment method by ID                 /alumni/api/v1/payment_methods/<payment_method_id> PUT, OPTIONS         app_views.update_payment_method
Delete a payment method by ID                 /alumni/api/v1/payment_methods/<payment_method_id> OPTIONS, DELETE      app_views.delete_payment_method

Retrieve contracts for a user                 /alumni/api/v1/contracts/my_contracts/<string:user_id> GET, OPTIONS, HEAD   app_views.get_contracts_for_user
Retrieve all contracts                        /alumni/api/v1/contracts                        GET, OPTIONS, HEAD   app_views.get_all_contracts
Retrieve a contract by ID                     /alumni/api/v1/contracts/<contract_id>          GET, OPTIONS, HEAD   app_views.get_contract_by_id
Create a new contract                         /alumni/api/v1/contracts                        OPTIONS, POST        app_views.create_contract
Update a contract by ID                       /alumni/api/v1/contracts/<contract_id>          PUT, OPTIONS         app_views.update_contract
Delete a contract by ID                       /alumni/api/v1/contracts/<contract_id>          OPTIONS, DELETE      app_views.delete_contract
Retrieve contract document                    /alumni/api/v1/contract_doc/<contract_id>       GET, OPTIONS, HEAD   app_views.get_contract_doc

Retrieve all beneficiaries                    /alumni/api/v1/beneficiaries                    GET, OPTIONS, HEAD   app_views.get_all_beneficiaries
Retrieve a beneficiary by ID                  /alumni/api/v1/beneficiaries/<beneficiary_id>   GET, OPTIONS, HEAD   app_views.get_beneficiary
Retrieve user's beneficiaries                 /alumni/api/v1/users/<user_id>/beneficiaries    GET, OPTIONS, HEAD   app_views.get_user_beneficiaries
Create a new beneficiary                      /alumni/api/v1/beneficiaries                    OPTIONS, POST        app_views.create_beneficiary
Update a beneficiary by ID                    /alumni/api/v1/beneficiaries/<beneficiary_id>   PUT, OPTIONS         app_views.update_beneficiary
Delete a beneficiary by ID                    /alumni/api/v1/beneficiaries/<beneficiary_id>   OPTIONS, DELETE      app_views.delete_beneficiary

Retrieve audit trails                         /alumni/api/v1/audit_trails                     GET, OPTIONS, HEAD   app_views.get_audit_trails
Retrieve user's invoices                      /alumni/api/v1/invoices/users_invoices/<user_id> GET, OPTIONS, HEAD   app_views.get_users_invoices
Retrieve all invoices                         /alumni/api/v1/invoices                         GET, OPTIONS, HEAD   app_views.get_all_invoices
Retrieve an invoice by ID                     /alumni/api/v1/invoices/<invoice_id>            GET, OPTIONS, HEAD   app_views.get_invoice
Create a new invoice                          /alumni/api/v1/invoices                         OPTIONS, POST        app_views.create_invoice
Update an invoice by ID                       /alumni/api/v1/invoices/<invoice_id>            PUT, OPTIONS         app_views.update_invoice
Delete an invoice by ID                       /alumni/api/v1/invoices/<invoice_id>            OPTIONS, DELETE      app_views.delete_invoice
Send an invoice                               /alumni/api/v1/send_invoice/<invoice_id>        OPTIONS, POST        app_views.send_invoice

Register a new user                           /alumni/api/v1/auth/register                    OPTIONS, POST        app_auth.register
User login                                    /alumni/api/v1/auth/login                       OPTIONS, POST        app_auth.login
Refresh access token                          /alumni/api/v1/auth/refresh_token               OPTIONS, POST        app_auth.refresh_access_token
User logout                                   /alumni/api/v1/auth/logout                      OPTIONS, POST        app_auth.logout
Recover password                              /alumni/api/v1/auth/recover                     OPTIONS, POST        app_auth.recover_password
Reset password                                /alumni/api/v1/auth/reset_password/<token>/<email> OPTIONS, POST        app_auth.reset_password



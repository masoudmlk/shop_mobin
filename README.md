# shop_mobin
In the project we have three main component which include **token-based authentication, store, and message or chat application**. 

## Token-based authentication
In the token-based authentication, we implement the basic action such as register, login, logout, change password for user. every user also can set profile info or can see his or her profile.
### Token-based Routes
- register user  /auth/register/
- login user  /auth/login/
- logout  /auth/logout/
- set profile information of user /auth/get-profile/
- get profile information auth/set-profile/
- change password  /auth/change-password/


## Store
In store, at first we have three level of permission which include anonymous user, register user, and admin.

The admin user only can make and edit products and other users can see list of product and a product.

Every register user can write opinions or score products. register users can add items to their cart and also remove items from their cart via product id and quantity of product after that they can finalize their product via shop action.
For tracking the previous purchase, user can use track list action and get track for show all products that user bought.

### Store routes
- ‫‪Product list /product/list/‬‬
- ‫‪Product /product/get/{product_id}/‬‬
‫‪
- add Opinion for product /opinion/add/{product_id}/‬‬
- ‫‪Opinions /opinion/list/{product_id}/‬‬
- ‫  ‪Add score for product /score/add/{product_id}/
- get average score of product ‫‪/score/get/{product_id}/‬‬
- ‫‪Add items to cart cart/add/‬‬
- ‬‬‫‪Remove items from cart /cart/remove/‬‬
- ‫‪purchase Products /shop/‬‬
- ‫show list of pervious user's purchase ‪/track/list/‬‬
-‫‪ show list of items and information of a purchase /track/get/{tack_id}/‬‬
## Chat
I use django channel for implement this part. In this section, users can make different groups and add memmbers to grous or remove members from groups.
Every message can seen all of members of group.
admin user can control the content of chat among people via filter swear words and put star(*) instead of them. Admin also can send message to group. In other words, Admin can set a message to send to groups via specfic their ids.

### Chat routes
- badword list
- get a badword
- remove a badword
- update a badword
- add a badword
- delete a badword
- get a list of groups base on creator
- get a group
- remove a group
- update a group
- delete a group
- add members to group
- remove members to group
- send a message to groups(admin)
- get list of groups(admin)
- send message

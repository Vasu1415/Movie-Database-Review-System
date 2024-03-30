from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
import base64
from io import BytesIO
import io
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm
from ..models import User
from ..movies.routes import movies

users = Blueprint("users", __name__)

def get_b64_img(username):
    user = User.objects(username=username).first()
    if user.profile_pic is None:
        return None
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

""" ************ User Management views ************ """


# TODO: implement
@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated: # if the user is already logged in then, all we need to do is return the main page. 
        return redirect(url_for('movies.index'))
    registration_user_form = RegistrationForm()
    if registration_user_form.validate_on_submit() and registration_user_form.validate():
        hashed = bcrypt.generate_password_hash(registration_user_form.password.data).decode('utf-8')
        user = User(username=registration_user_form.username.data, 
                    email=registration_user_form.email.data, password=hashed)
        user.save()
        return redirect(url_for('users.login'))

    return render_template('register.html', form=registration_user_form)


# TODO: implement
@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: # if the user is already logged in then, all we need to do is return the main page. 
        return redirect(url_for('movies.index'))
    login_user_form = LoginForm() # making a call to the LoginForm() so as to get details of the content inputted by the user
    if login_user_form.validate_on_submit():
        user = User.objects(username=login_user_form.username.data).first()
        if (user is not None and 
 bcrypt.check_password_hash(user.password, login_user_form.password.data)): # if the user exists but they entered the wrong password
                                                                            # then, we redirect them to the form and on successful
                                                                            # submission they go to the account page
            flash('Login failed. Check your username and/or password')
            login_user(user)
            return redirect(url_for('users.account'))
        elif user is None:
            flash('Login failed. Check your username and/or password')
            return redirect(url_for('users.login'))
    return render_template('login.html',form=login_user_form)


# TODO: implement
@users.route("/logout")
@login_required
def logout():
    logout_user() # logging out the user
    return redirect(url_for('movies.index')) # sending them to homepage.


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm() # making a call to the UpdateUsernameForm which will allow us to have access
                                                # to the most recent username.
    update_profile_pic_form = UpdateProfilePicForm() # making a call to the UpdateProfilePicForm will allow us to update our
                                                     # picture and potentially access the contents. 
    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            current_user.modify(username=update_username_form.username.data) # updating the username to the new username and saving the results in our
                                                        # database
            current_user.save()
            # this condition is essentially stating that if the user submitted the update_username_form and also the form 
            # submisssion is deemed to be valid then, we must do something. 

            # On running the sample we notice that the user is redirected to the login page. A given user has the following fields
            # associated with them: username, email, password, and profile picture.  

            # Since we have successfully validated the form and also submitted it we will simply be redirecting the user to the login
            # page now
            return redirect(url_for('users.login')) # url_for --> generates the link for the login page
                                                    # redirect() --> redirects them to the login page

        if update_profile_pic_form.submit_picture.data and update_profile_pic_form.validate(): # the second condition is the one
                                                                                               # which triggers the call to all 
                                                                                               # validate functions which are defined in
                                                                                               # the format: validate_<field_name>

            # this condition is essentially stating that if the user submitted the update_profile_pic_form and also the form 
            # submission is deemed to be valid then, we must do something. 

            # On running the sample we notice that the user is redirected to the account page.

            # After running the form we know we have some form of new picture with us. We want to make sure that we update the
            # database so that it shows the updated image. 

            # The update_profile_pic_form has two fields and the one with the image is called the picture field
            image = update_profile_pic_form.picture.data # Since we have validated the submission we can use '.data' to access the stored
                                                         # value. 
            filename = secure_filename(image.filename) 
            content_type = f'images/{filename[-3:]}'

            # The user may not necessarily be having a profile pic so we must not assume that the user already has some picture.
            if current_user.profile_pic is None: 
                current_user.profile_pic.put(image.stream, content_type=content_type) # adding a profile picture for that user
            else:
                current_user.profile_pic.replace(image.stream, content_type=content_type) # replacing the profile picture for the current user 
            current_user.save() # saving the new image in the user's database profile. 
            return redirect(url_for('users.account')) # redirecting the user back to the account page with the updated profile picture

    # if we are not making any form of updates then we just want our page to be displayed which includes the following:
        # image --> since the image is being displayed in base_64 we need to convert the image as well pass it in to the template
        # Welcome greeting for the user which makes of the username and need to display the form layout itself --> we must pass in the form 
        # Update Profile Picture form --> pass in the form from above
        # all reviews button that we need to perform linking for in the movie routes file. 
    return render_template('account.html',user = current_user, update_username_form=update_username_form, update_profile_pic_form=update_profile_pic_form, image=get_b64_img(current_user.username))

from config import app
from controller_functions import registration, signup, login, users, followers, follow, unfollow, dashboard, tweet, like_tweet, unlike_tweet, edit_tweet, update_tweet, delete_tweet, logout

app.add_url_rule('/registration', view_func=registration)
app.add_url_rule('/signup', view_func=signup, methods=['POST'])
app.add_url_rule('/login', view_func=login, methods=['POST'])
app.add_url_rule('/users', view_func=users)
app.add_url_rule('/followers', view_func=followers)
app.add_url_rule('/<followed_user>/follow', view_func=follow)
app.add_url_rule('/<followed_user>/unfollow', view_func=unfollow)
app.add_url_rule('/dashboard', view_func=dashboard)
app.add_url_rule('/tweet', view_func=tweet, methods=['POST'])
app.add_url_rule('/tweets/<tweet_id>/like', view_func=like_tweet)
app.add_url_rule('/tweets/<tweet_id>/unlike', view_func=unlike_tweet)
app.add_url_rule('/tweets/<tweet_id>/edit', view_func=edit_tweet)
app.add_url_rule('/tweets/<tweet_id>/update_tweet',
                 view_func=update_tweet, methods=['POST'])
app.add_url_rule('/tweets/<tweet_id>/delete', view_func=delete_tweet)
app.add_url_rule('/tweets/<tweet_id>/delete', view_func=logout)

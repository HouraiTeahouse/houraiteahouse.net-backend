from houraiteahouse.route.auth_route import auth
from houraiteahouse.route.news_route import news
from houraiteahouse.route.news_route import news
from houraiteahouse.route.errors import error

blueprints = {
    '/auth': auth,
    '/news': news,
    '': error
}

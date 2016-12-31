from .auth_route import auth
from .news_route import news

blueprints = {
    '/auth': auth,
    '/news': news
}
